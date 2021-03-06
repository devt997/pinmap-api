import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Pin, Tag

from pins.serializers import PinSerializer, PinDetailSerializer
import datetime
PINS_URL = reverse('pins:pin-list')


def image_upload_url(pin_id):
    """Return URL for pin image upload"""
    return reverse('pins:pin-upload-image', args=[pin_id])


def detail_url(pin_id):
    """Return pin detail URL"""
    return reverse('pins:pin-detail', args=[pin_id])


def sample_tag(user, name='Sample data'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_pin(user, **params):
    """Create and return a sample pin"""
    defaults = {
        'title': 'Sample pin',
        'date': datetime.date.today(),

    }
    defaults.update(params)

    return Pin.objects.create(user=user, **defaults)


class PublicPinApiTests(TestCase):
    """Test unauthenticated pin API access"""

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authenticaiton is required"""
        res = self.client.get(PINS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePinApiTests(TestCase):
    """Test authenticated pin API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'dev@dev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_pins(self):
        """Test retrieving list of pins"""
        sample_pin(user=self.user)
        sample_pin(user=self.user)

        res = self.client.get(PINS_URL)

        pins = Pin.objects.all().order_by('-id')
        serializer = PinSerializer(pins, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_pins_limited_to_user(self):
        """Test retrieving pins for user"""
        user2 = get_user_model().objects.create_user(
            'dev2@dev.com',
            'pass'
        )
        sample_pin(user=user2)
        sample_pin(user=self.user)

        res = self.client.get(PINS_URL)

        pins = Pin.objects.filter(user=self.user)
        serializer = PinSerializer(pins, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_pin_detail(self):
        """Test viewing a pin detail"""
        pin = sample_pin(user=self.user)
        pin.tags.add(sample_tag(user=self.user))
        url = detail_url(pin.id)
        res = self.client.get(url)

        serializer = PinDetailSerializer(pin)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_pin(self):
        """Test creating pin"""
        payload = {
            'title': 'Test pin',
            'date': datetime.date.today(),
        }
        res = self.client.post(PINS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        pin = Pin.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(pin, key))

    def test_create_pin_with_tags(self):
        """Test creating a pin with tags"""
        tag1 = sample_tag(user=self.user, name='Tag 1')
        tag2 = sample_tag(user=self.user, name='Tag 2')
        payload = {
            'title': 'Test pin with two tags',
            'tags': [tag1.id, tag2.id],
            'date': datetime.date.today(),
        }
        res = self.client.post(PINS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        pin = Pin.objects.get(id=res.data['id'])
        tags = pin.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_partial_update_pin(self):
        """Test updating a pin with patch"""
        pin = sample_pin(user=self.user)
        pin.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='test')

        payload = {'title': 'test event', 'tags': [new_tag.id]}
        url = detail_url(pin.id)
        self.client.patch(url, payload)

        pin.refresh_from_db()
        self.assertEqual(pin.title, payload['title'])
        tags = pin.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_pin(self):
        """Test updating a pin with put"""
        pin = sample_pin(user=self.user)
        pin.tags.add(sample_tag(user=self.user))

        payload = {
            'title': 'Test pin with two tags',
            'date': datetime.date.today(),
        }
        url = detail_url(pin.id)
        self.client.put(url, payload)

        pin.refresh_from_db()
        self.assertEqual(pin.title, payload['title'])
        self.assertEqual(pin.date, payload['date'])
        tags = pin.tags.all()
        self.assertEqual(len(tags), 0)


class PinImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user', 'testpass')
        self.client.force_authenticate(self.user)
        self.pin = sample_pin(user=self.user)

    def tearDown(self):
        self.pin.image.delete()

    def test_upload_image_to_pin(self):
        """Test uploading an image to pin"""
        url = image_upload_url(self.pin.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.pin.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.pin.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.pin.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_pins_by_tags(self):
        """Test returning pins with specific tags"""
        pin1 = sample_pin(user=self.user, title='Thai party',
                          date=datetime.date.today())
        pin2 = sample_pin(user=self.user, title='Event',
                          date=datetime.date.today())
        tag1 = sample_tag(user=self.user, name='Some tag1')
        tag2 = sample_tag(user=self.user, name='Some Tag2')
        pin1.tags.add(tag1)
        pin2.tags.add(tag2)
        pin3 = sample_pin(user=self.user, title='New Event')

        res = self.client.get(
            PINS_URL,
            {'tags': '{},{}'.format(tag1.id, tag2.id)}
        )

        serializer1 = PinSerializer(pin1)
        serializer2 = PinSerializer(pin2)
        serializer3 = PinSerializer(pin3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

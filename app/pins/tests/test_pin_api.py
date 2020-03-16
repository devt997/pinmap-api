from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Pin

from pins.serializers import PinSerializer
import datetime
PINS_URL = reverse('pins:pin-list')



def sample_pin(user, **params):
    """Create and return a sample pin"""
    defaults = {
        'title': 'Sample pin',
        'date': datetime.datetime.now(),

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


from rest_framework import serializers

from core.models import Tag
from core.models import Tag, Pin

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id',)

class PinSerializer(serializers.ModelSerializer):
    """Serialize a pin"""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Pin
        fields = (
            'id', 'title', 'tags', 'date',
            'link',
        )
        read_only_fields = ('id',)

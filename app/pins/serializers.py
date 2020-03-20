
from rest_framework import serializers


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


class PinDetailSerializer(PinSerializer):
    """Serialze a pin detail"""
    tags = TagSerializer(many=True, read_only=True)


class PinImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to pin"""

    class Meta:
        model = Pin
        fields = ('id', 'image')
        read_only_fields = ('id',)

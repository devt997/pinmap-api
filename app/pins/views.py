from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag,  Pin


from pins import serializers


class BasePinAttrViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin):
    """Base viewset for user owned pins attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for current user"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(pin__isnull=False)
        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """Create a new ingredient"""
        serializer.save(user=self.request.user)


class TagViewSet(BasePinAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class PinViewSet(viewsets.ModelViewSet):
    """Manage pins in the database"""
    serializer_class = serializers.PinSerializer
    queryset = Pin.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the pins for the authenticated user"""
        tags = self.request.query_params.get('tags')

        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.PinDetailSerializer
        elif self.action == 'upload_image':
            return serializers.PinImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new pin"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a pin"""
        pin = self.get_object()
        serializer = self.get_serializer(
            pin,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

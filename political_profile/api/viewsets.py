from rest_framework import viewsets

from political_profile.api import serializers
from political_profile.core import models


class CongressmanViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CongressmanSerializer
    queryset = models.Congressman.objects.all()


class PropositionViewset(viewsets.ModelViewSet):
    serializer_class = serializers.PropositionSerializer
    queryset = models.Proposition.objects.all()


class DiscourseViewset(viewsets.ModelViewSet):
    serializer_class = serializers.DiscourseSerializer
    queryset = models.Discourse.objects.all()

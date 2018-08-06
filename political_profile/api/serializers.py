from django.db.models import Field
from rest_framework import serializers

from political_profile.core.models import Congressman, Proposition, Discourse


def _get_base_fields(model_class, *args):
    fields = model_class._meta.get_fields()
    return [f.get_attname() for f in fields if issubclass(type(f), Field)] + list(args)


class CongressmanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Congressman
        fields = _get_base_fields(Congressman)


class PropositionSerializer(serializers.ModelSerializer):
    congressmen = CongressmanSerializer(many=True)

    class Meta:
        model = Proposition
        fields = _get_base_fields(Proposition)


class DiscourseSerializer(serializers.ModelSerializer):
    congressman = CongressmanSerializer()

    class Meta:
        model = Discourse
        fields = _get_base_fields(Discourse, 'congressman')

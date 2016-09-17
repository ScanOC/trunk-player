from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Transmission, TalkGroup, Unit, ScanList


class TalkGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TalkGroup
        fields = ('url', 'dec_id', 'alpha_tag', 'description', 'slug')

class UnitListField(serializers.RelatedField):

    def to_representation(self, value):
        return { "pk": value.pk, "dec_id": value.dec_id, "description": value.description }

class TransmissionSerializer(serializers.ModelSerializer):
    talkgroup_info = TalkGroupSerializer()
    audio_file = serializers.StringRelatedField()
    units = UnitListField(many=True, read_only=True)

    class Meta:
        model = Transmission
        fields = ('pk', 'url', 'start_datetime', 'local_start_datetime', 'audio_file', 'talkgroup', 'talkgroup_info', 'freq', 'emergency', 'units', 'play_length', 'print_play_length', 'slug', 'freq_mhz')

class ScanListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ScanList
        fields = ('pk', 'name', 'description')

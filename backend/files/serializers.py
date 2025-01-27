import secrets
from rest_framework import serializers
from .models import File, SharedFile

class FileSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = File
        fields = '__all__'

    def create(self, validated_data):
        file = validated_data.get('file')
        validated_data['filename'] = file.name
        validated_data['size'] = file.size
        validated_data['mime'] = file.content_type

        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['type'] = representation.pop('mime').split('/')[1]
        representation['owner'] = instance.owner.username
        return representation
    
class ShareFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedFile
        fields = ['file', 'user', 'permission']

    def create(self, validated_data):
        share_hash = secrets.token_urlsafe(32)
        validated_data['share_hash'] = share_hash
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        share_link = f'http://localhost:8000/files/download/?hash={instance.share_hash}'
        representation['link'] = share_link
        return representation
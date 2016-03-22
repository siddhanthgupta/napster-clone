from rest_framework import serializers
from napster.models import User, File, UserFileMap


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'ip_address', 'port')


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ('filename', 'filehash')


class UserFileMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFileMap
        fields = ('user', 'file')

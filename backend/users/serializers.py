from rest_framework import serializers
from .models import User
from .role import UserRole

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(choices=[(role, role) for role in UserRole.CHOICES], required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'mfa_enabled', 'role']
        read_only_fields = ['id', 'mfa_enabled']

    def validate(self, data):
        # Validate role value
        role = data.get('role')
        if role not in dict(UserRole.CHOICES):
            raise serializers.ValidationError({"role": "Invalid role value"})

        return data

    def create(self, validated_data):
        # Create the user using the custom manager
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )

        return user

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        sensitive_fields = ['password']
        for field in sensitive_fields:
            ret.pop(field, None)
        ret['isMFAEnabled'] = ret.pop('mfa_enabled', False)
        return ret
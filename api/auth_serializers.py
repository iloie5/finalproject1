from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    recovery_question = serializers.CharField(max_length=200, required=True)
    recovery_answer = serializers.CharField(max_length=200, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 
                 'recovery_question', 'recovery_answer', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    recovery_answer = serializers.CharField(max_length=200)

    def validate(self, attrs):
        email = attrs.get('email')
        recovery_answer = attrs.get('recovery_answer')
        
        try:
            user = User.objects.get(email=email)
            if not user.recovery_answer or user.recovery_answer.lower() != recovery_answer.lower():
                raise serializers.ValidationError("Invalid recovery answer.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        attrs['user'] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    recovery_answer = serializers.CharField(max_length=200)
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        try:
            user = User.objects.get(email=attrs['email'])
            if not user.recovery_answer or user.recovery_answer.lower() != attrs['recovery_answer'].lower():
                raise serializers.ValidationError("Invalid recovery answer.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)


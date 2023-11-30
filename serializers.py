from rest_framework import serializers


class URLSerializer(serializers.Serializer):
    url = serializers.CharField(max_length=200)


class GPTSerializer(serializers.Serializer):
    my_profile_data = serializers.CharField()
    other_profile_data = serializers.CharField()
    session_id = serializers.CharField()


class SignUpSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=20)
    last_name = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=20)


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(max_length=40)


class SetNewPasswordSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(max_length=40)
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(max_length=20)

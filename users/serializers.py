# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    # Add password2 field for confirmation (not part of the model)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        # Include fields the user submits, plus password1/2 for creation
        fields = ('username', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        # Check that the two passwords match
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Passwords must match."})
        return data

    def create(self, validated_data):
        # Remove the extra password2 field before creating the user
        validated_data.pop('password2')
        
        # Create the user using Django's recommended method for password hashing
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        # Add user_id to the token payload
        token['user_id'] = user.id
        

        return token
    def validate(self, attrs):
            data = super().validate(attrs)
    
            user = self.user
            data["user_id"] = user.id
          
            return data
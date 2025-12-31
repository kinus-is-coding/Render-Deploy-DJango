# users/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
class UserRegistrationView(generics.CreateAPIView):
    # Anyone can hit this endpoint
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # If validation succeeds, save the new user
            serializer.save()
            return Response(
                {"detail": "User registered successfully. Please log in."},
                status=status.HTTP_201_CREATED
            )
        
        # If validation fails, return errors (e.g., password mismatch)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

# Create your views here.
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    response_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }
    return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    data = request.data
    username = data.get("username")
    password = data.get("password")
    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response(
            {"detail": "Invalid credentials"},
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key},
            status=status.HTTP_200_OK
        )

@api_view(["GET"])
def user_me(request):
    user = request.user
    response_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }

    return Response(response_data, status=status.HTTP_200_OK)
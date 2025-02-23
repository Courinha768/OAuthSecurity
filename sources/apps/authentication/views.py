import logging
import secrets
import string
import uuid

from django.contrib.auth import authenticate
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = [AllowAny]

	def get_serializer_class(self):
		if self.action in ['register']:
			return UserRegistrationSerializer
		return UserSerializer

	@action(detail=True, methods=['post'], url_path='login')
	def login(self, request):
		serializer = self.get_serializer_class()
		serializer.is_valid(raise_exception=True)

		user_id = serializer.data.get('user_id')
		user_secret = serializer.data.get('user_secret')

		user = authenticate(request, user_id=user_id, user_secret=user_secret)
		if user is not None:
			refresh = RefreshToken.for_user(user)
			user_data = UserSerializer(user).data

			return Response({
				'access_token': str(refresh.access_token),
				'refresh_token': str(refresh),
				'user_id': user_data.get('user_id'),
				'scopes': user_data.get('scopes')
			}, status=status.HTTP_200_OK)
		return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


	@action(detail=False, methods=['post'], url_path='register')
	def register(self, request):

		serializer = self.get_serializer_class()(data=request.data)
		serializer.is_valid(raise_exception=True)

		user = serializer.save()
		refresh = RefreshToken.for_user(user)
		user_data = UserSerializer(user).data

		return Response({
			'user_id': user_data.get('user_id'),
			'user_secret': user_data.get('user_secret'),
			'refresh': str(refresh),
			'access': str(refresh.access_token),
		}, status=status.HTTP_201_CREATED)

	@action(detail=False, methods=['post'], url_path='check-token')
	def check_token(self, request):
		token = request.data.get('access_token')
		if not token:
			return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			refresh = RefreshToken(token)
			user = User.objects.get(id=refresh.get('user_id'))
			user_data = UserSerializer(user).data

			return Response({
				'valid': True,
				'access_token': str(refresh.access_token),
				'refresh_token': str(refresh),
				'user_id': user_data.get('user_id'),
				'scopes': user_data.get('scopes')
			}, status=status.HTTP_200_OK)
		except TokenError:
			return Response({
				'valid': False,
				'message': 'Invalid token'
			}, status=status.HTTP_401_UNAUTHORIZED)

	@action(detail=False, methods=['post'], url_path='refresh-token')
	def refresh_token(self, request):
		refresh_token = request.data.get('refresh_token')
		if not refresh_token:
			return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			refresh = RefreshToken(refresh_token)
			user = User.objects.get(id=refresh['user_id'])
			user_data = UserSerializer(user).data
			new_refresh = RefreshToken.for_user(user)

			return Response({
				'access_token': str(new_refresh.access_token),
				'refresh_token': str(new_refresh),
				'user_id': user_data.get('user_id'),
				'scopes': user_data.get('scopes')
			}, status=status.HTTP_200_OK)
		except TokenError as e:
			return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

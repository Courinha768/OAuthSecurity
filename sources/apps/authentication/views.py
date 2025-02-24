import logging
import os

from django.contrib.auth import authenticate
from django.core.cache import cache, InvalidCacheBackendError
from rest_framework import viewsets, status
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

	@action(detail=False, methods=['post'], url_path='login')
	def login(self, request):
		logger.info(f"Login attempt for user: {request.data.get('user_id')}")
		user_id = request.data.get('user_id')
		user_secret = request.data.get('user_secret')

		login_attempts_key = None
		attempts = None
		try:
			login_attempts_key = f"login_attempts:{user_id}"
			attempts = cache.get(login_attempts_key) or 0

			if attempts >= os.environ.get('RATE_LIMIT', 1000):
				return Response({'error': 'Too many failed attempts. Try again later.'},
								status=status.HTTP_429_TOO_MANY_REQUESTS)
		except (InvalidCacheBackendError, ConnectionError):
			logger.warning("Redis cache is unavailable. Falling back to database.")


		user = authenticate(request, user_id=user_id, user_secret=user_secret)
		logger.info(f"User: {user}")

		if user:
			logger.info(f"Successful login for user: {user_id}")
			refresh = RefreshToken.for_user(user)
			return Response({
				'access_token': str(refresh.access_token),
				'refresh_token': str(refresh),
				'user_id': user.user_id,
				'scopes': user.scopes
			}, status=status.HTTP_200_OK)

		try:
			cache.set(login_attempts_key, attempts + 1, timeout=300)
		except (InvalidCacheBackendError, ConnectionError):
			logger.warning("Redis cache is unavailable. Skipping caching.")

		logger.warning(f"Failed login attempt for user: {user_id}")
		return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

	@action(detail=False, methods=['post'], url_path='register')
	def register(self, request):

		serializer = self.get_serializer_class()(data=request.data)
		serializer.is_valid(raise_exception=True)

		response = serializer.create(serializer.validated_data)

		return Response(response, status=status.HTTP_201_CREATED)

	@action(detail=False, methods=['post'], url_path='check-token')
	def check_token(self, request):
		token = request.data.get('access_token')
		if not token:
			return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

		cached_user = None
		try:
			cached_user = cache.get(f"token:{token}")
		except (InvalidCacheBackendError, ConnectionError):
			logger.warning("Redis cache is unavailable. Falling back to database.")

		if cached_user:
			return Response(cached_user, status=status.HTTP_200_OK)

		try:
			refresh = RefreshToken(token)
			user = User.objects.get(user_id=refresh.get('user_id'))

			user_data =	{
				'valid': True,
				'access_token': str(refresh.access_token),
				'refresh_token': str(refresh),
				'user_id': user.user_id,
				'scopes': user.scopes
			}

			cache.set(f"token:{token}", user_data, timeout=900)
			return Response(user_data, status=status.HTTP_200_OK)
		except (TokenError, User.DoesNotExist):
			return Response({'valid': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
		except (InvalidCacheBackendError, ConnectionError):
			logger.warning("Redis cache is unavailable. Skipping caching.")

	@action(detail=False, methods=['post'], url_path='refresh-token')
	def refresh_token(self, request):
		refresh_token = request.data.get('refresh_token')
		if not refresh_token:
			return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

		if cache.get(f"blacklist:{refresh_token}"):
			return Response({'error': 'Token has been revoked'}, status=status.HTTP_401_UNAUTHORIZED)

		try:
			refresh = RefreshToken(refresh_token)
			user = User.objects.get(id=refresh['user_id'])
			new_refresh = RefreshToken.for_user(user)

			cache.set(f"blacklist:{refresh_token}", "revoked", timeout=604800)

			return Response({
				'access_token': str(new_refresh.access_token),
				'refresh_token': str(new_refresh),
				'user_id': user.user_id,
				'scopes': user.scopes
			}, status=status.HTTP_200_OK)
		except TokenError:
			return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
		except (InvalidCacheBackendError, ConnectionError):
			logger.warning("Redis cache is unavailable. Skipping caching.")

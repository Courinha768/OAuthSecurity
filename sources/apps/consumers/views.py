import logging
import os

from django.contrib.auth import authenticate
from django.core.cache import cache, InvalidCacheBackendError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .authentication import validate_token
from .models import Consumer
from .serializers import ConsumerSerializer, ConsumerRegistrationSerializer
from .permissions import AllowAny, IsAuthenticated, IsStaff

logger = logging.getLogger(__name__)

class ConsumerViewSet(viewsets.ViewSet):
	queryset = Consumer.objects.all()
	serializer_class = ConsumerSerializer
	permission_classes = [AllowAny]

	def get_serializer_class(self):
		if self.action in ['register']:
			return ConsumerRegistrationSerializer
		return ConsumerSerializer

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
		logger.info(f"Consumer: {user}")

		if user:
			logger.info(f"Successful login for user: {user_id}")
			refresh = RefreshToken.for_user(user)
			return Response({
				'access_token': str(refresh.access_token),
				'refresh_token': str(refresh),
				'user': ConsumerSerializer(user).data,
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
		scope = request.data.get('scope')
		if not token:
			return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

		user_data = validate_token(token)

		if not user_data or (scope and user_data[0] and scope not in user_data[0].get('scopes')):
			return Response({'valid': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
		return Response({'valid': True, 'user': user_data}, status=status.HTTP_200_OK)

	@action(detail=False, methods=['post'], url_path='refresh-token')
	def refresh_token(self, request):
		refresh_token = request.data.get('refresh_token')
		if not refresh_token:
			return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

		if cache.get(f"blacklist:{refresh_token}"):
			return Response({'error': 'Token has been revoked'}, status=status.HTTP_401_UNAUTHORIZED)

		try:
			refresh = RefreshToken(refresh_token)
			user = Consumer.objects.get(id=refresh['user_id'])
			new_refresh = RefreshToken.for_user(user)

			cache.set(f"blacklist:{refresh_token}", "revoked", timeout=604800)

			return Response({
				'access_token': str(new_refresh.access_token),
				'refresh_token': str(new_refresh),
				'user': ConsumerSerializer(user).data,
			}, status=status.HTTP_200_OK)
		except TokenError:
			return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
		except (InvalidCacheBackendError, ConnectionError):
			logger.warning("Redis cache is unavailable. Skipping caching.")

class ManageViewSet(viewsets.ModelViewSet):
	queryset = Consumer.objects.all()
	serializer_class = ConsumerSerializer
	permission_classes = [IsStaff]

	@action(detail=False, methods=['post'], url_path='scopes')
	def manage_scopes(self, request):
		user_id             : str = request.data.get('user_id')
		scopes_to_add		: list = request.data.get('add')
		scopes_to_remove	: list = request.data.get('remove')

		try:
			user = Consumer.objects.get(user_id=user_id)
		except Consumer.DoesNotExist:
			return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

		if scopes_to_add:
			for scope in scopes_to_add:
				user.add_scope(scope)
		if scopes_to_remove:
			for scope in scopes_to_remove:
				user.remove_scope(scope)
		return Response({'user': ConsumerSerializer(user).data}, status=status.HTTP_200_OK)

	@action(detail=False, methods=['post'], url_path='admin')
	def manage_scopes(self, request):
		user_id: str = request.data.get('user_id')
		admin : bool = request.data.get('admin')

		try:
			user = Consumer.objects.get(user_id=user_id)
		except Consumer.DoesNotExist:
			return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

		user.set_admin(admin)
		return Response({'user': ConsumerSerializer(user).data}, status=status.HTTP_200_OK)


import logging

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.core.cache import InvalidCacheBackendError, cache
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .models import Consumer
from .serializers import ConsumerSerializer

logger = logging.getLogger(__name__)

class ConsumerSecretAuthBackend(BaseBackend):
	def authenticate(self, request, user_id=None, user_secret=None):
		try:
			user = Consumer.objects.get(user_id=user_id)
			if check_password(user_secret, user.user_secret):
				return user
			else:
				logger.warning("Password check failed")
		except Consumer.DoesNotExist:
			logger.warning("Consumer not found")

		return None

def validate_token(token):
	try:
		cached_user = cache.get(f"token:{token}")
		if cached_user:
			return cached_user
	except (InvalidCacheBackendError, ConnectionError):
		logger.warning("Redis cache is unavailable. Falling back to database.")

	try:
		refresh = AccessToken(token)
		user = Consumer.objects.get(id=refresh.get('user_id'))

		user_data = ConsumerSerializer(user).data,

		cache.set(f"token:{token}", user_data, timeout=900)
		return user_data
	except (TokenError, Consumer.DoesNotExist):
		logger.warning('Wrong token')
		return None
	except (InvalidCacheBackendError, ConnectionError):
		logger.warning("Redis cache is unavailable. Skipping caching.")
		return None

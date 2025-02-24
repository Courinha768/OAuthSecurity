import logging

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password

from .models import User

logger = logging.getLogger(__name__)

class UserSecretAuthBackend(BaseBackend):
	def authenticate(self, request, user_id=None, user_secret=None):
		try:
			user = User.objects.get(user_id=user_id)
			if check_password(user_secret, user.user_secret):
				return user
			else:
				logger.warning("Password check failed")
		except User.DoesNotExist:
			logger.warning("User not found")

		return None

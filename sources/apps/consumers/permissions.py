import logging

from rest_framework.permissions import BasePermission

from .authentication import validate_token

logger = logging.getLogger(__name__)

class AllowAny(BasePermission):
	"""
    Allow any access.
    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the intention
    more explicit.
    """

	def has_permission(self, request, view):
		return True


class IsAuthenticated(BasePermission):
	def has_permission(self, request, view):
		auth_header = request.META.get('HTTP_AUTHORIZATION')
		if auth_header is not None:
			try:
				auth_type, token = auth_header.split(' ')
				if auth_type.lower() == 'bearer':
					user_data = validate_token(token)
					if user_data:
						return True
			except ValueError:
				return False

		return False


class IsStaff(BasePermission):
	def has_permission(self, request, view):
		auth_header = request.META.get('HTTP_AUTHORIZATION')
		if auth_header is not None:
			try:
				auth_type, token = auth_header.split(' ')
				if auth_type.lower() == 'bearer':
					user_data = validate_token(token)
					if user_data and user_data[0] and user_data[0].get('is_staff'):
						return True
			except ValueError:
				return False

		return False

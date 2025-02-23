import secrets
import string
import uuid

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('user_id', 'user_secret', 'scopes', 'date_joined', 'last_login')

def generate_user_id():
	return str(uuid.uuid4())

def generate_user_secret(length=16):
	characters = string.ascii_letters + string.digits
	return ''.join(secrets.choice(characters) for _ in range(length))

class UserRegistrationSerializer(serializers.Serializer):
	class Meta:
		model = User
		fields = ('user_id', 'user_secret')
		extra_kwargs = {'user_secret': {'write_only': True}}

	def create(self, validated_data) -> User:

		user_id = generate_user_id()
		user_secret = generate_user_secret()

		user = User.objects.create(
			user_id=user_id,
			user_secret=user_secret
		)

		return user

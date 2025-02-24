import secrets
import string
import uuid

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('user_id', 'scopes', 'date_joined', 'last_login')

def generate_user_id():
	return str(uuid.uuid4())

def generate_user_secret(length=32):
	raw_secret = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
	return raw_secret

class UserRegistrationSerializer(serializers.Serializer):
	class Meta:
		model = User
		fields = ('user_id', 'user_secret')
		extra_kwargs = {'user_secret': {'write_only': True}}

	def create(self, validated_data):

		user_id = generate_user_id()
		raw_secret = generate_user_secret()

		user = User.objects.create_user(
			user_id=user_id,
			user_secret=raw_secret,
		)

		return {
			'user_id': user.user_id,
			'user_secret': raw_secret,
		}

import secrets
import string
import uuid

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Consumer

class ConsumerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Consumer
		fields = ('user_id', 'scopes', 'date_joined', 'last_login', 'is_staff')

def generate_user_id():
	return str(uuid.uuid4())

def generate_user_secret(length=32):
	raw_secret = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
	return raw_secret

class ConsumerRegistrationSerializer(serializers.Serializer):
	class Meta:
		model = Consumer
		fields = ('user_id', 'user_secret', 'scopes', 'name', 'description', 'date_joined', 'last_login')
		extra_kwargs = {'user_secret': {'write_only': True}}

	def create(self, validated_data):

		user_id = generate_user_id()
		raw_secret = generate_user_secret()

		user = Consumer.objects.create_user(
			user_id=user_id,
			user_secret=raw_secret,
		)

		return {
			'user_id': user.user_id,
			'user_secret': raw_secret,
		}

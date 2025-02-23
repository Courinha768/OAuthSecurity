from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group, Permission
from django.db import models
from django.contrib.postgres.fields import ArrayField

class User(AbstractBaseUser, PermissionsMixin):
	user_id = models.CharField(max_length=255, unique=True)
	user_secret = models.CharField(max_length=255)
	scopes = ArrayField(models.CharField(max_length=255), null=True, blank=True)

	date_joined = models.DateTimeField(auto_now_add=True)
	last_login = models.DateTimeField(auto_now=True)

	groups = models.ManyToManyField(
		Group,
		related_name='custom_user_set',  # Avoids clash with the default User model
		blank=True
	)

	user_permissions = models.ManyToManyField(
		Permission,
		related_name='custom_user_permissions_set',  # Avoids clash with the default User model
		blank=True
	)

	class Meta:
		verbose_name = 'user'
		verbose_name_plural = 'users'

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin, Group, Permission
from django.db import models
from django.contrib.postgres.fields import ArrayField

class ConsumerManager(BaseUserManager):
	def create_user(self, user_id, user_secret):
		user = self.model(user_id=user_id, user_secret=make_password(user_secret))
		user.save(using=self._db)
		return user

class Consumer(AbstractBaseUser, PermissionsMixin):
	user_id = models.CharField(max_length=255, unique=True)
	user_secret = models.CharField(max_length=255)
	scopes = models.TextField(default="", blank=True)

	date_joined = models.DateTimeField(auto_now_add=True)
	last_login = models.DateTimeField(auto_now=True)

	is_staff = models.BooleanField(default=False)

	objects = ConsumerManager()

	USERNAME_FIELD = 'user_id'
	REQUIRED_FIELDS = []

	groups = models.ManyToManyField(
		Group,
		related_name='custom_user_set',
		blank=True
	)

	user_permissions = models.ManyToManyField(
		Permission,
		related_name='custom_user_permissions_set',
		blank=True
	)

	class Meta:
		verbose_name = 'user'
		verbose_name_plural = 'users'

	def __str__(self):
		return self.user_id

	def add_scope(self, new_scope):
		if not self.scopes:
			self.scopes = new_scope
		else:
			scope_list = self.scopes.split(" ")
			if new_scope not in scope_list:
				scope_list.append(new_scope)
				self.scopes = " ".join(scope_list)
		self.save()

	def remove_scope(self, new_scope):

		scope_list = self.scopes.split(" ")
		if new_scope in scope_list:
			scope_list.remove(new_scope)
			self.scopes = " ".join(scope_list)
		self.save()

	def set_admin(self, value : bool):

		self.is_staff = value
		self.save()

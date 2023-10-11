from collections.abc import MutableMapping
from PIL import Image
from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone

from .AccountModel import Account


class UserManager(BaseUserManager):

    def get_or_create(self, defaults: MutableMapping[str, Any] | None = None, **kwargs: dict) -> tuple[Any, bool]:
        user, created = super().get_or_create(defaults, **kwargs)
        
        if created: 
            user.account = Account.objects.create_account()
            user.created_at = timezone.now()
            user.account.activate()
            user.save()
        
        return user, created

    def create_user_with_password(self, username, password):
        user = self.model(
            username = username,
            created_at = timezone.now(),
            is_staff = 0,
            is_superuser = 0,
            is_active = 0
        )

        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self, username, password):
        user = self.create_user_with_password(
            username = username,
            password = password
        )

        user.is_superuser = 1
        user.is_staff = 1
        user.is_active = 1
        user.save(using = self._db)
        return user
    
    def reset_username(self, user_id, username):
        user = self.get_user_from_id(user_id)
        user.username = username
        user.save()
        return user

    
    
    
    
class User(AbstractBaseUser):
    password = models.CharField(max_length = 128, null = True)
    username = models.CharField(max_length = 120, unique = True)
    last_login = models.DateTimeField(blank = True, null = True)
    created_at = models.DateTimeField(blank = True, null = True)
    is_superuser = models.IntegerField(blank = True, null = True)
    is_active = models.IntegerField(blank = True, null = True)
    is_staff = models.IntegerField(blank = True, null = True)

    thumbnail = models.ImageField(upload_to = 'profile_image', blank = True, null = True)

    account = models.ForeignKey(Account, on_delete = models.CASCADE, related_name='user', blank = True, null = True)


    email = models.CharField(max_length = 120, blank = True, null = True)


    # profile_image = models.ImageField(storage = settings.s3_storage, upload_to = 'profile_image', blank = True, null = True, default='profile_image/default.png')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    def has_perm(self, perm, obj = None):
        return True
    
    def has_module_perms(self, app_label):
        return True
    
    def upload_thumbnail(self, thumbnail: Image.Image):
        self.thumbnail = thumbnail
        self.save()
        return

    class Meta:
        db_table = 'auth_user'

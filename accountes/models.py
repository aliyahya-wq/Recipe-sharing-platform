from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteUserManager(UserManager, SoftDeleteManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)


class User(AbstractUser, SoftDeleteMixin):
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    facebook_link = models.URLField(blank=True)
    instagram_link = models.URLField(blank=True)
    twitter_link = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    objects = SoftDeleteUserManager()
    all_objects = UserManager()


class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create_recipe', 'Create Recipe'),
        ('update_recipe', 'Update Recipe'),
        ('delete_recipe', 'Delete Recipe'),
        ('comment', 'Comment'),
        ('rating', 'Rating'),
        ('favorite', 'Favorite'),
        ('like', 'Like'),
        ('follow', 'Follow'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} {self.action} at {self.timestamp}"


class Visit(models.Model):
    ip_address = models.GenericIPAddressField()
    country = models.CharField(max_length=100, default='Unknown')
    country_code = models.CharField(max_length=5, default='UN')
    path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Visit {self.path} from {self.ip_address}"

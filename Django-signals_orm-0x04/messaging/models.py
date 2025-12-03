from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid


class Role(models.TextChoices):
    """Role choices for users"""
    GUEST = 'guest', 'Guest'
    HOST = 'host', 'Host'
    ADMIN = 'admin', 'Admin'


class User(AbstractUser):
    """
    Custom User model extending AbstractUser.
    Includes additional fields: phone_number and role.
    Uses UUID as primary key.
    
    Inherited fields from AbstractUser/AbstractBaseUser:
    - password: CharField (max_length=128) - password hash stored automatically by Django
    - username: CharField (overridden to be optional)
    - email: EmailField (overridden to be required and unique)
    - first_name, last_name: CharField (overridden to be required)
    """
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    first_name = models.CharField(max_length=150, null=False, blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False, db_index=True)
    # password field is inherited from AbstractBaseUser (via AbstractUser)
    # It's a CharField(max_length=128) that stores the password hash
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        null=False,
        blank=False,
        default=Role.GUEST
    )
    created_at = models.DateTimeField(auto_now_add=True)


    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_id']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email'),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"



class Message(models.Model):
  message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  sender = models.ForeignKey(User, on_delete=models.CASCADE)
  receiver = models.ForeignKey(User, on_delete=models.CASCADE)
  content = models.TextField()
  timestamp = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
  notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  message = models.ForeignKey(Message, on_delete=models.CASCADE)
  timestamp = models.DateTimeField(auto_now_add=True)
  is_read = models.BooleanField(default=False)

  class Meta:
    db_table = 'notification'
    indexes = [
      models.Index(fields=['notification_id']),
      models.Index(fields=['user'])
    ]
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


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


class Conversation(models.Model):
    """
    Conversation model to track which users are involved in a conversation.
    Uses ManyToMany relationship for participants to support multiple users.
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversation'
        indexes = [
            models.Index(fields=['conversation_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        participant_names = ', '.join([user.email for user in self.participants.all()[:3]])
        return f"Conversation {self.conversation_id} - {participant_names}"


class Message(models.Model):
    """
    Message model containing sender and conversation references.
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        db_column='sender_id',
        db_index=True
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        db_column='conversation_id',
        db_index=True,
        null=True,  # Temporarily nullable for migration
        blank=True
    )
    message_body = models.TextField(null=False, blank=False)
    sent_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'message'
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
            models.Index(fields=['sent_at']),
        ]
        ordering = ['-sent_at']

    def __str__(self):
        return f"Message from {self.sender.email} at {self.sent_at}"

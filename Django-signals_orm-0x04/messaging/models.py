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

    # Override groups and user_permissions to add related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='messaging_user_set',
        related_query_name='messaging_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='messaging_user_set',
        related_query_name='messaging_user',
    )

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
  sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
  receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
  content = models.TextField()
  edited = models.BooleanField(default=False)
  timestamp = models.DateTimeField(auto_now_add=True)
  parent_message = models.ForeignKey(
      'self',
      on_delete=models.CASCADE,
      null=True,
      blank=True,
      related_name='replies'
  )

  class Meta:
    db_table = 'message'
    indexes = [
      models.Index(fields=['message_id']),
      models.Index(fields=['sender']),
      models.Index(fields=['receiver']),
      models.Index(fields=['timestamp']),
      models.Index(fields=['parent_message']),
    ]

  @classmethod
  def get_threaded_messages(cls, parent_id=None):
    """Get messages with optimized queries using select_related and prefetch_related."""
    queryset = cls.objects.select_related(
        'sender',
        'receiver',
        'parent_message',
        'parent_message__sender',
        'parent_message__receiver'
    ).prefetch_related(
        'replies__sender',
        'replies__receiver',
        'replies__replies'
    )
    
    if parent_id is None:
      # Get top-level messages (no parent)
      return queryset.filter(parent_message__isnull=True).order_by('timestamp')
    else:
      # Get replies to a specific message
      return queryset.filter(parent_message_id=parent_id).order_by('timestamp')

  def get_all_replies(self, depth=0, max_depth=10):
    """Recursively get all replies to this message."""
    if depth > max_depth:
      return []
    
    replies = list(
        Message.objects.select_related('sender', 'receiver')
        .filter(parent_message=self)
        .order_by('timestamp')
    )
    
    result = []
    for reply in replies:
      reply_data = {
        'message': reply,
        'replies': reply.get_all_replies(depth=depth + 1, max_depth=max_depth)
      }
      result.append(reply_data)
    
    return result

  def __str__(self):
    return f"Message from {self.sender.email} to {self.receiver.email}"


class MessageHistory(models.Model):
  """Model to store edit history of messages."""
  history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
  old_content = models.TextField()
  edited_at = models.DateTimeField(auto_now_add=True)
  edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='message_edits')

  class Meta:
    db_table = 'message_history'
    indexes = [
      models.Index(fields=['history_id']),
      models.Index(fields=['message']),
      models.Index(fields=['edited_at']),
    ]
    ordering = ['-edited_at']

  def __str__(self):
    return f"History for message {self.message.message_id} at {self.edited_at}"


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

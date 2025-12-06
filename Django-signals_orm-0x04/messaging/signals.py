from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Message, Notification, MessageHistory, User


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """Log old content before message is updated."""
    if instance.pk:  # Only for existing messages (updates, not creates)
        try:
            old_message = Message.objects.get(pk=instance.pk)
            # Check if content has changed
            if old_message.content != instance.content:
                # Save old content to history
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender
                )
                # Mark message as edited
                instance.edited = True
        except Message.DoesNotExist:
            pass


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """Create notification when a new message is created."""
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)


@receiver(pre_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """Clean up all user-related data when a user is deleted."""
    # Delete MessageHistory entries where user is edited_by
    # (These won't be deleted automatically because edited_by uses SET_NULL)
    MessageHistory.objects.filter(edited_by=instance).delete()
    
    # Messages where user is sender or receiver will be deleted via CASCADE
    # When messages are deleted, their MessageHistory entries are also deleted via CASCADE
    
    # Notifications where user is the recipient will be deleted via CASCADE
    # All related data is properly cleaned up respecting foreign key constraints


from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import Message, Notification, MessageHistory


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


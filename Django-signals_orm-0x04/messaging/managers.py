from django.db import models


class UnreadMessagesManager(models.Manager):
    """Custom manager for filtering unread messages."""
    
    def unread_for_user(self, user):
        """Get unread messages for a specific user."""
        return self.filter(
            receiver=user,
            read=False
        )


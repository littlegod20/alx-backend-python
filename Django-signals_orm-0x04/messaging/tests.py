from django.test import TestCase
from .models import Message, Notification
from django.contrib.auth.models import User
import uuid

class MessageTestCase(TestCase):
  def setUp(self):
    self.user1 = User.objects.create(username='user1', email='user1@example.com')
    self.user2 = User.objects.create(username='user2', email='user2@example.com')
    self.message = Message.objects.create(sender=self.user1, receiver=self.user2, content='Hello, how are you?')

  def test_message_creation(self):
    self.assertEqual(self.message.sender, self.user1)
    self.assertEqual(self.message.receiver, self.user2)
    self.assertEqual(self.message.content, 'Hello, how are you?')

  def test_notification_creation(self):
    self.assertEqual(Notification.objects.count(), 1)
    self.assertEqual(Notification.objects.first().user, self.user2)
    self.assertEqual(Notification.objects.first().message, self.message)

class NotificationTestCase(TestCase):
  def setUp(self):
    self.user1 = User.objects.create(username='user1', email='user1@example.com')
    self.user2 = User.objects.create(username='user2', email='user2@example.com')
    self.message = Message.objects.create(sender=self.user1, receiver=self.user2, content='Hello, how are you?')
    self.notification = Notification.objects.create(user=self.user2, message=self.message)

  def test_notification_creation(self):
    self.assertEqual(Notification.objects.count(), 1)
    self.assertEqual(Notification.objects.first().user, self.user2)
    self.assertEqual(Notification.objects.first().message, self.message)
    self.assertEqual(Notification.objects.first().is_read, False)

  def test_notification_read(self):
    self.notification.is_read = True
    self.notification.save()
    self.assertEqual(Notification.objects.first().is_read, True)

  def test_notification_unread(self):
    self.notification.is_read = False
    self.notification.save()
    self.assertEqual(Notification.objects.first().is_read, False)

  def test_notification_delete(self):
    self.notification.delete()
    self.assertEqual(Notification.objects.count(), 0)

  def test_notification_update(self):
    self.notification.message = 'Hello, how are you?'
    self.notification.save()


"""
URL configuration for chats app.
"""
from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register(r'chats', ConversationViewSet, basename='chat')
router.register(r'messages', MessageViewSet, basename='message')


urlpatterns = [
    path('', include(router.urls)),
]

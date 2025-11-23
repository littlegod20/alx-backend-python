"""
URL configuration for chats app.
"""
from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Create router using routers.DefaultRouter()
router = routers.DefaultRouter()
router.register(r'chats', ConversationViewSet, basename='chat')
router.register(r'messages', MessageViewSet, basename='message')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]

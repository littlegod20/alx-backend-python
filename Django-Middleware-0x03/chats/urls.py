"""
URL configuration for chats app.
"""
from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import ConversationViewSet, MessageViewSet


router = routers.DefaultRouter()
router.register(r'chats', ConversationViewSet, basename='chat')


# This allows URLs like: /api/chats/{conversation_id}/messages/
nested_router = NestedDefaultRouter(router, r'chats', lookup='conversation')
nested_router.register(r'messages', MessageViewSet, basename='conversation-messages')


router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(nested_router.urls)),
]

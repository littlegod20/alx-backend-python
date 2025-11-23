from django.shortcuts import render
from django.db import models
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .pagination import StandardResultsSetPagination


class ChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Chat objects.
    Uses IsParticipantOfConversation permission to ensure only authenticated
    users who are participants in a conversation can access chats.
    """
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        Filter chats to only show those where the current user is a participant.
        Optionally filter by conversation_id if provided.
        """
        user = self.request.user
        if user.is_authenticated:
            queryset = Chat.objects.filter(
                models.Q(user1=user) | models.Q(user2=user)
            )
            # Filter by conversation_id if provided as query parameter
            conversation_id = self.request.query_params.get('conversation_id')
            if conversation_id:
                queryset = queryset.filter(pk=conversation_id)
            return queryset
        return Chat.objects.none()


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Message objects.
    Uses IsParticipantOfConversation permission to ensure only authenticated
    users who are participants in a conversation can send, view, update, and delete messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        Filter messages to only show those from chats where the current user is a participant.
        Optionally filter by conversation_id if provided.
        """
        user = self.request.user
        if user.is_authenticated:
            queryset = Message.objects.filter(
                models.Q(chat__user1=user) | models.Q(chat__user2=user)
            )
            # Filter by conversation_id if provided as query parameter
            conversation_id = self.request.query_params.get('conversation_id')
            if conversation_id:
                queryset = queryset.filter(chat_id=conversation_id)
            return queryset
        return Message.objects.none()
    
    def create(self, request, *args, **kwargs):
        """
        Create a new message with conversation_id validation.
        Returns HTTP_403_FORBIDDEN if user is not a participant in the conversation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        chat_id = serializer.validated_data.get('chat')
        conversation_id = request.data.get('chat_id') or chat_id
        
        if conversation_id:
            try:
                chat = conversation_id if isinstance(conversation_id, Chat) else Chat.objects.get(pk=conversation_id)
                if self.request.user != chat.user1 and self.request.user != chat.user2:
                    return Response(
                        {"detail": f"You can only send messages to conversations you are part of. Chat {conversation_id} has participants: {chat.user1.username} and {chat.user2.username}, but you are {self.request.user.username}."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Chat.DoesNotExist:
                return Response(
                    {"detail": f"Chat with id {conversation_id} does not exist."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        """
        Automatically set the sender to the current user when creating a message.
        """
        serializer.save(sender=self.request.user)
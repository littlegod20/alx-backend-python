from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .pagination import StandardResultsSetPagination
from rest_framework.permissions import IsAuthenticated



class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Conversation objects.
    Uses IsParticipantOfConversation permission to ensure only authenticated
    users who are participants in a conversation can access conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['participants__email', 'participants__first_name', 'participants__last_name']
    ordering_fields = ['created_at', 'conversation_id']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter conversations to only show those where the current user is a participant.
        Optionally filter by conversation_id if provided.
        """
        user = self.request.user
        if user.is_authenticated:
            queryset = Conversation.objects.filter(participants=user)
            # Apply additional filters from filter_backends
            queryset = self.filter_queryset(queryset)
            return queryset
        return Conversation.objects.none()
    
    def perform_create(self, serializer):
        """
        Create a new conversation and automatically add the current user as a participant.
        """
        conversation = serializer.save()
        # Add the creator as a participant
        conversation.participants.add(self.request.user)


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
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['message_body', 'sender__email', 'sender__first_name', 'sender__last_name']
    ordering_fields = ['sent_at', 'message_id', 'conversation']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        """
        Filter messages to only show those from conversations where the current user is a participant.
        Optionally filter by conversation_id if provided.
        """
        user = self.request.user
        if user.is_authenticated:
            queryset = Message.objects.filter(conversation__participants=user)
            # Apply additional filters from filter_backends
            queryset = self.filter_queryset(queryset)
            return queryset
        return Message.objects.none()
    
    def create(self, request, *args, **kwargs):
        """
        Create a new message with conversation_id validation.
        Returns HTTP_403_FORBIDDEN if user is not a participant in the conversation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation_id = serializer.validated_data.get('conversation')
        
        if conversation_id:
            try:
                conversation = conversation_id if isinstance(conversation_id, Conversation) else Conversation.objects.get(pk=conversation_id)
                if self.request.user not in conversation.participants.all():
                    participant_emails = ', '.join([p.email for p in conversation.participants.all()])
                    return Response(
                        {"detail": f"You can only send messages to conversations you are part of. Conversation {conversation_id} has participants: {participant_emails}, but you are {self.request.user.email}."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Conversation.DoesNotExist:
                return Response(
                    {"detail": f"Conversation with id {conversation_id} does not exist."},
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
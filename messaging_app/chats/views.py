from rest_framework import viewsets, status
from rest_framework.response import Response
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
    
    def get_queryset(self):
        """
        Filter conversations to only show those where the current user is a participant.
        Optionally filter by conversation_id if provided.
        """
        user = self.request.user
        if user.is_authenticated:
            queryset = Conversation.objects.filter(participants=user)
            # Filter by conversation_id if provided as query parameter
            conversation_id = self.request.query_params.get('conversation_id')
            if conversation_id:
                queryset = queryset.filter(pk=conversation_id)
            return queryset
        return Conversation.objects.none()


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
        Filter messages to only show those from conversations where the current user is a participant.
        Optionally filter by conversation_id if provided.
        """
        user = self.request.user
        if user.is_authenticated:
            queryset = Message.objects.filter(conversation__participants=user)
            # Filter by conversation_id if provided as query parameter
            conversation_id = self.request.query_params.get('conversation_id')
            if conversation_id:
                queryset = queryset.filter(conversation_id=conversation_id)
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
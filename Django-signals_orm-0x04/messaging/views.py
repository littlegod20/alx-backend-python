#!/usr/bin/env python3
"""Views for messaging app.

"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import User, Message


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_user(request):
    """Delete the authenticated user's account."""
    user = request.user
    user.delete()
    return JsonResponse(
        {"message": "User account deleted successfully."},
        status=200
    )


@login_required
def get_messages(request):
    """Get messages for the authenticated user with optimized queries."""
    # Use select_related and prefetch_related to optimize queries
    # Filter messages where user is sender or receiver
    messages = Message.objects.filter(
        sender=request.user
    ) | Message.objects.filter(
        receiver=request.user
    )
    messages = messages.select_related(
        'sender',
        'receiver',
        'parent_message'
    ).prefetch_related(
        'replies__sender',
        'replies__receiver'
    ).order_by('-timestamp')
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'message_id': str(msg.message_id),
            'sender': msg.sender.email,
            'receiver': msg.receiver.email,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'edited': msg.edited,
            'parent_message_id': str(msg.parent_message.message_id) if msg.parent_message else None,
            'replies_count': msg.replies.count()
        })
    
    return JsonResponse({'messages': messages_data}, status=200)


@login_required
def get_threaded_message(request, message_id):
    """Get a message with all its replies in threaded format using recursive query."""
    try:
        # Get the message with optimized queries using filter with sender and receiver
        messages = Message.objects.filter(
            sender=request.user
        ) | Message.objects.filter(
            receiver=request.user
        )
        message = messages.select_related(
            'sender',
            'receiver',
            'parent_message',
            'parent_message__sender',
            'parent_message__receiver'
        ).prefetch_related(
            'replies__sender',
            'replies__receiver'
        ).get(message_id=message_id)
        
        # Get all replies recursively
        all_replies = message.get_all_replies()
        
        def serialize_replies(replies_list):
            """Serialize replies recursively."""
            result = []
            for reply_data in replies_list:
                reply = reply_data['message']
                result.append({
                    'message_id': str(reply.message_id),
                    'sender': reply.sender.email,
                    'receiver': reply.receiver.email,
                    'content': reply.content,
                    'timestamp': reply.timestamp.isoformat(),
                    'edited': reply.edited,
                    'replies': serialize_replies(reply_data['replies'])
                })
            return result
        
        message_data = {
            'message_id': str(message.message_id),
            'sender': message.sender.email,
            'receiver': message.receiver.email,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'edited': message.edited,
            'parent_message_id': str(message.parent_message.message_id) if message.parent_message else None,
            'replies': serialize_replies(all_replies)
        }
        
        return JsonResponse(message_data, status=200)
        
    except Message.DoesNotExist:
        return JsonResponse(
            {'error': 'Message not found'},
            status=404
        )


@login_required
def get_unread_messages(request):
    """Get unread messages for the authenticated user using custom manager."""
    # Use the custom UnreadMessagesManager with .only() optimization
    unread_messages = Message.unread.for_user(request.user).select_related(
        'sender',
        'receiver'
    ).only(
        'message_id',
        'sender',
        'receiver',
        'content',
        'timestamp',
        'edited',
        'read',
        'parent_message'
    ).order_by('-timestamp')
    
    messages_data = []
    for msg in unread_messages:
        messages_data.append({
            'message_id': str(msg.message_id),
            'sender': msg.sender.email,
            'receiver': msg.receiver.email,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'edited': msg.edited,
            'read': msg.read,
            'parent_message_id': str(msg.parent_message.message_id) if msg.parent_message else None,
        })
    
    return JsonResponse({
        'unread_count': len(messages_data),
        'messages': messages_data
    }, status=200)


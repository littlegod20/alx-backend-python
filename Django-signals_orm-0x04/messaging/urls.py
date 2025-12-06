"""
URL configuration for messaging project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from messaging import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/delete/', views.delete_user, name='delete_user'),
    path('api/messages/', views.get_messages, name='get_messages'),
    path('api/messages/<uuid:message_id>/thread/', views.get_threaded_message, name='get_threaded_message'),
    path('api/messages/unread/', views.get_unread_messages, name='get_unread_messages'),
]

from django.urls import path
from apps.messaging import views
urlpatterns = [
    path('admin-panel/chat/', views.admin_chat, name='admin_chat'),
    path('api/chat/messages/', views.api_messages, name='api_chat_messages'),
    path('api/chat/send/', views.api_send, name='api_chat_send'),
    path('api/chat/unread/', views.api_unread, name='api_chat_unread'),
    path('api/chat/mark-read/', views.api_mark_read, name='api_chat_mark_read'),
]

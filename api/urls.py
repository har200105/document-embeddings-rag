from django.urls import path
from .views import (process_document,get_all_asset_ids,start_chat,chat_message,chat_history,chat_history_by_id,)

urlpatterns= [
    path('documents/process',process_document),
    path('assets-list',get_all_asset_ids),
    path('chat/start',start_chat),
    path('chat/message',chat_message),
    path('chat/history/all',chat_history),
    path('chat/history/<str:id>',chat_history_by_id),
]
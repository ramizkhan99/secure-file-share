from django.urls import path

from files.views import handle_file_requests, get_share_link, get_shared_file

urlpatterns = [
    path('share/', get_share_link, name='get_share_link'),
    path('shared/<str:file_id>/', get_shared_file, name='get_shared_file'),
    path('', handle_file_requests, name='handle_file_requests'),
]
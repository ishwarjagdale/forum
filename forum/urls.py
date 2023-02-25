from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path

from .views import home, new_thread, sign_up, log_in, thread_view

urlpatterns = [
    path('', home, name='home'),
    path('new-thread/', new_thread, name='new-thread'),
    path('edit-thread/<thread_id>', new_thread, name='edit-thread'),
    path('thread/<thread_id>', thread_view, name='thread-view'),
    path('signup/', sign_up, name='signup'),
    path('login/', log_in, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path

from .views import home, new_thread, sign_up, log_in

urlpatterns = [
    path('', home, name='home'),
    path('new-thread/', new_thread, name='new-thread'),
    path('signup/', sign_up, name='signup'),
    path('login/', log_in, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
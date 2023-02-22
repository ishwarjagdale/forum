from django.urls import path
from .views import home, new_thread


urlpatterns = [
    path('', home, name='home'),
    path('new-thread/', new_thread, name='new-thread')
]
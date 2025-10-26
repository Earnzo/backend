from django.urls import path
from .views import StakeCreateView, StakeListView, StakeDetailView

urlpatterns = [
    path('', StakeListView.as_view(), name='stake_list'),
    path('create/', StakeCreateView.as_view(), name='stake_create'),
    path('<uuid:pk>/', StakeDetailView.as_view(), name='stake_detail'),
]

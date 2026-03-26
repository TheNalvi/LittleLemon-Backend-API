from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.RegisterView.as_view()),
    path('users/me/', views.MeView.as_view()),
    path('menu-items/', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>/', views.SingeMenuItemView.as_view()),
    path('groups/<str:group_name>/users/<int:pk>/', views.ManagersRemoveView.as_view()),
    path('groups/<str:group_name>/users/', views.GroupManagementView.as_view()),
    path('cart/menu-items/', views.CartMenuItemView.as_view()),
    path('orders/', views.OrderMenuItemView.as_view()),
    path('orders/<int:pk>/', views.OrderDetailView.as_view()),
    path('showusers/', views.UsersView.as_view()),
]
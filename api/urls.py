from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView,
    LogoutView,
    RegisterView,
    ProfileUpdateView,
    SoftDeleteUserView,
    AccessRoleRuleListCreateView,
    AccessRoleRuleDetailView,
    UserViewSet,
    ProductViewSet,
    StoreViewSet,
    MockUsersView,
    MockProductsView,
    MockStoresView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'stores', StoreViewSet, basename='store')

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/profile/', ProfileUpdateView.as_view(), name='update-profile'),
    path('auth/delete/', SoftDeleteUserView.as_view(), name='soft-delete'),

    # Access rules endpoints
    path('access-rules/', AccessRoleRuleListCreateView.as_view(), name='access-rules'),
    path('access-rules/<int:pk>/', AccessRoleRuleDetailView.as_view(), name='access-rule-detail'),

    path('mock/users/', MockUsersView.as_view(), name='mock-users'),
    path('mock/products/', MockProductsView.as_view(), name='mock-products'),
    path('mock/stores/', MockStoresView.as_view(), name='mock-stores'),
    # Include router URLs for viewsets
    path('', include(router.urls)),
]

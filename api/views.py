from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from .authentication import JWTAuthentication
from .models import (
    User,
    Role,
    AccessRoleRule,
    Product,
    Store,
    Order,
    RevokedToken
)
from .serializers import (
    AccessRoleRuleSerializer,
    UserSerializer,
    ProductSerializer,
    StoreSerializer,
    OrderSerializer
)
from .permissions import CanAccessAccessRules, RoleBasedPermission, MockRoleBasedPermission
from .utils import create_jwt
import json
import bcrypt

class LoginView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        token = create_jwt(user.id, user.role.name)
        return Response({"token": token}, status=status.HTTP_200_OK)

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = []

    def post(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return Response({"detail": "Authorization header missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            prefix, token = auth_header.split(" ")
            if prefix.lower() != "bearer":
                return Response({"detail": "Invalid token prefix"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"detail": "Invalid Authorization header format"}, status=status.HTTP_400_BAD_REQUEST)

        # Save token to revoked list
        RevokedToken.objects.get_or_create(token=token)
        return Response({"message": "Logout successful, token revoked"}, status=status.HTTP_200_OK)

class RegisterView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")
        password_repeat = data.get("password_repeat")

        if not all([full_name, email, password, password_repeat]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if password != password_repeat:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        role = Role.objects.get(name="User")
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User.objects.create(email=email, full_name=full_name, password_hash=password_hash, role=role)

        token = create_jwt(user.id, role.name)
        return Response({"token": token, "user_id": user.id}, status=status.HTTP_201_CREATED)

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ProfileUpdateView(APIView):

    def put(self, request):
        user = request.user
        data = request.data

        full_name = data.get("full_name")
        password = data.get("password")
        password_repeat = data.get("password_repeat")

        if full_name:
            user.full_name = full_name

        if password:
            if password != password_repeat:
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
            user.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        user.save()
        return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class SoftDeleteUserView(APIView):

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response({"message": "Account deleted (soft) successfully"}, status=status.HTTP_200_OK)

class AccessRoleRuleListCreateView(generics.ListCreateAPIView):
    queryset = AccessRoleRule.objects.all()
    serializer_class = AccessRoleRuleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanAccessAccessRules]

class AccessRoleRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessRoleRule.objects.all()
    serializer_class = AccessRoleRuleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanAccessAccessRules]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    business_element = "Users"

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    business_element = "Products"

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    business_element = "Stores"


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    business_element = "Orders"

# Mock Users endpoint
class MockUsersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, MockRoleBasedPermission]
    business_element = "Users"

    def get(self, request):
        mock_users = [
            {
                "id": 1,
                "full_name": "Alice",
                "email": "alice@example.com",
                "password_hash": "$2b$12$abcdefghijklmnopqrstuv",  # fake bcrypt hash
                "role": "Admin",  # e.g. Admin role id
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
                "date_joined": "2025-11-13T09:00:00Z",
            },
            {
                "id": 2,
                "full_name": "Bob",
                "email": "bob@example.com",
                "password_hash": "$2b$12$uvwxyzabcdefghijklmn",  # fake bcrypt hash
                "role": "User",  # e.g. Manager role id
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
                "date_joined": "2025-11-13T09:30:00Z",
            },
        ]
        # Access rule provided by MockRoleBasedPermission
        rule = getattr(self, "access_rule", None)
        if not rule:
            return Response({"detail": "Forbidden"}, status=403)

        # If read_all_permission, return all users
        if rule.read_all_permission:
            return Response(mock_users)

        # If read_permission, return only users owned by this user
        if rule.read_permission:
            filtered = [s for s in mock_users if s["id"] == request.user.id]
            return Response(filtered)

        # Otherwise, forbid access
        return Response({"detail": "Forbidden"}, status=403)

# Mock Products endpoint
class MockProductsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, MockRoleBasedPermission]
    business_element = "Products"

    def get(self, request):
        # fake product list
        mock_products = [
            {
                "id": 1,
                "name": "Laptop",
                "description": "High-performance laptop with 16GB RAM and 1TB SSD.",
                "price": 1200.00,
                "store": 1,
                "store_name": "Main Street Store",
                "is_active": True,
                "owner": 1,
                "owner_name": "Alice",
                "created_at": "2025-11-13T09:00:00Z",
                "updated_at": "2025-11-13T09:15:00Z",
            },
            {
                "id": 2,
                "name": "Phone",
                "description": "Latest smartphone with OLED display and 128GB storage.",
                "price": 800.00,
                "store": 2,  # Mall Store
                "store_name": "Mall Store",
                "is_active": True,
                "owner": 2,  # Bob
                "owner_name": "Bob",
                "created_at": "2025-11-13T09:30:00Z",
                "updated_at": "2025-11-13T09:45:00Z",
            },
        ]
        # Access rule provided by MockRoleBasedPermission
        rule = getattr(self, "access_rule", None)
        if not rule:
            return Response({"detail": "Forbidden"}, status=403)

        # If read_all_permission, return all products
        if rule.read_all_permission:
            return Response(mock_products)

        # If read_permission, return only products owned by this user
        if rule.read_permission:
            filtered = [s for s in mock_products if s["owner"] == request.user.id]
            return Response(filtered)

        # Otherwise, forbid access
        return Response({"detail": "Forbidden"}, status=403)

# Mock Stores endpoint
class MockStoresView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, MockRoleBasedPermission]
    business_element = "Stores"

    def get(self, request):
        # All mock stores
        mock_stores = [
            {
                "id": 1,
                "name": "Main Street Store",
                "address": "123 Main St",
                "is_active": True,
                "owner": 1,  # Alice
                "owner_email": "alice@example.com",
            },
            {
                "id": 2,
                "name": "Mall Store",
                "address": "456 Mall Rd",
                "is_active": True,
                "owner": 2,  # Bob
                "owner_email": "bob@example.com",
            },
        ]

        # Access rule provided by MockRoleBasedPermission
        rule = getattr(self, "access_rule", None)
        if not rule:
            return Response({"detail": "Forbidden"}, status=403)

        # If read_all_permission, return all stores
        if rule.read_all_permission:
            return Response(mock_stores)

        # If read_permission, return only stores owned by this user
        if rule.read_permission:
            filtered = [s for s in mock_stores if s["owner"] == request.user.id]
            return Response(filtered)

        # Otherwise, forbid access
        return Response({"detail": "Forbidden"}, status=403)
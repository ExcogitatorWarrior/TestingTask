from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import (
    User,
    Role,
    AccessRoleRule,
    BusinessElement,
    Product,
    Store
)
from api.utils import create_jwt
import json
import bcrypt

class AccessRoleRuleTests(APITestCase):
    def setUp(self):
        # Create roles
        self.admin_role, _ = Role.objects.get_or_create(name="Admin")
        self.user_role, _ = Role.objects.get_or_create(name="User")

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            full_name="Admin User",
            password="password123"
        )
        # Ensure role matches exactly
        self.admin_user.role = self.admin_role
        self.admin_user.save()

        # Create non-admin user
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            full_name="Normal User",
            password="password123",
            role_name="User"
        )

        # Create a business element and rule for testing
        self.element = BusinessElement.objects.create(name="Test Element")
        self.access_rule = AccessRoleRule.objects.create(
            role=self.admin_role,
            element=self.element,
            read_permission=True
        )

        # Endpoints
        self.login_url = reverse("login")
        self.access_rules_url = reverse("access-rules")

    def get_jwt_token(self, email, password):
        """Helper to get JWT token for a user"""
        response = self.client.post(
            self.login_url,
            {"email": email, "password": password},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["token"]

    def test_admin_can_list_rules(self):
        """Admin should have access to list all access rules"""
        token = self.get_jwt_token("admin@example.com", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.access_rules_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_non_admin_cannot_list_rules(self):
        """Non-admin roles should receive 403 Forbidden"""
        token = self.get_jwt_token("user@example.com", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.access_rules_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_gets_401(self):
        """Requests without JWT should return 401"""
        self.client.credentials()  # Remove any credentials
        response = self.client.get(self.access_rules_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        """Clean up all test data"""
        User.objects.all().delete()
        Role.objects.all().delete()
        AccessRoleRule.objects.all().delete()
        BusinessElement.objects.all().delete()

class ProductPermissionTests(APITestCase):
    def setUp(self):
        # ----------------------
        # Roles
        # ----------------------
        self.admin_role, _ = Role.objects.get_or_create(name="Admin")
        self.user_role, _ = Role.objects.get_or_create(name="User")

        # ----------------------
        # Users
        # ----------------------
        # Admin
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            full_name="Admin User",
            password="password123"
        )
        self.admin_user.role = self.admin_role
        self.admin_user.save()

        # Normal User
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            full_name="Normal User",
            password="password123",
            role_name="User"
        )

        # ----------------------
        # Stores and Products element
        # ----------------------
        self.store = Store.objects.create(name="Test Store")
        products_element, _ = BusinessElement.objects.get_or_create(name="Products")

        # ----------------------
        # Access rules
        # ----------------------
        # User role: can create, read products
        AccessRoleRule.objects.create(
            role=self.user_role,
            element=products_element,
            create_permission=True,
            read_permission=True  # optional if listing is needed
        )

        # Admin role: full permissions
        AccessRoleRule.objects.create(
            role=self.admin_role,
            element=products_element,
            create_permission=True,
            read_permission=True,
            update_permission=True,
            delete_permission=True,
            update_all_permission=True,
            delete_all_permission=True
        )

        # ----------------------
        # JWT / endpoints
        # ----------------------
        self.login_url = reverse("login")
        self.products_url = reverse("product-list")  # DRF router generates this

    def get_jwt_token(self, email, password):
        """Helper to get JWT token for a user"""
        response = self.client.post(
            self.login_url,
            {"email": email, "password": password},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["token"]

    def test_user_cannot_delete_product_but_admin_can(self):
        """User creates a product, cannot delete it, admin deletes it"""
        # ----------------------
        # Get JWT tokens
        # ----------------------
        user_token = self.get_jwt_token("user@example.com", "password123")
        admin_token = self.get_jwt_token("admin@example.com", "password123")

        # ----------------------
        # User creates a product
        # ----------------------
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_token}")
        product_data = {
            "name": "Test Product",
            "description": "A product created by user",
            "price": "9.99",
            "store": self.store.id,
            "is_active": True
        }
        response = self.client.post(self.products_url, product_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        product_id = response.data["id"]
        product_detail_url = reverse("product-detail", args=[product_id])

        # ----------------------
        # User tries to delete the product → should fail
        # ----------------------
        response = self.client.delete(product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ----------------------
        # Admin deletes the product → should succeed
        # ----------------------
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        response = self.client.delete(product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self):
        """Clean up all test data"""
        Product.objects.all().delete()
        Store.objects.all().delete()
        User.objects.all().delete()
        Role.objects.all().delete()
        AccessRoleRule.objects.all().delete()
        BusinessElement.objects.all().delete()

class AccessRulesPermissionTests(APITestCase):
    def setUp(self):
        # ----------------------
        # Roles
        # ----------------------
        self.admin_role, _ = Role.objects.get_or_create(name="Admin")
        self.manager_role, _ = Role.objects.get_or_create(name="Manager")
        self.user_role, _ = Role.objects.get_or_create(name="User")

        # ----------------------
        # Users
        # ----------------------
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            full_name="Admin User",
            password="password123"
        )
        self.admin_user.role = self.admin_role
        self.admin_user.save()

        self.manager_user = User.objects.create_user(
            email="manager@example.com",
            full_name="Manager User",
            password="password123",
            role_name="Manager"
        )

        self.normal_user = User.objects.create_user(
            email="user@example.com",
            full_name="Normal User",
            password="password123",
            role_name="User"
        )

        # ----------------------
        # Business element
        # ----------------------
        self.access_rules_element, _ = BusinessElement.objects.get_or_create(name="Access Rules")

        # ----------------------
        # AccessRoleRule
        # ----------------------
        # Manager role can read Access Rules
        AccessRoleRule.objects.create(
            role=self.manager_role,
            element=self.access_rules_element,
            read_permission=True
        )

        # Admin already has access via their role, no need to create extra

        # ----------------------
        # Endpoints
        # ----------------------
        self.access_rules_url = reverse("access-rules")

    def get_jwt_token(self, email, password):
        """Helper to get JWT token for a user"""
        response = self.client.post(
            reverse("login"),
            {"email": email, "password": password},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["token"]

    def test_admin_can_access_access_rules(self):
        token = self.get_jwt_token("admin@example.com", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.access_rules_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_can_access_access_rules(self):
        token = self.get_jwt_token("manager@example.com", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.access_rules_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_normal_user_cannot_access_access_rules(self):
        token = self.get_jwt_token("user@example.com", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.access_rules_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        """Clean up all test data"""
        AccessRoleRule.objects.all().delete()
        BusinessElement.objects.all().delete()
        User.objects.all().delete()
        Role.objects.all().delete()

class ProductOwnershipPermissionTests(APITestCase):
    def setUp(self):
        # --- Roles ---
        self.role_user, _ = Role.objects.get_or_create(name="User")
        self.role_admin, _ = Role.objects.get_or_create(name="Admin")

        # --- Users ---
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            full_name="User One",
            password="password123",
            role_name="User"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            full_name="User Two",
            password="password123",
            role_name="User"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            full_name="Admin User",
            password="password123"
        )

        # --- Business element ---
        self.products_element, _ = BusinessElement.objects.get_or_create(name="Products")

        # --- Access rules ---
        # User role: can create and read products they own
        self.user_rule, _ = AccessRoleRule.objects.get_or_create(
            role=self.role_user,
            element=self.products_element,
            defaults=dict(
                create_permission=True,
                read_permission=True,
                update_permission=True,
                delete_permission=True
            )
        )

        # Admin role: can read/update/delete all products
        self.admin_rule, _ = AccessRoleRule.objects.get_or_create(
            role=self.role_admin,
            element=self.products_element,
            defaults=dict(
                read_all_permission=True,
                update_all_permission=True,
                delete_all_permission=True
            )
        )

        # --- Store ---
        self.store = Store.objects.create(name="Main Store", address="123 Market Street")

        # --- Products URL ---
        self.products_url = reverse("product-list")

    def get_jwt_token(self, email, password):
        """Helper to get JWT token for a user"""
        response = self.client.post(
            reverse("login"),
            {"email": email, "password": password},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["token"]

    def test_ownership_delete_permission(self):
        """User1 creates a product, User2 fails to delete, permissions updated, User2 succeeds"""
        # --- User1 creates a product ---
        token1 = self.get_jwt_token("user1@example.com", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")

        create_response = self.client.post(
            self.products_url,
            {
                "name": "User1 Product",
                "store": self.store.id,
                "price": "9.99",
                "owner": self.user1.id
            },
            format="json"
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED, create_response.data)
        product_id = create_response.data["id"]

        # --- User2 tries to delete (should fail) ---
        token2 = self.get_jwt_token("user2@example.com", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")

        delete_url = reverse("product-detail", args=[product_id])
        delete_response_1 = self.client.delete(delete_url)
        self.assertEqual(delete_response_1.status_code, status.HTTP_403_FORBIDDEN)

        # --- Update user role to allow delete_all ---
        self.user_rule.delete_all_permission = True
        self.user_rule.save()

        # --- User2 tries again (should succeed) ---
        delete_response_2 = self.client.delete(delete_url)
        self.assertEqual(delete_response_2.status_code, status.HTTP_204_NO_CONTENT)

        # --- Verify deletion ---
        self.assertFalse(Product.objects.filter(id=product_id).exists())

class LogoutAndTokenRevocationTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="user@example.com",
            full_name="Test User",
            password="password123",
            role_name="User"
        )
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.profile_url = reverse("update-profile")

    def get_jwt_token(self, email, password):
        """Helper to get JWT token for a user"""
        response = self.client.post(
            reverse("login"),
            {"email": email, "password": password},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["token"]

    def test_profile_access_with_logout(self):
        # --- Step 1: Login ---
        token = self.get_jwt_token("user@example.com", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # --- Step 2: Access profile (should succeed) ---
        response = self.client.put(self.profile_url, {"full_name": "Updated Name"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Updated Name")

        # --- Step 3: Logout ---
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # --- Step 4: Try to access profile again with same token (should fail) ---
        response = self.client.put(self.profile_url, {"full_name": "Hacker Name"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # --- Step 5: Login again ---
        token2 = self.get_jwt_token("user@example.com", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")

        # --- Step 6: Access profile again (should succeed) ---
        response = self.client.put(self.profile_url, {"full_name": "New Name After Re-login"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "New Name After Re-login")
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.conf import settings
import bcrypt
from django.utils import timezone

class Role(models.Model):
    ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("Moderator", "Moderator"),
        ("User", "User"),
        ("Guest", "Guest"),
    ]

    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, role_name="User"):
        if not email:
            raise ValueError("Users must have an email address")

        # get role
        try:
            role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            raise ValueError(f"Role '{role_name}' does not exist")

        email = self.normalize_email(email)
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        user = self.model(
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            role=role,
            is_active=True
        )
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password):
        user = self.create_user(email, full_name, password, role_name="Admin")
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)       # Admins only
    is_superuser = models.BooleanField(default=False)   # Admins only
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    def __str__(self):
        return f"{self.full_name} ({self.email}) - {self.role.name}"

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode(), self.password_hash.encode())

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

class BusinessElement(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class AccessRoleRule(models.Model):
    role = models.ForeignKey("Role", on_delete=models.CASCADE, related_name="access_rules")
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, related_name="access_rules")

    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'element')

    def __str__(self):
        return f"{self.role.name} → {self.element.name}"


class Store(models.Model):
    """
    Represents a store where products are sold.
    """
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(  # Store owner (User)
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_stores',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Represents a product belonging to a store.
    Includes ownership so we can check object-level permissions.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(  # Product creator/owner
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_products',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.store.name})"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="orders"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_orders",
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Calculate total price automatically if not provided
        if not self.total_price:
            self.total_price = self.product.price * self.quantity
        # Set owner to the user if not explicitly set
        if not self.owner:
            self.owner = self.user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.product.name} x{self.quantity} by {self.user.full_name}"

class RevokedToken(models.Model):
    token = models.CharField(max_length=512, unique=True)
    revoked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RevokedToken({self.token[:20]}...)"
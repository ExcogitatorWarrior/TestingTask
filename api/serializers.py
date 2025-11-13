from rest_framework import serializers
from .models import AccessRoleRule, User, Product, Store, Order

class AccessRoleRuleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    element_name = serializers.CharField(source='element.name', read_only=True)

    class Meta:
        model = AccessRoleRule
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password_hash': {'write_only': True},
            'is_staff': {'read_only': True},
            'is_superuser': {'read_only': True},
        }

class StoreSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')  # show owner email

    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'is_active', 'owner']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')  # show owner email

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'store', 'is_active', 'owner']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['owner', 'total_price', 'created_at', 'updated_at']
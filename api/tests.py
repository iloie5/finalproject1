from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
import json

from api.models import Order, User, Product, OrderItem
from api.auth_serializers import UserRegistrationSerializer

User = get_user_model()


class UserOrderTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='test')
        user2 = User.objects.create_user(username='user2', password='test')
        Order.objects.create(user=user1)
        Order.objects.create(user=user1)
        Order.objects.create(user=user2)
        Order.objects.create(user=user2)

    def test_user_order_endpoint_retrieves_only_authenticated_user_orders(self):
        user = User.objects.get(username='user2')
        self.client.force_login(user)
        response = self.client.get(reverse('user-orders'))

        assert response.status_code == status.HTTP_200_OK
        orders = response.json()
        self.assertTrue(all(order['user'] == user.id for order in orders))

    def test_user_order_list_unauthenticated(self):
        response = self.client.get(reverse('user-orders'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProductTestCase(APITestCase):
    def setUp(self):
        self.product_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': Decimal('19.99'),
            'stock': 10
        }
        self.product = Product.objects.create(**self.product_data)
        self.admin_user = User.objects.create_superuser(
            username='admin', 
            password='admin123',
            email='admin@test.com'
        )

    def test_product_list(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_product_detail(self):
        response = self.client.get(reverse('product-detail', kwargs={'product_id': self.product.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)

    def test_product_create_unauthorized(self):
        response = self.client.post(reverse('product-list'), self.product_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_create_authorized(self):
        self.client.force_authenticate(user=self.admin_user)
        new_product_data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': '29.99',
            'stock': 5
        }
        response = self.client.post(reverse('product-list'), new_product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_product_update_unauthorized(self):
        update_data = {'name': 'Updated Product'}
        response = self.client.patch(
            reverse('product-detail', kwargs={'product_id': self.product.id}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_delete_unauthorized(self):
        response = self.client.delete(
            reverse('product-detail', kwargs={'product_id': self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticationTestCase(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'recovery_question': 'What is your favorite color?',
            'recovery_answer': 'blue'
        }

    def test_user_registration(self):
        response = self.client.post(reverse('register'), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_registration_password_mismatch(self):
        self.user_data['password_confirm'] = 'different'
        response = self.client.post(reverse('register'), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_verification(self):
        # Create user first
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            recovery_question='What is your favorite color?',
            recovery_answer='blue'
        )
        
        # Mock verification code
        cache.set('email_verification_test@example.com', '123456', timeout=300)
        
        verification_data = {
            'email': 'test@example.com',
            'verification_code': '123456'
        }
        response = self.client.post(reverse('verify-email'), verification_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)

    def test_password_reset_request(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            recovery_question='What is your favorite color?',
            recovery_answer='blue'
        )
        
        reset_data = {
            'email': 'test@example.com',
            'recovery_answer': 'blue'
        }
        response = self.client.post(reverse('password-reset-request'), reset_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_wrong_answer(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            recovery_question='What is your favorite color?',
            recovery_answer='blue'
        )
        
        reset_data = {
            'email': 'test@example.com',
            'recovery_answer': 'red'
        }
        response = self.client.post(reverse('password-reset-request'), reset_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_profile_authenticated(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_user_profile_unauthenticated(self):
        response = self.client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('19.99'),
            stock=10
        )
        self.order = Order.objects.create(user=self.user)
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2
        )

    def test_order_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_orders_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('user-orders'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_orders_unauthenticated(self):
        response = self.client.get(reverse('user-orders'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProductFilterTestCase(APITestCase):
    def setUp(self):
        Product.objects.create(
            name='Cheap Product',
            description='A cheap product',
            price=Decimal('9.99'),
            stock=5
        )
        Product.objects.create(
            name='Expensive Product',
            description='An expensive product',
            price=Decimal('99.99'),
            stock=0
        )
        Product.objects.create(
            name='Medium Product',
            description='A medium product',
            price=Decimal('49.99'),
            stock=10
        )

    def test_price_filter(self):
        response = self.client.get('/products/?price__lt=50')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_name_search(self):
        response = self.client.get('/products/?search=cheap')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_in_stock_filter(self):
        response = self.client.get('/products/?in_stock=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return only products with stock > 0
        for product in response.data['results']:
            self.assertGreater(product['stock'], 0)

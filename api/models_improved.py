import uuid
import hashlib
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class User(AbstractUser):
    email = models.EmailField(unique=True, validators=[])  # Custom email validation
    is_email_verified = models.BooleanField(default=False)
    recovery_question = models.CharField(max_length=200, blank=True)
    recovery_answer_hash = models.CharField(max_length=64, blank=True)  # Hashed for security
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_password_change = models.DateTimeField(default=timezone.now)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    def set_recovery_answer(self, answer):
        """Hash and store recovery answer"""
        self.recovery_answer_hash = hashlib.sha256(answer.lower().strip().encode()).hexdigest()
    
    def check_recovery_answer(self, answer):
        """Check recovery answer against hash"""
        if not self.recovery_answer_hash:
            return False
        return self.recovery_answer_hash == hashlib.sha256(answer.lower().strip().encode()).hexdigest()
    
    def is_account_locked(self):
        """Check if account is locked due to failed attempts"""
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        return False
    
    def lock_account(self, minutes=30):
        """Lock account for specified minutes"""
        self.locked_until = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save()
    
    def unlock_account(self):
        """Unlock account and reset failed attempts"""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save()


class Product(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        DISCONTINUED = 'discontinued', 'Discontinued'
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=2000)  # Added length limit
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]  # Minimum price validation
    )
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'stock']),
            models.Index(fields=['name']),
        ]
    
    @property
    def in_stock(self):
        return self.stock > 0 and self.status == self.StatusChoices.ACTIVE
    
    @property
    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold
    
    def clean(self):
        """Custom validation"""
        if self.price <= 0:
            raise ValidationError({'price': 'Price must be greater than 0.'})
        if self.stock < 0:
            raise ValidationError({'stock': 'Stock cannot be negative.'})
    
    def __str__(self):
        return self.name


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'
    
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)  # Changed from CASCADE
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,  # Increased length
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def calculate_total(self):
        """Calculate total amount from order items"""
        total = sum(item.item_subtotal for item in self.items.all())
        self.total_amount = total
        return total
    
    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in [self.StatusChoices.PENDING, self.StatusChoices.CONFIRMED]
    
    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)  # Changed from CASCADE
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]  # Quantity limits
    )
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Locked price
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['order', 'product']  # Prevent duplicate products in same order
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    @property
    def item_subtotal(self):
        return self.unit_price * self.quantity
    
    def clean(self):
        """Custom validation"""
        if self.product.stock < self.quantity:
            raise ValidationError(
                f'Not enough stock. Available: {self.product.stock}, Requested: {self.quantity}'
            )
        if self.product.status != Product.StatusChoices.ACTIVE:
            raise ValidationError('Cannot add inactive product to order.')
    
    def save(self, *args, **kwargs):
        """Override save to lock price and validate stock"""
        if not self.pk:  # New instance
            self.unit_price = self.product.price
            self.clean()
            # Update product stock
            self.product.stock -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to restore stock"""
        if self.pk:
            self.product.stock += self.quantity
            self.product.save()
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_id}"


class OrderHistory(models.Model):
    """Audit trail for order changes"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']


class ProductAudit(models.Model):
    """Audit trail for product changes"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='audit_log')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    field_name = models.CharField(max_length=50)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_at']

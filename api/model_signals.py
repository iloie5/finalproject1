from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import User, Product, Order, OrderItem, OrderHistory, ProductAudit
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Handle user creation and updates"""
    if created:
        logger.info(f"New user created: {instance.username}")
        # Send welcome email
        try:
            send_mail(
                'Welcome to Our E-Commerce Platform',
                f'Hello {instance.username},\n\nWelcome to our platform! Please verify your email to get started.',
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email to {instance.email}: {e}")
    else:
        # Log user updates
        logger.info(f"User updated: {instance.username}")


@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, **kwargs):
    """Handle product updates before saving"""
    if instance.pk:
        # Get the old instance
        try:
            old_instance = Product.objects.get(pk=instance.pk)
            
            # Check for price changes
            if old_instance.price != instance.price:
                logger.info(f"Product {instance.name} price changed from {old_instance.price} to {instance.price}")
            
            # Check for stock changes
            if old_instance.stock != instance.stock:
                logger.info(f"Product {instance.name} stock changed from {old_instance.stock} to {instance.stock}")
                
                # Check for low stock
                if instance.stock <= instance.low_stock_threshold:
                    logger.warning(f"Product {instance.name} is low on stock: {instance.stock}")
                    
        except Product.DoesNotExist:
            pass


@receiver(post_save, sender=Product)
def product_post_save(sender, instance, created, **kwargs):
    """Handle product creation and updates"""
    if created:
        logger.info(f"New product created: {instance.name}")
    else:
        logger.info(f"Product updated: {instance.name}")


@receiver(pre_save, sender=Order)
def order_pre_save(sender, instance, **kwargs):
    """Handle order updates before saving"""
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            
            # Check for status changes
            if old_instance.status != instance.status:
                logger.info(f"Order {instance.order_id} status changed from {old_instance.status} to {instance.status}")
                
                # Create history entry
                OrderHistory.objects.create(
                    order=instance,
                    old_status=old_instance.status,
                    new_status=instance.status,
                    changed_at=timezone.now()
                )
                
        except Order.DoesNotExist:
            pass


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    """Handle order creation and updates"""
    if created:
        logger.info(f"New order created: {instance.order_id}")
    else:
        logger.info(f"Order updated: {instance.order_id}")


@receiver(post_save, sender=OrderItem)
def order_item_post_save(sender, instance, created, **kwargs):
    """Handle order item creation and updates"""
    if created:
        logger.info(f"Order item added: {instance.product.name} to order {instance.order.order_id}")
        
        # Update order total
        instance.order.calculate_total()
        instance.order.save()
    else:
        logger.info(f"Order item updated: {instance.product.name} in order {instance.order.order_id}")


@receiver(post_delete, sender=OrderItem)
def order_item_post_delete(sender, instance, **kwargs):
    """Handle order item deletion"""
    logger.info(f"Order item removed: {instance.product.name} from order {instance.order.order_id}")
    
    # Update order total
    instance.order.calculate_total()
    instance.order.save()


@receiver(post_save, sender=User)
def user_failed_login_tracking(sender, instance, **kwargs):
    """Track failed login attempts"""
    if instance.failed_login_attempts >= 5:
        if not instance.is_account_locked():
            instance.lock_account(minutes=30)
            logger.warning(f"Account locked for user {instance.username} due to failed login attempts")


# Custom signal for low stock alerts
from django.dispatch import Signal

low_stock_alert = Signal()


@receiver(low_stock_alert)
def handle_low_stock_alert(sender, product, **kwargs):
    """Handle low stock alerts"""
    logger.warning(f"Low stock alert for product: {product.name} (Stock: {product.stock})")
    
    # Send email to admin
    try:
        send_mail(
            'Low Stock Alert',
            f'Product "{product.name}" is running low on stock. Current stock: {product.stock}',
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMINS[0][1] if settings.ADMINS else 'admin@example.com'],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Failed to send low stock alert email: {e}")


# Custom signal for order status changes
order_status_changed = Signal()


@receiver(order_status_changed)
def handle_order_status_change(sender, order, old_status, new_status, **kwargs):
    """Handle order status changes"""
    logger.info(f"Order {order.order_id} status changed from {old_status} to {new_status}")
    
    # Send email to user for important status changes
    important_statuses = ['confirmed', 'shipped', 'delivered', 'cancelled']
    if new_status in important_statuses:
        try:
            status_messages = {
                'confirmed': 'Your order has been confirmed and is being processed.',
                'shipped': 'Your order has been shipped and is on its way.',
                'delivered': 'Your order has been delivered successfully.',
                'cancelled': 'Your order has been cancelled.'
            }
            
            send_mail(
                f'Order {order.order_id} Status Update',
                f'Your order status has been updated to: {new_status}\n\n{status_messages.get(new_status, "")}',
                settings.DEFAULT_FROM_EMAIL,
                [order.user.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send order status email: {e}")

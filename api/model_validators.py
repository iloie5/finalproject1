from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import re


class EmailValidator:
    """Custom email validation"""
    
    @staticmethod
    def validate_email_domain(email):
        """Validate email domain"""
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        domain = email.split('@')[1].lower()
        if domain not in allowed_domains:
            raise ValidationError(
                _('Email domain not allowed. Allowed domains: %(domains)s'),
                params={'domains': ', '.join(allowed_domains)}
            )
    
    @staticmethod
    def validate_email_format(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError(_('Invalid email format.'))


class PasswordValidator:
    """Enhanced password validation"""
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password strength"""
        if len(password) < 8:
            raise ValidationError(_('Password must be at least 8 characters long.'))
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError(_('Password must contain at least one uppercase letter.'))
        
        if not re.search(r'[a-z]', password):
            raise ValidationError(_('Password must contain at least one lowercase letter.'))
        
        if not re.search(r'\d', password):
            raise ValidationError(_('Password must contain at least one digit.'))
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(_('Password must contain at least one special character.'))


class BusinessLogicValidator:
    """Business logic validators"""
    
    @staticmethod
    def validate_stock_availability(product, quantity):
        """Validate stock availability"""
        if product.stock < quantity:
            raise ValidationError(
                _('Insufficient stock. Available: %(available)s, Requested: %(requested)s'),
                params={'available': product.stock, 'requested': quantity}
            )
    
    @staticmethod
    def validate_order_status_transition(current_status, new_status):
        """Validate order status transitions"""
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered'],
            'delivered': ['refunded'],
            'cancelled': [],
            'refunded': []
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise ValidationError(
                _('Invalid status transition from %(current)s to %(new)s'),
                params={'current': current_status, 'new': new_status}
            )
    
    @staticmethod
    def validate_price_range(price):
        """Validate price is within reasonable range"""
        if price < 0.01:
            raise ValidationError(_('Price must be at least $0.01'))
        if price > 999999.99:
            raise ValidationError(_('Price cannot exceed $999,999.99'))


class RecoveryQuestionValidator:
    """Recovery question validation"""
    
    COMMON_QUESTIONS = [
        "What is your mother's maiden name?",
        "What was the name of your first pet?",
        "What city were you born in?",
        "What was your first car?",
        "What is your favorite color?",
        "What was the name of your elementary school?",
        "What is your favorite movie?",
        "What was your childhood nickname?"
    ]
    
    @staticmethod
    def validate_recovery_question(question):
        """Validate recovery question format"""
        if len(question) < 10:
            raise ValidationError(_('Recovery question must be at least 10 characters long.'))
        
        if len(question) > 200:
            raise ValidationError(_('Recovery question cannot exceed 200 characters.'))
        
        # Check for common patterns
        if question.lower() in [q.lower() for q in RecoveryQuestionValidator.COMMON_QUESTIONS]:
            return True
        
        # Basic format validation
        if not question.endswith('?'):
            raise ValidationError(_('Recovery question must end with a question mark.'))
    
    @staticmethod
    def validate_recovery_answer(answer):
        """Validate recovery answer"""
        if len(answer) < 2:
            raise ValidationError(_('Recovery answer must be at least 2 characters long.'))
        
        if len(answer) > 100:
            raise ValidationError(_('Recovery answer cannot exceed 100 characters.'))
        
        # Check for common weak answers
        weak_answers = ['password', '123456', 'admin', 'test', 'user', 'guest']
        if answer.lower() in weak_answers:
            raise ValidationError(_('Recovery answer is too common. Please choose a more secure answer.'))

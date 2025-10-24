# Django REST Framework E-commerce final project





 Core E-Commerce Features
    Product Management – Full CRUD operations
    Order Management – Complete order lifecycle handling
    Order Items – Detailed item-level management
    User Management – Custom user model with extended fields

Authentication & Security
    JWT Authentication – Secure token-based login
    Email Verification – Code-based account verification
    Security Questions – Password recovery via preset questions
    Password Reset – Safe reset workflow
    User Profiles – Full profile management





finalproject/
├── api/
│   ├── models.py              # Database models
│   ├── serializers.py         # DRF serializers
│   ├── views.py              # API views
│   ├── urls.py               # URL routing
│   ├── auth_serializers.py   # Authentication serializers
│   ├── auth_views.py         # Authentication views
│   ├── filters.py            # Custom filters
│   ├── tests.py              # Comprehensive tests
│   └── management/
│       └── commands/
│           └── populate_db.py # Database population
├── drf_project/
│   ├── settings.py           # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── celery.py            # Celery configuration
│   └── wsgi.py              # WSGI configuration
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
└── requirements.txt        # Python dependencies


API Endpoints

Products
`GET /products/` - List products (with filtering, search, pagination)
`POST /products/` - Create product (Admin only)
`GET /products/<id>/` - Get product details
`PUT/PATCH /products/<id>/` - Update product (Admin only)
`DELETE /products/<id>/` - Delete product (Admin only)
`GET /products/info/` - Product statistics

Orders
`GET /orders/` - List all orders
`POST /orders/create/` - Create new order
`GET /orders/<uuid>/` - Get order details
`PUT/PATCH /orders/<uuid>/` - Update order
`DELETE /orders/<uuid>/` - Delete order
`GET /user-orders/` - Get user's orders

Order Items
`POST /orders/<uuid>/items/` - Add item to order
`GET /order-items/<id>/` - Get order item details
`PUT/PATCH /order-items/<id>/` - Update order item
`DELETE /order-items/<id>/` - Remove order item

Authentication
`POST /auth/register/` - User registration
`POST /auth/verify-email/` - Email verification
`POST /auth/resend-verification/` - Resend verification code
`POST /auth/password-reset-request/` - Request password reset
`POST /auth/password-reset-confirm/` - Confirm password reset
`GET /auth/profile/` - Get user profile
`POST /auth/change-password/` - Change password

JWT Authentication
`POST /api/token/` - Get JWT tokens
`POST /api/token/refresh/` - Refresh JWT tokens

Docker 


Quick Start

# Clone the repository
git clone <repository-url>
cd finalproject

# Build and run with Docker Compose
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Populate database with sample data
docker-compose exec web python manage.py populate_db
```







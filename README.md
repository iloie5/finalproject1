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



The project includes a custom management command to populate the database with sample data for testing and development purposes.

### Populate Database Command
```bash
# Using Docker
docker-compose exec web python manage.py populate_db

# Or locally (if not using Docker)
python manage.py populate_db
```

### What the populate_db command does:
- Creates sample products with various categories and prices
- Generates test users with different roles
- Creates sample orders with order items
- Sets up realistic test data for development and testing
- Includes products with different statuses (active, inactive)
- Creates orders with various states (pending, completed, cancelled)

### Sample Data Includes:
- **Products**: Electronics, Clothing, Books, Home & Garden items
- **Users**: Regular users and admin users
- **Orders**: Various order states and order items
- **Categories**: Product categories for better organization

This command is particularly useful for:
- Development and testing
- Demonstrating API functionality
- Setting up a development environment quickly
- Testing pagination, filtering, and search features
```

### Services
- **Web**: Django application (Port 8000)
- **Database**: PostgreSQL (Port 5432)
- **Redis**: Cache and message broker (Port 6379)

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run specific test classes
docker-compose exec web python manage.py test api.tests.ProductTestCase
docker-compose exec web python manage.py test api.tests.AuthenticationTestCase
```

## 📊 API Documentation

Access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/

## 🔧 Configuration

### Environment Variables
Update the following in `drf_project/settings.py`:
- `EMAIL_HOST_USER`: Your email address
- `EMAIL_HOST_PASSWORD`: Your email app password
- `DEFAULT_FROM_EMAIL`: Your email address

### Database Configuration
The project is configured to use PostgreSQL. Update database settings in `settings.py` if needed.

## 🚀 Deployment

### Production Considerations
1. Set `DEBUG = False` in production
2. Use environment variables for sensitive data
3. Configure proper email settings
4. Set up SSL certificates
5. Use production database
6. Configure proper logging

### Environment Variables for Production
```bash
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@host:port/dbname
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-app-password
REDIS_URL=redis://host:port/0
```

## 📈 Performance Features

- **Pagination**: Efficient data pagination
- **Filtering**: Advanced product filtering
- **Caching**: Redis-based caching
- **Background Tasks**: Celery for async operations
- **Database Optimization**: Proper indexing and queries
- **API Documentation**: Auto-generated documentation

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Email Verification**: Required email verification
- **Recovery Questions**: Security question-based recovery
- **Password Validation**: Strong password requirements
- **Permission System**: Role-based access control
- **Input Validation**: Comprehensive data validation

## 📝 CRUD Operations Summary

### ✅ Complete CRUD Operations
- **Products**: Create, Read, Update, Delete
- **Orders**: Create, Read, Update, Delete
- **Order Items**: Create, Read, Update, Delete
- **Users**: Registration, Profile management, Password changes

### 🔐 Authentication Flow
1. User registration with email verification
2. Email verification with 6-digit code
3. JWT token authentication
4. Password recovery using security questions
5. Secure password reset process

## 🎯 Use Cases

This API is perfect for:
- E-commerce applications
- Learning Django REST Framework
- Understanding JWT authentication
- Email verification systems
- Password recovery mechanisms
- API documentation with Swagger
- Docker containerization
- Comprehensive testing strategies

## 📚 Learning Resources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)


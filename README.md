# Django REST Framework E-commerce final project





Core E-Commerce Features
 1.Product Management – Full CRUD operations
 2.Order Management – Complete order lifecycle handling
 3.Order Items – Detailed item-level management
 4.User Management – Custom user model with extended fields

Authentication & Security
  1.JWT Authentication – Secure token-based login
  2.Email Verification – Code-based account verification
  3.Security Questions – Password recovery via preset questions
  4.Password Reset – Safe reset workflow
  5.User Profiles – Full profile management








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







# 🍽️ Restaurant API (Django REST Framework)

A scalable **REST API built with Django and Django REST Framework** for managing a restaurant system, including menu items, shopping cart, orders, and role-based access control (RBAC).

The system supports three types of users: **customers, managers, and delivery crew**, with strict permissions and workflow separation.

---

## 📌 Key Features

### 👤 User Management
- User registration
- Retrieve authenticated user profile (`/users/me/`)
- Admin/manager can list all users

### 🍔 Menu Management
- Full CRUD for menu items (manager-only write access)
- Filtering by category and featured flag
- Search by title and category
- Ordering by price and category
- Pagination support for large datasets

### 🛒 Cart System
- Add items to cart
- View current user's cart
- Clear cart
- Automatic price calculation (unit price × quantity)

### 📦 Order System
- Create order from cart (transaction-safe)
- Role-based order visibility
- Order lifecycle management
- Managers can fully manage orders
- Delivery crew can update order status only

### 👥 Role-Based Access (Groups)
- `manager`
- `delivery-crew`
- Add/remove users from groups via API

---

## 🔐 Authentication & Permissions

The API uses **Django authentication + custom permission classes**:

- `IsAuthenticated` — required for protected endpoints
- `isManagerOnly` — restricts access to managers only
- `isManagerOrReadOnly` — read for all, write for managers only
- Delivery crew restrictions for status updates only

---

## 🧭 API Endpoints

### 👤 Users
```text
POST   /users/          → Register user
GET    /users/me/       → Get current user
GET    /showusers/      → List all users
```

---

### 🍔 Menu Items
```text
GET    /menu-items/        → List menu items
POST   /menu-items/        → Create item (manager only)
GET    /menu-items/<id>/   → Retrieve item
PUT    /menu-items/<id>/   → Update item (manager only)
DELETE /menu-items/<id>/   → Delete item (manager only)
```

---

### 👥 Groups (Role Management)
```text
GET    /groups/<group>/users/        → List users in group
POST   /groups/<group>/users/        → Add user to group
DELETE /groups/<group>/users/<id>/   → Remove user from group
```

---

### 🛒 Cart
```text
GET    /cart/menu-items/   → View cart items
POST   /cart/menu-items/   → Add item to cart
DELETE /cart/menu-items/   → Clear cart
```

---

### 📦 Orders
```text
GET    /orders/        → List orders (role-based)
POST   /orders/        → Create order from cart
GET    /orders/<id>/   → Order details
PUT    /orders/<id>/   → Full update (manager only)
PATCH  /orders/<id>/   → Partial update
DELETE /orders/<id>/   → Delete order (manager only)
```

---

## 🔎 Filtering, Searching & Ordering

### 🍔 Menu Items
- Filter: `category`, `featured`
- Search: `title`, `category__title`
- Ordering: `price`, `category`

### 📦 Orders
- Filter: `status`, `user`, `delivery_crew`, `date`
- Search: `user__username`, `order_items__menuitem__title`
- Ordering: `total`, `date`, `status`

---

## ⚙️ Transactions & Data Integrity

Order creation is fully **atomic**:

- Order is created
- Cart items are converted into order items
- Cart is cleared
- Ensures consistency using `transaction.atomic()`

---

## 🧠 Role Permissions

| Role           | Permissions |
|----------------|-------------|
| Customer       | Browse menu, manage cart, create orders |
| Manager        | Full access to menu, users, and orders |
| Delivery Crew  | Update order delivery status only |

---

## 🚀 Installation & Setup

```bash
# Clone repository
git clone <repo-url>
cd <project-folder>

# Create virtual environment (Pipenv)
pipenv install
pipenv shell

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

---

## 📦 Tech Stack

- Django
- Django REST Framework
- Django Filters
- SQLite / PostgreSQL
- Authentication (Session / Token-based)
- Django Groups (RBAC implementation)

---

## 🧱 Architecture Notes

- Class-based views (DRF generics + APIView)
- Custom permissions layer
- Role-based queryset filtering
- Atomic transactions for order creation
- Modular serializers for different roles (e.g. manager vs user)

---

## 🚀 Highlights

- Clean role-based architecture (RBAC)
- Secure transaction handling for orders
- Scalable filtering/search system
- Production-ready DRF structure

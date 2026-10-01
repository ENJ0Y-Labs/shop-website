# AGENT.md

## Project Identity

* Repository: `shop-website`
* Product/brand: `enj0y-solution`
* Project type: E-commerce shop website
* Primary purpose: HNG 15 Lesson 2 submission
* Long-term purpose: Continue development after HNG
* UI requirement: Fully responsive across desktop, tablet, and mobile
* Product category: Determined by the product data/database rather than hardcoded project assumptions

The project must be built as a functional e-commerce MVP, not merely a static frontend demonstration.

---

## Core Requirement

The application must allow a visitor to:

1. Browse products without authentication.
2. Search, filter, sort, and inspect products.
3. Add products to a cart.
4. Modify or remove cart items.
5. Authenticate using Google OAuth or email/password.
6. Continue browsing or proceed to checkout after authentication.
7. Complete a checkout form.
8. Create an order.
9. Persist the order and its items in PostgreSQL.
10. Send an order-confirmation email through Mailgun.
11. View the resulting order.
12. View previous orders through order history.

The primary Lesson 2 flow is:

```text
Browse
  ↓
Product
  ↓
Cart
  ↓
Authentication
  ↓
Checkout
  ↓
Create Order
  ↓
Persist in Database
  ↓
Send Mailgun Confirmation
  ↓
Order Confirmation
```

No real payment gateway is required for the HNG Lesson 2 MVP.

---

## Technology Stack

### Frontend

* React
* Vite
* JavaScript
* Plain CSS
* Global stylesheet: `global.css`
* Font Awesome

Do not introduce Tailwind, CSS-in-JS, or another styling framework unless explicitly requested.

### Backend

* Python
* Flask
* SQLAlchemy
* PostgreSQL
* Server-side sessions

### Database

* Supabase PostgreSQL

Supabase is used as the PostgreSQL database provider. Do not treat Supabase as the application's business-logic layer.

Database access must go through the Flask backend.

### Authentication

Support:

* Google OAuth
* Email/password authentication
* Server-side sessions

Google and email/password accounts using the same verified email address must resolve to the same user account rather than creating duplicate accounts.

### Email

* Mailgun API

Mailgun credentials must remain server-side and must never be exposed to the frontend.

### Storage

* Supabase Storage for product images

---

## Architecture

Use a clear separation between frontend, backend, database, and third-party services.

```text
React/Vite
    │
    │ HTTP/JSON
    ▼
Flask API
    │
    ├── Authentication
    ├── Products
    ├── Cart
    ├── Checkout
    └── Orders
    │
    ▼
SQLAlchemy
    │
    ▼
Supabase PostgreSQL

Flask
    │
    └── Mailgun API
             │
             ▼
      Confirmation Email

Flask
    │
    └── Google OAuth
```

The frontend must never connect directly to PostgreSQL.

The frontend must never contain database credentials, Mailgun credentials, OAuth client secrets, or other private secrets.

---

## Backend Structure

Prefer a modular Flask structure similar to:

```text
backend/
├── app/
│   ├── __init__.py
│   ├── config/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   └── ...
├── tests/
├── migrations/
└── ...
```

Use:

* `models/` for database models
* `routes/` for HTTP/API endpoints
* `services/` for business logic and third-party integrations
* `config/` for configuration
* `utils/` for reusable helpers

Do not put substantial business logic directly inside route handlers.

---

## Frontend Structure

Prefer a structure that keeps UI, API access, and reusable components separate.

Example:

```text
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── context/
│   ├── services/
│   ├── hooks/
│   ├── utils/
│   ├── App.jsx
│   ├── main.jsx
│   └── global.css
└── ...
```

Avoid unnecessary abstraction. Components should be created when they represent meaningful reusable UI or behavior.

---

## Database Models

The initial database should support:

```text
User
Product
Cart
CartItem
Order
OrderItem
```

### User

Recommended fields:

```text
id
email
password_hash
name
google_id
profile_picture_url
created_at
updated_at
```

Passwords must only be stored as secure password hashes.

Never store plaintext passwords.

### Product

Recommended fields:

```text
id
name
description
price
image_url
category
stock
created_at
updated_at
```

Products may support variants such as:

* size
* color

The implementation should not force every product to have variants.

### Cart

A cart belongs to a user.

Unauthenticated users may maintain a temporary browser cart.

When an unauthenticated user authenticates, their existing cart should be preserved and merged into their account cart where appropriate.

### CartItem

Recommended fields:

```text
id
cart_id
product_id
quantity
```

The backend must validate product availability and quantity.

### Order

Recommended fields:

```text
id
user_id
order_number
total_amount
status
created_at
updated_at
```

Suggested initial order statuses:

```text
pending
confirmed
cancelled
```

Because real payment processing is outside the HNG MVP, placing an order can move it to `confirmed` after successful validation and database creation.

### OrderItem

Recommended fields:

```text
id
order_id
product_id
product_name
quantity
unit_price
subtotal
```

`product_name` and `unit_price` must be stored at purchase time.

Historical orders must not change merely because a product's current name or price changes.

---

## Money Handling

Do not use floating-point numbers for monetary calculations.

Prefer integer minor units.

For Nigerian Naira:

```text
₦1,500
=
150000 kobo
```

The backend must perform monetary calculations consistently.

The frontend may format the stored value for display.

---

## Product Variants

Products may have variants such as size or color.

Variant information must be validated on the backend.

The frontend must not assume every product has the same variant structure.

---

## Product Discovery

The shop should support:

* Product listing
* Product details
* Search
* Category filtering
* Sorting
* Stock visibility

Sorting should support sensible options such as:

* Name
* Price ascending
* Price descending

Do not build an unnecessarily complex search engine for the MVP.

---

## Cart

Users must be able to:

* Add items
* Increase quantity
* Decrease quantity
* Remove items
* Clear the cart
* Continue shopping
* Proceed to checkout

Cart data should be persisted in both:

* Browser storage for unauthenticated visitors
* Database for authenticated users

The browser cart must not be treated as trusted data.

The backend must recalculate prices and validate products during checkout.

---

## Checkout

Checkout should collect the information required to fulfill an order, including:

```text
Full name
Email
Phone number
Address
City
State
Country
```

The backend must validate checkout data.

The client must never be trusted to determine:

* Final price
* Product availability
* Order ownership
* Order total

The backend must calculate the final order total using current validated product data.

---

## Authentication

Supported methods:

```text
Google OAuth
Email/password
```

Unauthenticated users can browse products.

Authentication is required for placing an order.

Users must be able to log out.

Provide:

```text
GET /api/auth/me
```

to determine the current authenticated user.

Use server-side sessions.

Authentication cookies should be configured securely, particularly in production.

---

## Google OAuth

Google OAuth must be implemented through Google Cloud Console.

The OAuth callback must be validated correctly.

OAuth credentials and client secrets must never be committed.

If a Google account uses an email address that already belongs to an existing email/password account, the system should associate the Google identity with the existing account instead of creating a duplicate user.

Do not create duplicate users merely because authentication methods differ.

---

## API Conventions

Use an `/api/` prefix.

Example endpoints:

```text
GET    /api/products
GET    /api/products/:id

GET    /api/cart
POST   /api/cart/items
PATCH  /api/cart/items/:id
DELETE /api/cart/items/:id
DELETE /api/cart

POST   /api/orders
GET    /api/orders
GET    /api/orders/:id

POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me

GET    /api/auth/google
GET    /api/auth/google/callback
```

The exact endpoint structure may be adjusted when implementation requires it, but changes should remain consistent with REST conventions.

---

## Authorization

Every protected resource must verify ownership.

A user must never be able to:

* Read another user's cart
* Modify another user's cart
* Read another user's order
* Modify another user's order
* Manipulate another user's account

Never trust a `user_id` supplied by the frontend to determine ownership.

The authenticated server-side session determines the current user.

---

## Validation

Frontend validation improves user experience.

Backend validation provides security and correctness.

Both should be used.

The backend must independently validate:

* Required fields
* Data types
* Product IDs
* Quantities
* Stock
* Prices
* Authentication
* Authorization
* Checkout information

Never assume frontend validation has already occurred.

---

## Order Creation

Order creation must be handled transactionally.

The backend should:

1. Verify authentication.
2. Retrieve the user's cart.
3. Verify every product.
4. Verify quantities.
5. Verify stock.
6. Determine current trusted prices.
7. Calculate totals.
8. Create the order.
9. Create order items using purchase-time product information.
10. Update inventory where applicable.
11. Clear the user's cart.
12. Commit the transaction.
13. Send the confirmation email.

Do not rely on frontend totals.

If an order cannot be completed safely, the transaction should not leave partial order data behind.

---

## Inventory

Stock should be tracked on products.

The system should prevent customers from ordering more units than are available.

Successful orders should reduce available stock.

Inventory operations must be performed by the backend.

---

## Order History

Authenticated users should have an order-history page.

Users may only view their own orders.

An individual order page should display:

```text
Order number
Order date
Status
Products
Quantities
Unit prices
Subtotal
Total
Customer information
```

---

## Email Confirmation

After a successful order, send a confirmation email through Mailgun.

The email should contain:

```text
Order number
Customer name
Order date
Products
Quantity
Unit price
Subtotal
Total
Order status
```

Mailgun API credentials must only exist on the backend.

Email failures must be handled gracefully and logged appropriately.

An email failure must not expose Mailgun credentials or internal errors to the customer.

---

## UI and Branding

Brand:

```text
enj0y-solution
```

Primary visual direction:

```text
Black + Orange
```

The interface should be:

* Clean
* Modern
* Professional
* Responsive
* Easy to navigate

Use the global stylesheet:

```text
global.css
```

Do not introduce a CSS framework unless explicitly approved.

Use Font Awesome for icons.

Do not use icons merely for decoration when ordinary text would be clearer.

---

## Required Pages

Initial page structure:

```text
/
    Shop

/products/:id
    Product details

/cart
    Cart

/checkout
    Checkout

/order/:id
    Order confirmation

/orders
    Order history

/login
    Login

/register
    Registration
```

Additional pages may be introduced when they provide clear product value.

---

## Product Images

Product images should use Supabase Storage.

Do not hardcode large image files into the frontend repository.

Image URLs should be stored in the database where appropriate.

---

## Error Handling

The application must provide useful user-facing errors.

Do not expose:

* Stack traces
* Database errors
* Secret values
* Internal implementation details
* Authentication credentials

Production errors should be logged server-side while returning safe messages to the client.

---

## Environment Variables

Secrets must never be committed to Git.

Examples include:

```text
DATABASE_URL
SECRET_KEY
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
MAILGUN_API_KEY
MAILGUN_DOMAIN
MAILGUN_FROM_EMAIL
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

Never expose server-only secrets through frontend environment variables.

Never commit `.env` files containing secrets.

Provide a safe `.env.example` when appropriate.

---

## Security

The backend is the authority.

Implement:

* Secure password hashing
* Server-side sessions
* Secure cookies in production
* Appropriate SameSite configuration
* CORS restricted to known frontend origins
* OAuth state/CSRF protection
* Input validation
* Authorization checks
* Safe error responses
* Secret management through environment variables

Do not weaken security merely to make development easier.

Development shortcuts must not become production behavior.

---

## Testing

Use `pytest` for backend tests.

Important test areas include:

```text
Authentication
Registration
Login
Google OAuth behavior
Logout
Current-user endpoint

Products
Product retrieval
Invalid product IDs

Cart
Add item
Update quantity
Remove item
Clear cart
Authorization

Checkout
Validation
Stock validation
Price calculation
Order creation
Order ownership

Orders
Order history
Individual order access
Authorization

Email
Mailgun integration behavior
```

Tests should focus particularly on business rules and authorization.

Run relevant tests after meaningful backend changes.

---

## Git Rules

Use:

```text
main
```

as the stable branch.

Use feature branches for significant feature development.

Prefer conventional commit messages:

```text
feat: add checkout flow
fix: validate cart ownership
docs: update setup instructions
test: add order authorization tests
refactor: separate mail service
```

AI agents may modify project files when explicitly tasked to implement a feature.

AI agents must not push or commit changes unless explicitly instructed.

---

## AGENT.md Rules

`AGENT.md` is project-level instruction.

AI agents must:

1. Read `AGENT.md` before making project changes.
2. Follow its architectural and security requirements.
3. Inspect existing code before modifying it.
4. Prefer the smallest correct change.
5. Avoid unnecessary rewrites.
6. Preserve working behavior.
7. Run relevant tests after changes.
8. Explain important architectural decisions before implementing them when the decision materially affects the system.
9. Ask before destructive changes.
10. Ask before major dependency changes.
11. Ask before architecture changes.
12. Ask before database schema changes.
13. Never expose secrets.
14. Never modify `AGENT.md` unless explicitly instructed to do so.

Do not create abstractions merely because they appear sophisticated.

Prefer simple, maintainable solutions.

---

## Scope Control

The following are explicitly outside the HNG Lesson 2 MVP:

* Real payment gateway
* Admin dashboard
* Product management dashboard
* Coupons
* Reviews
* Wishlist
* Shipping API integration
* SMS notifications
* Refund system

These may be considered after the HNG submission.

The existence of a future feature must not complicate the current MVP unnecessarily.

---

## Deployment

Target deployment:

```text
Frontend
    ↓
Vercel

Backend
    ↓
Render

Database
    ↓
Supabase PostgreSQL

Email
    ↓
Mailgun
```

Production configuration must use environment variables.

Deployment-specific configuration must not be hardcoded into application logic.

---

## Development Priorities

When choosing between implementation options, prioritize:

1. Correctness
2. Security
3. Simplicity
4. Maintainability
5. HNG requirements
6. Performance optimization

Do not prematurely optimize.

Do not add infrastructure that the current requirements do not justify.

---

## Definition of Done

The HNG Lesson 2 MVP is considered complete when:

> A visitor can browse products, search/filter/sort them, add products to a persistent cart, authenticate with Google or email/password, complete checkout, have the order and order items persisted in Supabase PostgreSQL, have inventory updated, and receive a Mailgun confirmation email while being able to view the resulting order and their order history.

The project must work as an integrated system rather than as disconnected demonstrations of individual technologies.

---

## Post-HNG Direction

The project is intended to continue after HNG.

Future features must be added incrementally.

Do not prematurely implement post-HNG features.

The HNG MVP should establish a clean foundation that can later support:

* Better inventory management
* Real payment processing
* Admin functionality
* More advanced product management
* Customer accounts
* Shipping
* Reviews
* Wishlist
* Analytics
* Additional notification channels

Future extensibility should be considered during design, but future features should not be implemented unless explicitly requested.
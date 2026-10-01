# enJOY Solution

A full-stack shop website built for the **HNG15 Lesson 2 Individual Task**.

## HNG15 Lesson 2

> Build a website for a shop. Add a check-out page. Persist everything in a database using Supabase/Neon. Send confirmation emails using Mailgun. Do Google auth using Google Cloud Console.

## Project Goal

enJOY Solution is a responsive e-commerce website where visitors can browse products, search and filter the catalogue, manage a shopping cart, authenticate with email/password or Google, and place orders through a checkout flow.

The project is being developed beyond the HNG15 task as a foundation for a more complete shop application.

## Planned Features

- Product catalogue
- Product details
- Product search
- Category filtering
- Product sorting
- Product variants such as size and color where applicable
- Persistent shopping cart
- Local cart for visitors
- Cart synchronization after login
- Email/password authentication
- Google OAuth authentication
- Server-side sessions
- Protected checkout
- Order creation and confirmation
- Inventory/stock validation
- Automatic stock reduction after successful orders
- Order history
- Individual order details
- Order confirmation emails through Mailgun
- Responsive design for desktop and mobile

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- Plain CSS
- Font Awesome

### Backend

- Python
- Flask
- SQLAlchemy
- REST API
- Server-side sessions

### Database and Storage

- Supabase PostgreSQL
- Supabase Storage

### Authentication

- Email/password
- Google OAuth
- Google Cloud Console

### Email

- Mailgun API

### Deployment

- Frontend: Vercel
- Backend: Render
- Database: Supabase
- Email: Mailgun

## Planned Architecture

```
React + Vite
     |
     | HTTPS / REST API
     v
Flask Backend
     |
     +------ SQLAlchemy ------> Supabase PostgreSQL
     |
     +------------------------> Supabase Storage
     |
     +------------------------> Google OAuth
     |
     +------------------------> Mailgun
```

## Main Pages

| Route | Purpose |
|---|---|
| `/` | Product catalogue |
| `/products/:id` | Product details |
| `/cart` | Shopping cart |
| `/checkout` | Checkout |
| `/order/:id` | Order confirmation |
| `/orders` | Order history |
| `/login` | Login |
| `/register` | Registration |

## Core Database Models

The planned database consists of:

- **User** - customer account and authentication information
- **Product** - product catalogue and inventory
- **Cart** - authenticated user's persistent cart
- **CartItem** - products and quantities in a cart
- **Order** - customer order and checkout information
- **OrderItem** - products purchased, quantities, and price snapshots

Product prices used during checkout will be calculated and validated by the backend rather than trusted from the browser.

## Checkout Flow

The checkout process will:

1. Require an authenticated user.
2. Load the user's current cart.
3. Validate the products and requested quantities.
4. Verify available stock.
5. Use current database prices.
6. Calculate the order total on the backend.
7. Create the order and order items.
8. Reduce product inventory.
9. Clear the cart.
10. Commit the database transaction.
11. Send a confirmation email through Mailgun.

There is **no real payment gateway** in the HNG15 Lesson 2 scope. Checkout creates and confirms an order without processing a real payment.

## Authentication

Users will be able to:

- Register with email and password
- Log in with email and password
- Log in with Google
- Log out
- Maintain a server-side authenticated session

If Google authentication and email/password authentication use the same verified email address, they will be linked to the same customer account.

## Environment Variables

Secrets must never be committed to the repository.

The backend will require environment variables similar to:

```env
DATABASE_URL=
SECRET_KEY=

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

MAILGUN_API_KEY=
MAILGUN_DOMAIN=
MAILGUN_FROM_EMAIL=

SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

The exact variables used by the implementation will be documented as development progresses.

## Local Development

The project will contain separate frontend and backend applications.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

Start the Flask development server using the backend's configured entry point.

> Local setup instructions will be updated with the final commands once the project structure and application entry points are implemented.

## Testing

Backend tests will use **pytest**.

Important areas to test include:

- Registration
- Duplicate email handling
- Login/logout
- Google authentication flow
- Product access
- Cart operations
- Cart merging
- Checkout validation
- Stock validation
- Order creation
- Inventory updates
- Order ownership/authorization
- API error handling

## Security Requirements

- Passwords must be securely hashed.
- Authentication must use server-side sessions.
- Production cookies must be configured securely.
- CORS must be restricted to trusted frontend origins.
- OAuth state/CSRF protection must be implemented.
- Backend validation must not rely on frontend validation.
- Users must only access their own carts and orders.
- Secrets must be stored in environment variables.
- Sensitive credentials must never be committed to Git.

## HNG15 Scope

The following are intentionally outside the Lesson 2 implementation scope:

- Real payment processing
- Admin dashboard
- Product management dashboard
- Coupons
- Reviews
- Wishlist
- Shipping API integration
- SMS notifications
- Refund processing

These may be considered for future development.

## Development Approach

Development will proceed incrementally:

```
Repository setup
      ↓
Project structure
      ↓
Database
      ↓
Backend API
      ↓
Authentication
      ↓
Products
      ↓
Cart
      ↓
Checkout
      ↓
Mailgun
      ↓
Frontend integration
      ↓
Testing
      ↓
Deployment
      ↓
Production verification
```

Each major feature should be tested before dependent features are built.

## Deployment

The target production architecture is:

```
Vercel
  |
  v
React Frontend
  |
  v
Render
  |
  v
Flask API
  |
  +----> Supabase PostgreSQL
  |
  +----> Supabase Storage
  |
  +----> Mailgun
```

Google OAuth will also be configured for the production frontend/backend domains through Google Cloud Console.

## Status

**Current status:** Project setup / planning

The repository currently contains the initial project files. Application development will follow the implementation plan above.

## Repository

[GitHub Repository](https://github.com/ENJ0Y-Labs/shop-website)

---

Built for HNG15 Lesson 2 by **enJOY Solution**.

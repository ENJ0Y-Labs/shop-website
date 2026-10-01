# Production Configuration

This checklist covers the production configuration required before deploying **enj0y Solution**.

## 1. Frontend environment

Set this on the frontend deployment:

```env
VITE_API_URL=https://api.example.com/api
```

Use the actual HTTPS URL of the deployed Flask API. The value must include `/api`.

Do not put backend secrets in Vite variables. Anything prefixed with `VITE_` is exposed to the browser.

## 2. Backend environment

Set these on the backend deployment:

```env
APP_ENV=production

DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require
SECRET_KEY=<long-random-secret>

CORS_ORIGINS=https://shop.example.com

SESSION_TYPE=filesystem
SESSION_COOKIE_SAMESITE=None
SESSION_COOKIE_SECURE=true

GOOGLE_CLIENT_ID=<google-client-id>
GOOGLE_CLIENT_SECRET=<google-client-secret>
GOOGLE_REDIRECT_URI=https://api.example.com/api/auth/google/callback

SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_STORAGE_BUCKET=product-images
SUPABASE_SERVICE_ROLE_KEY=<server-only-key>

MAILGUN_API_KEY=<mailgun-api-key>
MAILGUN_DOMAIN=<verified-mailgun-domain>
MAILGUN_FROM_EMAIL=enj0y Solution <orders@your-domain.example>
MAILGUN_API_BASE_URL=https://api.mailgun.net
MAILGUN_TIMEOUT=10
```

Replace every placeholder with the real deployment value. Never commit these values.

For Mailgun EU domains, use:

```env
MAILGUN_API_BASE_URL=https://api.eu.mailgun.net
```

## 3. Production CORS

Set `CORS_ORIGINS` to the exact frontend origin, for example:

```env
CORS_ORIGINS=https://shop.example.com
```

Do not use `*` because the application uses credentialed requests and session cookies.

If the frontend is deployed at a Vercel URL, use that exact URL instead.

## 4. Secure session cookies

Production must use:

```env
APP_ENV=production
SESSION_COOKIE_SAMESITE=None
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
```

`SESSION_COOKIE_HTTPONLY=true` is enforced by the backend configuration and prevents JavaScript from reading the session cookie.

Because the frontend and backend normally have different production origins, `SameSite=None` is required for the browser to send the session cookie cross-site. `Secure=true` requires HTTPS.

The current Flask-Session filesystem backend is intended for the HNG deployment's single-instance setup. If the backend is later scaled across multiple instances, move server-side sessions to a shared store such as Redis.

## 5. HTTPS

HTTPS is provided by the deployment platform for the public frontend and backend.

Production URLs must therefore be:

```text
Frontend: https://<frontend-domain>
Backend:  https://<backend-domain>
```

Do not configure `http://` production URLs in CORS, Google OAuth, Mailgun callbacks, or `VITE_API_URL`.

## 6. Google OAuth

In Google Cloud Console, add this exact production callback under the OAuth client's authorized redirect URIs:

```text
https://<backend-domain>/api/auth/google/callback
```

The backend `GOOGLE_REDIRECT_URI` must contain the same URL character-for-character.

The frontend origin is configured separately through `CORS_ORIGINS`.

## 7. Mailgun

Before production email testing:

1. Verify the production sending domain in Mailgun.
2. Configure the required DNS records at the domain provider.
3. Set `MAILGUN_DOMAIN` to the verified Mailgun domain.
4. Set `MAILGUN_FROM_EMAIL` to an address allowed by that domain.
5. Use the correct Mailgun API region.

The order is committed before Mailgun delivery is attempted, so a Mailgun outage does not roll back the order.

## 8. Supabase database

Copy the PostgreSQL connection string from Supabase's **Connect** panel.

Use the exact host supplied by Supabase. Do not manually construct or guess the pooler hostname.

The connection string should use SSL, for example:

```text
postgresql+psycopg://...?...sslmode=require
```

Run migrations against the production database before serving traffic:

```powershell
flask --app backend.run db upgrade
python -m backend.seed
```

Only run the seed command if the deployment is intended to contain the project's initial demo products.

Then verify:

```text
GET /api/health
GET /api/health/db
```

The database health endpoint should return:

```json
{"status":"ok","database":"connected"}
```

## 9. Backend tests

From the repository root:

```powershell
python -m pytest backend/tests -q
```

The suite covers authentication, Google OAuth behavior, products, carts, checkout, inventory, orders, email invocation, and authorization.

## 10. Frontend tests and build

From the frontend directory:

```powershell
npm test
npm run build
```

The build should complete successfully and produce the `frontend/dist` directory.

For a production build, make sure the deployment environment contains:

```env
VITE_API_URL=https://<backend-domain>/api
```

Vite injects environment variables at build time. Changing `VITE_API_URL` after the build does not change an already-generated frontend bundle.

## Final production verification

Before opening the site to users, verify this path manually:

1. Open the HTTPS frontend.
2. Browse products.
3. Register or sign in.
4. Confirm the session survives a page refresh.
5. Test Google sign-in.
6. Add an item as a visitor, sign in, and confirm the cart merges.
7. Complete checkout.
8. Confirm inventory decreases.
9. Confirm the order appears in history and detail views.
10. Confirm the Mailgun confirmation arrives.
11. Sign in as another user and confirm the first user's order cannot be read.

Humanity invented twelve different ways to misconfigure an environment variable, so this verification step exists for a reason.

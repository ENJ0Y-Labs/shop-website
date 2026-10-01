# Phase 11: Deployment

Target architecture:

```text
Vercel React/Vite
      |
     HTTPS
      v
Render Flask API
   |          |
   v          v
Supabase    Mailgun
PostgreSQL  Email API
```

## 1. Render backend

The repository includes `render.yaml` for the backend service.

Create a Render Web Service from the GitHub repository:

- Repository: `ENJ0Y-Labs/shop-website`
- Root directory: `backend`
- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn run:app`
- Health check: `/api/health`

If Render reads `render.yaml`, these values can be supplied from the Blueprint instead.

### Environment variables

Set these in Render. Never commit the actual values:

```text
APP_ENV=production
DATABASE_URL=postgresql+psycopg://...?...sslmode=require
SECRET_KEY=<long-random-secret>
CORS_ORIGINS=https://<your-vercel-domain>
SESSION_TYPE=filesystem
SESSION_COOKIE_SAMESITE=None
SESSION_COOKIE_SECURE=true

GOOGLE_CLIENT_ID=<google-client-id>
GOOGLE_CLIENT_SECRET=<google-client-secret>
GOOGLE_REDIRECT_URI=https://<your-render-domain>/api/auth/google/callback

SUPABASE_URL=<supabase-project-url>
SUPABASE_STORAGE_BUCKET=product-images

MAILGUN_API_KEY=<mailgun-api-key>
MAILGUN_DOMAIN=<verified-mailgun-domain>
MAILGUN_FROM_EMAIL=<verified-from-address>
MAILGUN_API_BASE_URL=https://api.mailgun.net
MAILGUN_TIMEOUT=10
```

Use `https://api.eu.mailgun.net` instead when the Mailgun domain is hosted in the EU region.

Do not set `CORS_ORIGINS` to `*`. It must contain the exact Vercel browser origin, without a trailing slash.

## 2. Database migration

After the Render service has access to the production `DATABASE_URL`, run:

```powershell
flask --app run db upgrade
```

Run this from the Render service's `backend` root.

Then seed the initial products only if the production database is empty:

```powershell
python -m seed
```

Do not repeatedly seed production after data has been created. The seed script is idempotent by product name, but production data should still be treated deliberately.

## 3. Render verification

Check:

```text
GET https://<your-render-domain>/api/health
GET https://<your-render-domain>/api/health/db
GET https://<your-render-domain>/api/products
GET https://<your-render-domain>/api/auth/me
```

Expected unauthenticated `/api/auth/me` behavior is a safe authentication response, not a server error.

Also inspect Render logs for startup, migration, database, CORS, session, and Mailgun errors.

## 4. Vercel frontend

Create a Vercel project from the same repository.

Set:

- Framework preset: Vite
- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`

Set the frontend environment variable:

```text
VITE_API_URL=https://<your-render-domain>/api
```

The `/api` suffix is required because the frontend service builds endpoint paths such as `/products` and `/auth/me` on top of this base URL.

The repository includes `frontend/vercel.json` so direct visits to client-side routes such as `/cart`, `/checkout`, and `/orders` fall back to `index.html`.

## 5. Google OAuth production callback

In Google Cloud Console, add this exact authorized redirect URI:

```text
https://<your-render-domain>/api/auth/google/callback
```

The value must exactly match Render's `GOOGLE_REDIRECT_URI`.

Do not use the Vercel URL as the OAuth callback because Google OAuth is handled by Flask.

## 6. CORS and cookies

The browser talks from Vercel to Render, so production is cross-site.

Use:

```text
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=None
SESSION_COOKIE_SECURE=true
```

`SESSION_COOKIE_HTTPONLY` is already enabled by the Flask configuration.

The frontend requests use `credentials: "include"`, and Flask-CORS is configured with credentials support.

## 7. Mailgun

Use a verified production Mailgun sending domain and verified sender address.

Confirm DNS/domain verification in Mailgun before testing order confirmation emails.

A Mailgun failure must not delete an already committed order. The current backend commits the order before attempting the confirmation email.

## 8. Final browser test

Run this sequence against the deployed URLs:

1. Open the Vercel site.
2. Browse products.
3. Search, filter, and sort.
4. Add an item while logged out.
5. Register or log in.
6. Confirm the visitor cart merges into the authenticated cart.
7. Complete checkout.
8. Confirm the order page loads.
9. Confirm stock decreased.
10. Confirm the order appears in order history.
11. Confirm the confirmation email arrives.
12. Log out.
13. Confirm protected pages require authentication.
14. Test Google login.
15. Test another user's order cannot be opened.

## Important production limitation

The current Flask-Session filesystem backend stores sessions on the Render instance's local filesystem. That is acceptable for a simple single-instance HNG deployment, but it is not durable across instance replacement and is not appropriate for multi-instance scaling.

Moving sessions to shared Redis/CacheLib should be treated as a separate infrastructure change, not silently mixed into this deployment.

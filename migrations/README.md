# Migrations

Run the migrations from the repository root:

```powershell
flask --app backend.run db upgrade
python -m backend.seed
```

For the current checkout schema, migration `0003_checkout_customer_details` adds the customer and shipping information required by the order flow.

## Phase 7: Mailgun

Mailgun is used only by the Flask backend. Never put Mailgun credentials in frontend environment variables.

Required backend environment variables:

```env
MAILGUN_API_KEY=
MAILGUN_DOMAIN=
MAILGUN_FROM_EMAIL=
MAILGUN_API_BASE_URL=https://api.mailgun.net
MAILGUN_TIMEOUT=10
```

For a Mailgun domain created in the EU region, use `https://api.eu.mailgun.net` as the API base URL.

The order endpoint commits the database transaction before attempting email delivery. If Mailgun fails, the order remains persisted and the failure is logged server-side.

## Phase 9: Integration testing

Backend integration tests:

```powershell
python -m pytest backend/tests -q
```

Frontend visitor-cart test:

```powershell
cd frontend
npm test
```

The Phase 9 backend suite covers registration, login/logout, mocked Google OAuth callback and email verification, product browsing/search/filter/sort, authenticated cart merge, checkout, current inventory, insufficient-stock atomicity, order history/details, Mailgun invocation, and cross-user order authorization.

The visitor cart test covers localStorage persistence, quantity updates, removal, clearing, and malformed stored data without requiring a browser test dependency.

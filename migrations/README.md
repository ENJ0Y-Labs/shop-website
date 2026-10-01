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

For a Mailgun domain created in the EU region, use `https://api.eu.mailgun.net` as the API base URL. Mailgun documents separate US and EU API base URLs. 

The order endpoint commits the database transaction before attempting email delivery. If Mailgun fails, the order remains persisted and the failure is logged server-side.

# Database migrations

This directory is managed by Flask-Migrate/Alembic.

Run migration commands from the repository root with:

```bash
flask --app backend.run db upgrade
```

Seed the development products after the migration:

```bash
python -m backend.seed
```

The database URL is read from `DATABASE_URL`. Never commit a real database URL or other credentials.

The current migration chain includes the checkout customer-information fields in migration `0003_checkout_customer_details`.

After pulling the Phase 6 branch, apply it with:

```bash
flask --app backend.run db upgrade
```

Then run the backend tests:

```bash
python -m pytest backend/tests -q
```

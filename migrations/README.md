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

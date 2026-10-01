# Database migrations

This directory is managed by Flask-Migrate/Alembic.

Run migration commands from the repository root with:

```bash
flask --app backend.run db upgrade
```

The database URL is read from `DATABASE_URL`. Never commit a real database URL or other credentials.

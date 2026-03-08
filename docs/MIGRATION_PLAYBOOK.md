# AutoPenTest AI — Migration Playbook

> **Day 206 · Phase K: Documentation**
> Database migrations, version upgrade procedures, rollback instructions, and
> a catalogue of breaking changes for every minor release.

---

## Table of Contents

1. [Migration Principles](#migration-principles)
2. [Database Migrations (Prisma)](#database-migrations-prisma)
3. [Version Upgrade Procedures](#version-upgrade-procedures)
4. [Rollback Procedures](#rollback-procedures)
5. [Breaking Changes Log](#breaking-changes-log)
6. [Data Migration Scripts](#data-migration-scripts)
7. [Zero-Downtime Migration Pattern](#zero-downtime-migration-pattern)

---

## Migration Principles

1. **Always backup before migrating** — run `pg_dump` before any schema change.
2. **Test in staging first** — never apply untested migrations to production.
3. **Migrations are forward-only** — write reversible migrations where possible, but
   treat rollback as an emergency procedure (restore backup) not a routine one.
4. **One concern per migration** — avoid combining schema changes with data transforms.
5. **Monitor after migration** — watch error rates for 30 minutes post-deploy.

---

## Database Migrations (Prisma)

AutoPenTest AI uses **Prisma Migrate** to manage the PostgreSQL schema.

### View pending migrations

```bash
cd backend
python -m prisma migrate status
```

### Apply all pending migrations (production)

```bash
python -m prisma migrate deploy
```

`migrate deploy` is non-interactive and safe for CI/CD pipelines.

### Create a new migration (development)

```bash
# Edit prisma/schema.prisma first, then:
python -m prisma migrate dev --name add_project_tags
```

This creates a timestamped SQL file under `backend/prisma/migrations/`.

### Inspect generated SQL before applying

```bash
python -m prisma migrate diff \
  --from-schema-datasource prisma/schema.prisma \
  --to-schema-datamodel prisma/schema.prisma \
  --script
```

### Reset the database (⚠️ destructive — dev/test only)

```bash
python -m prisma migrate reset --force
```

### Seed the database

```bash
python -m prisma db seed
```

The seed script is at `backend/prisma/seed.py`.

---

## Version Upgrade Procedures

### Patch release (e.g., 1.0.0 → 1.0.1)

Patch releases contain bug fixes only — no breaking changes, no schema changes.

```bash
git pull origin main
docker compose pull
docker compose up -d --no-deps backend frontend
```

### Minor release (e.g., 1.0.x → 1.1.0)

Minor releases may include new columns (additive schema changes) but no removed
or renamed columns.

```bash
# 1. Back up the database
docker compose exec postgres pg_dump -U autopentestai autopentestai > backup_pre_1.1.0.sql

# 2. Pull the new images
docker compose pull

# 3. Apply migrations (safe because additive)
docker compose exec backend python -m prisma migrate deploy

# 4. Rolling restart (zero-downtime if using blue-green)
docker compose up -d --no-deps backend frontend
```

### Major release (e.g., 1.x → 2.0.0)

Major releases may include breaking schema changes, renamed API fields, or removed
endpoints. Follow the [Zero-Downtime Migration Pattern](#zero-downtime-migration-pattern).

```bash
# 1. Review BREAKING CHANGES section of RELEASE_NOTES.md
cat RELEASE_NOTES.md | grep -A 50 "BREAKING"

# 2. Schedule a maintenance window
# 3. Full backup
docker compose exec postgres pg_dump -U autopentestai autopentestai \
  | gzip > backup_pre_v2.0.0_$(date +%Y%m%d_%H%M%S).sql.gz

# 4. Apply migrations
docker compose -f docker/production/docker-compose.production.yml exec backend \
  python -m prisma migrate deploy

# 5. Deploy new images
docker compose -f docker/production/docker-compose.production.yml \
  up -d --no-deps backend frontend

# 6. Verify
curl https://your-domain/health
```

---

## Rollback Procedures

### Option A: Restore from database backup (recommended)

Use when a migration has already been applied and data is potentially corrupt.

```bash
# 1. Stop the backend to prevent further writes
docker compose stop backend

# 2. Drop and recreate the database
docker compose exec postgres psql -U autopentestai -c "DROP DATABASE autopentestai;"
docker compose exec postgres psql -U autopentestai -c "CREATE DATABASE autopentestai;"

# 3. Restore backup
gunzip -c backup_pre_vX.Y.Z_20260101_120000.sql.gz \
  | docker compose exec -T postgres psql -U autopentestai autopentestai

# 4. Roll back the container image
docker compose up -d --no-deps backend frontend  # uses previous image tag

# 5. Verify
curl http://localhost:8000/health
```

### Option B: Reverse migration (additive changes only)

Prisma does not auto-generate reverse migrations, but you can manually craft one:

```bash
# Create a reverse migration file
cat > backend/prisma/migrations/rollback_YYYYMMDD_HHMMSS/migration.sql << 'EOF'
-- Reverse: drop the column added in the last migration
ALTER TABLE "Project" DROP COLUMN IF EXISTS "tags";
EOF

# Apply it
python -m prisma migrate resolve --applied "rollback_YYYYMMDD_HHMMSS"
```

### Option C: Blue-green rollback (zero-downtime)

If using the blue-green deployment workflow:

```bash
# Trigger rollback via GitHub Actions
gh workflow run blue-green.yml \
  -f action=rollback \
  -f environment=production
```

See [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md#blue-green-rollback) for details.

---

## Breaking Changes Log

### v1.0.0 (initial release)

No breaking changes — initial release.

### Planned for v1.1.0

| Area | Change | Migration Required |
|------|--------|--------------------|
| API | `/api/v1/scans` renamed to `/api/v1/recon` | Update client base URLs |
| Schema | `Project.config` JSONB column split into typed columns | Data migration script provided |
| Auth | Refresh token endpoint moved to `/api/v1/auth/refresh` | Update frontend fetch calls |

### API field renames (v1.0.x)

If you have external integrations, note these field renames from the internal
form schema to the API:

| Old Field Name | New Field Name | Endpoint |
|----------------|----------------|----------|
| `enable_auto_exploit` | `ai_auto_exploit` | `POST /api/v1/projects` |

---

## Data Migration Scripts

### Script: Backfill `ai_auto_exploit` from `enable_auto_exploit`

If upgrading from a version that used the old field name in the database:

```sql
-- backend/prisma/migrations/manual/backfill_ai_auto_exploit.sql
UPDATE "Project"
SET config = jsonb_set(
    config,
    '{ai_auto_exploit}',
    config->'enable_auto_exploit'
)
WHERE config ? 'enable_auto_exploit'
  AND NOT config ? 'ai_auto_exploit';

-- Remove old key after verifying the above
UPDATE "Project"
SET config = config - 'enable_auto_exploit'
WHERE config ? 'enable_auto_exploit';
```

Run with:

```bash
docker compose exec postgres psql -U autopentestai autopentestai \
  -f /docker-entrypoint-initdb.d/backfill_ai_auto_exploit.sql
```

### Script: Migrate Neo4j node labels

If updating the graph schema:

```cypher
// Rename node label (Neo4j does not support RENAME LABEL natively)
MATCH (n:OldLabel)
SET n:NewLabel
REMOVE n:OldLabel;
```

---

## Zero-Downtime Migration Pattern

For schema changes that cannot be applied while the application is running:

### Phase 1 — Expand (deploy new code, old + new schema both valid)

1. Add new column as nullable (no default):
   ```sql
   ALTER TABLE "Project" ADD COLUMN "new_field" TEXT;
   ```
2. Deploy new application version that writes **both** old and new columns.
3. Run data backfill script during low-traffic window.

### Phase 2 — Migrate (backfill existing rows)

```sql
UPDATE "Project" SET "new_field" = derive_value("old_field")
WHERE "new_field" IS NULL;
```

### Phase 3 — Contract (remove old column)

1. Deploy application version that reads only from `new_field`.
2. Drop the old column:
   ```sql
   ALTER TABLE "Project" DROP COLUMN "old_field";
   ```
3. Add NOT NULL constraint if required:
   ```sql
   ALTER TABLE "Project" ALTER COLUMN "new_field" SET NOT NULL;
   ```

This pattern means each deploy is independently reversible.

---

*Last updated: Week 31 — Day 206*

#!/usr/bin/env bash
# ==============================================================================
# pg_backup.sh – PostgreSQL backup script for AutoPenTest AI
# ==============================================================================
#
# Usage:
#   ./pg_backup.sh [backup_dir]
#
# Environment variables (all optional – defaults match docker-compose.yml):
#   POSTGRES_USER     – default: autopentestai
#   POSTGRES_PASSWORD – default: autopentestai_dev_password
#   POSTGRES_HOST     – default: localhost
#   POSTGRES_PORT     – default: 5432
#   POSTGRES_DB       – default: autopentestai
#   BACKUP_DIR        – default: /var/backups/autopentestai
#   BACKUP_KEEP_DAILY – days to keep daily backups (default: 7)
#   BACKUP_KEEP_WEEKLY– weeks to keep weekly backups  (default: 4)
#
# The script:
#   1. Runs pg_dump and compresses the output with gzip.
#   2. Tags the file as daily, weekly, or monthly depending on the date.
#   3. Applies retention: removes backups older than the configured threshold.
#
# Exit codes:
#   0 – success
#   1 – pg_dump failed
# ==============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PGUSER="${POSTGRES_USER:-autopentestai}"
PGPASSWORD="${POSTGRES_PASSWORD:-autopentestai_dev_password}"
PGHOST="${POSTGRES_HOST:-localhost}"
PGPORT="${POSTGRES_PORT:-5432}"
PGDATABASE="${POSTGRES_DB:-autopentestai}"

BACKUP_DIR="${BACKUP_DIR:-/var/backups/autopentestai}"
KEEP_DAILY="${BACKUP_KEEP_DAILY:-7}"
KEEP_WEEKLY="${BACKUP_KEEP_WEEKLY:-4}"   # in weeks → kept for 28 days max

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
DAY_OF_WEEK="$(date +%u)"   # 1=Monday … 7=Sunday
DAY_OF_MONTH="$(date +%d)"

# ---------------------------------------------------------------------------
# Determine backup type label
# ---------------------------------------------------------------------------
if [ "${DAY_OF_MONTH}" = "01" ]; then
    BACKUP_TYPE="monthly"
elif [ "${DAY_OF_WEEK}" = "7" ]; then
    BACKUP_TYPE="weekly"
else
    BACKUP_TYPE="daily"
fi

BACKUP_FILE="${BACKUP_DIR}/${BACKUP_TYPE}/autopentestai_${TIMESTAMP}.sql.gz"

# ---------------------------------------------------------------------------
# Ensure directories exist
# ---------------------------------------------------------------------------
mkdir -p "${BACKUP_DIR}/daily" "${BACKUP_DIR}/weekly" "${BACKUP_DIR}/monthly"

# ---------------------------------------------------------------------------
# Run pg_dump
# ---------------------------------------------------------------------------
echo "[$(date -u +%FT%TZ)] Starting ${BACKUP_TYPE} backup → ${BACKUP_FILE}"

export PGPASSWORD

pg_dump \
    --host="${PGHOST}" \
    --port="${PGPORT}" \
    --username="${PGUSER}" \
    --dbname="${PGDATABASE}" \
    --format=plain \
    --no-password \
    | gzip -9 > "${BACKUP_FILE}"

if [ $? -ne 0 ]; then
    echo "[$(date -u +%FT%TZ)] ERROR: pg_dump failed!" >&2
    exit 1
fi

echo "[$(date -u +%FT%TZ)] Backup written: ${BACKUP_FILE} ($(du -sh "${BACKUP_FILE}" | cut -f1))"

# ---------------------------------------------------------------------------
# Retention – prune old backups
# ---------------------------------------------------------------------------

# Daily: keep last N days
find "${BACKUP_DIR}/daily" -name "*.sql.gz" -mtime "+${KEEP_DAILY}" -delete \
    && echo "[$(date -u +%FT%TZ)] Pruned daily backups older than ${KEEP_DAILY} days"

# Weekly: keep last N×7 days
KEEP_WEEKLY_DAYS=$(( KEEP_WEEKLY * 7 ))
find "${BACKUP_DIR}/weekly" -name "*.sql.gz" -mtime "+${KEEP_WEEKLY_DAYS}" -delete \
    && echo "[$(date -u +%FT%TZ)] Pruned weekly backups older than ${KEEP_WEEKLY_DAYS} days"

# Monthly: keep for 1 year (365 days)
find "${BACKUP_DIR}/monthly" -name "*.sql.gz" -mtime "+365" -delete \
    && echo "[$(date -u +%FT%TZ)] Pruned monthly backups older than 365 days"

echo "[$(date -u +%FT%TZ)] Backup complete."

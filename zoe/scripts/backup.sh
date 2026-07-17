#!/bin/bash
# ZOE Backup Script
# Backup automatizado de la base de datos SQLite

set -euo pipefail

ZOE_DATA="${ZOE_DATA:-/opt/zoe/data}"
BACKUP_DIR="${BACKUP_DIR:-/opt/zoe/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup SQLite database
if [ -f "$ZOE_DATA/memory.db" ]; then
    sqlite3 "$ZOE_DATA/memory.db" ".backup '$BACKUP_DIR/memory_$TIMESTAMP.db'"
    echo "Backup created: $BACKUP_DIR/memory_$TIMESTAMP.db"
fi

# Backup identity and trajectory
if [ -d "$ZOE_DATA/alma" ]; then
    tar czf "$BACKUP_DIR/alma_$TIMESTAMP.tar.gz" -C "$ZOE_DATA" alma/
    echo "Backup created: $BACKUP_DIR/alma_$TIMESTAMP.tar.gz"
fi

# Cleanup old backups
find "$BACKUP_DIR" -name "*.db" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed. Retention: $RETENTION_DAYS days."

#!/bin/bash

# Backup script for landslide monitoring images
BACKUP_DIR="./backups"
IMAGE_DIR="./images"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/landslide_backup_$DATE.tar.gz"

mkdir -p "$BACKUP_DIR"

if [[ -d "$IMAGE_DIR" ]] && [[ $(ls -A "$IMAGE_DIR") ]]; then
    echo "Creating backup: $BACKUP_FILE"
    tar -czf "$BACKUP_FILE" -C "$IMAGE_DIR" .
    echo "Backup created successfully"
    
    # Keep only last 10 backups
    ls -t "$BACKUP_DIR"/landslide_backup_*.tar.gz | tail -n +11 | xargs -r rm
    echo "Old backups cleaned up"
else
    echo "No images to backup"
fi

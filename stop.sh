#!/usr/bin/env bash
# stop.sh — Tear down the stack (preserves volumes/data)
# Use --volumes flag to also wipe data: ./stop.sh --volumes

if [ "$1" == "--volumes" ]; then
    echo "Stopping stack and removing all data volumes..."
    docker compose down --volumes
else
    echo "Stopping stack (data preserved)..."
    docker compose down
fi
echo "Done."

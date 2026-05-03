#!/usr/bin/env bash
# ============================================================
# start.sh — Bring up the full observability stack
# Usage: ./start.sh
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting Observability Stack...${NC}"

# Pull latest images
echo -e "${YELLOW}Pulling images (first time may take 3-5 minutes)...${NC}"
docker compose pull

# Build sample-app
echo -e "${YELLOW}Building sample-app...${NC}"
docker compose build sample-app

# Start stack
echo -e "${YELLOW}Starting all services...${NC}"
docker compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 15

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Stack is UP! Access points:${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "  Grafana        → http://localhost:3000"
echo "                   user: admin / pass: observability123"
echo ""
echo "  Prometheus     → http://localhost:9090"
echo "  Alertmanager   → http://localhost:9093"
echo "  Kibana         → http://localhost:5601"
echo "  Sample App     → http://localhost:8080"
echo "  Node Exporter  → http://localhost:9100/metrics"
echo ""
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Run './status.sh' to check all services"
echo "Run './stop.sh' to shut down"

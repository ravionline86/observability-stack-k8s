#!/usr/bin/env bash
# status.sh — Check health of all stack services

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

check() {
    local name=$1
    local url=$2
    if curl -sf "$url" > /dev/null 2>&1; then
        echo -e "  ${GREEN}UP${NC}   $name  ($url)"
    else
        echo -e "  ${RED}DOWN${NC} $name  ($url)"
    fi
}

echo ""
echo "Service Health Check"
echo "===================="
check "Sample App    " "http://localhost:8080/health"
check "Prometheus    " "http://localhost:9090/-/healthy"
check "Alertmanager  " "http://localhost:9093/-/healthy"
check "Grafana       " "http://localhost:3000/api/health"
check "Elasticsearch " "http://localhost:9200/_cluster/health"
check "Kibana        " "http://localhost:5601/api/status"
check "Node Exporter " "http://localhost:9100/metrics"
echo ""
docker compose ps

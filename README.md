# observability-stack-k8s rakuten

> **Prometheus + Grafana + ELK Stack** — a production-style observability platform mirroring the monitoring architecture used for 5G Core deployments.

![CI](https://github.com/YOUR_USERNAME/observability-stack-k8s/actions/workflows/ci.yml/badge.svg)

---

## What This Project Does

This stack runs a **complete observability platform** locally using Docker Compose:

| Component | Role | Port |
|---|---|---|
| **sample-app** | Python microservice emitting metrics + logs (simulates a 5G NF) | 8080 |
| **Prometheus** | Scrapes metrics, evaluates alert rules | 9090 |
| **Alertmanager** | Routes alerts (email/Slack when configured) | 9093 |
| **Grafana** | Pre-built dashboards for NF metrics + host stats | 3000 |
| **Elasticsearch** | Stores structured JSON logs | 9200 |
| **Logstash** | Ingests and parses logs from the app | 5000 |
| **Kibana** | Log search and visualisation UI | 5601 |
| **Node Exporter** | Host CPU / RAM / Disk metrics | 9100 |

### Architecture

```
sample-app (port 8080)
    │
    ├──[/metrics]──► Prometheus ──► Alertmanager ──► (email/Slack)
    │                    │
    │                    └──────► Grafana (dashboards)
    │
    └──[stdout JSON logs]──► Logstash ──► Elasticsearch ──► Kibana
                                               │
                                           Node Exporter (host metrics)
                                               │
                                          Prometheus (also scraped)
```

---

## Prerequisites

Install these tools first (one-time setup):

### Windows (WSL2 + Docker Desktop)
1. Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) — enable WSL2 backend during install
2. Open **WSL2 terminal** (Ubuntu) for all commands below
3. Verify: `docker --version` and `docker compose version`

### Linux (Ubuntu/Debian)
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version
```

---

## Part 1: Run the Stack Locally

### Step 1 — Clone or download this repository

If you haven't set up Git yet:
```bash
# Install git (Linux/WSL)
sudo apt update && sudo apt install git -y

# Configure your identity (one-time)
git config --global user.name "Ravinder Kumar"
git config --global user.email "ravionline86@gmail.com"
```

Clone the repo:
```bash
git clone https://github.com/YOUR_USERNAME/observability-stack-k8s.git
cd observability-stack-k8s
```

### Step 2 — Make helper scripts executable
```bash
chmod +x start.sh stop.sh status.sh
```

### Step 3 — Start the stack
```bash
./start.sh
```
> **First run:** Docker pulls ~2 GB of images. Takes 3–5 minutes. Subsequent starts are fast.

### Step 4 — Open the UIs

| Tool | URL | Credentials |
|---|---|---|
| **Grafana** | http://localhost:3000 | admin / observability123 |
| **Prometheus** | http://localhost:9090 | none |
| **Alertmanager** | http://localhost:9093 | none |
| **Kibana** | http://localhost:5601 | none |
| **Sample App** | http://localhost:8080 | none |

### Step 5 — View the pre-built Grafana dashboard
1. Open http://localhost:3000 → login
2. Left sidebar → **Dashboards** → **Observability Stack** folder
3. Click **"5G Core NF Observability"**

You'll see live graphs for:
- Request rate & latency (p50/p95/p99)
- NF registration rates by type (AMF, SMF, UDM, PCF, CHF)
- Policy decision breakdown (PERMIT / DENY / REDIRECT)
- Active sessions gauge
- CPU / RAM / Disk from Node Exporter

### Step 6 — Check running services
```bash
./status.sh
```

### Step 7 — Stop the stack
```bash
./stop.sh                # stops, keeps data
./stop.sh --volumes      # stops + wipes all data (fresh start)
```

---

## Part 2: Push to GitHub (Beginner Step-by-Step)

### Step 1 — Create a GitHub account
Go to https://github.com → Sign up (free)

### Step 2 — Create a new repository on GitHub
1. Click the **+** icon (top right) → **New repository**
2. Repository name: `observability-stack-k8s`
3. Description: `Prometheus + Grafana + ELK observability stack with 5G NF simulation`
4. Set to **Public** (so CI badge is visible; required for free GitHub Actions minutes)
5. **Do NOT** check "Add a README" (we already have one)
6. Click **Create repository**

### Step 3 — Connect your local folder to GitHub
```bash
# Inside the project folder:
cd observability-stack-k8s

# Initialise git (if not cloned)
git init
git branch -M main

# Connect to your GitHub repo (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/observability-stack-k8s.git
```

### Step 4 — Stage, commit, and push all files
```bash
# Stage everything
git add .

# Commit with a message
git commit -m "Initial commit: Prometheus + Grafana + ELK observability stack"

# Push to GitHub
git push -u origin main
```
GitHub will ask for your username and a **Personal Access Token** (PAT) as password.

**How to create a PAT:**
1. GitHub → Settings → Developer Settings → Personal access tokens → Tokens (classic)
2. Click **Generate new token** → check `repo` scope → Generate
3. Copy the token — use it as the password when `git push` asks

### Step 5 — Watch CI run automatically
1. Go to your repo on GitHub
2. Click the **Actions** tab
3. You'll see **"CI — Build & Validate"** running
4. Green ✅ = all jobs passed. Red ❌ = click the job to see what failed.

### Step 6 — Making changes (the standard workflow)
```bash
# After editing any file:
git add .
git commit -m "describe what you changed"
git push
# → CI runs automatically on every push
```

---

## Part 3: Explore Prometheus Queries (PromQL)

Open http://localhost:9090 → click **Graph** tab → try these queries:

```promql
# Total requests per second
rate(app_requests_total[5m])

# p95 latency
histogram_quantile(0.95, rate(app_request_duration_seconds_bucket[5m]))

# NF registration failure rate
rate(nf_registrations_total{result="failure"}[5m])

# Active sessions
app_active_sessions

# Host CPU usage %
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

---

## Part 4: Explore Kibana Logs

1. Open http://localhost:5601
2. Go to **Discover** (left sidebar)
3. Create index pattern: `app-logs-*` with time field `@timestamp`
4. You'll see structured JSON logs from the sample-app in real time

---

## Part 5: Test Alerts

Fire a test alert by querying Alertmanager:
```bash
# Check active alerts
curl http://localhost:9093/api/v2/alerts | python -m json.tool

# View alert rules in Prometheus
curl http://localhost:9090/api/v1/rules | python -m json.tool
```

---

## Project Structure

```
observability-stack-k8s/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── prometheus/
│   ├── prometheus.yml          # Scrape config + targets
│   └── alert_rules.yml         # Alerting rules (app + infra)
├── alertmanager/
│   └── alertmanager.yml        # Alert routing config
├── grafana/
│   ├── dashboards/
│   │   └── nf-observability.json   # Pre-built Grafana dashboard
│   └── provisioning/
│       ├── datasources/
│       │   └── datasources.yml     # Auto-wires Prometheus + ES
│       └── dashboards/
│           └── dashboards.yml      # Auto-loads dashboards
├── logstash/
│   ├── pipeline/
│   │   └── logstash.conf       # Log ingestion pipeline
│   └── config/
│       └── logstash.yml        # Logstash settings
├── sample-app/
│   ├── app.py                  # Flask app with metrics + structured logs
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml          # Full stack definition
├── start.sh                    # Start script
├── stop.sh                     # Stop script
├── status.sh                   # Health check script
└── README.md
```

---

## Connecting to Resume

This project directly mirrors production work :

| Resume Claim | Project Implementation |
|---|---|
| *"Built KPI observability dashboards using Prometheus and Grafana"* | Pre-built Grafana dashboard with NF metrics, latency percentiles, gauge panels |
| *"Leveraged ELK Stack for centralised log aggregation"* | Full Logstash → Elasticsearch → Kibana pipeline |
| *"Prometheus and Grafana; ELK Stack for log correlation and incident triage"* | Dual pipeline: metrics via Prometheus, logs via ELK |
| *"Kubernetes environments"* | Docker Compose here, K8s manifests can be added |
| *"5G Core NFs (PCF, NRF, SCP)"* | sample-app simulates NF registration, policy decisions, SBI-style endpoints |

---

## Troubleshooting

**Elasticsearch fails to start (exit code 137):**
Increase Docker memory to at least 4 GB.
Docker Desktop → Settings → Resources → Memory → set to 4 GB+

**Port already in use:**
```bash
# Find what's using port 9090 (example)
sudo lsof -i :9090
# Or change the port in docker-compose.yml
```

**Grafana shows "No data":**
Wait 60 seconds after stack starts for Prometheus to collect first data points.

**Logstash keeps restarting:**
Elasticsearch may not be ready yet. Wait 30 seconds and run `./start.sh` again.

---

## License

MIT — free to use, modify, and share.

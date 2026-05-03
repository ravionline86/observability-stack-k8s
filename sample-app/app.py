"""
Sample Telecom-Style Microservice
Emits Prometheus metrics + structured JSON logs to stdout (picked up by Logstash)

Simulates a lightweight NF (Network Function) health endpoint
similar to what runs alongside PCF/NRF/SCP in a 5G Core deployment.
"""

import time
import random
import logging
import json
import os
from datetime import datetime

from flask import Flask, jsonify, request
from prometheus_client import (
    Counter, Histogram, Gauge, generate_latest,
    CONTENT_TYPE_LATEST, CollectorRegistry
)

# ──────────────────────────────────────────────
# Structured JSON logger (Logstash-friendly)
# ──────────────────────────────────────────────
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "sample-app",
            "environment": os.getenv("APP_ENV", "development"),
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        return json.dumps(log_entry)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("sample-app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ──────────────────────────────────────────────
# Prometheus metrics (mirrors 5G core NF style)
# ──────────────────────────────────────────────
app = Flask(__name__)

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total HTTP requests received",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "app_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

ACTIVE_SESSIONS = Gauge(
    "app_active_sessions",
    "Number of currently active sessions (simulated)"
)

NF_REGISTRATION_COUNT = Counter(
    "nf_registrations_total",
    "Simulated NF registration attempts",
    ["nf_type", "result"]
)

POLICY_DECISIONS = Counter(
    "policy_decisions_total",
    "Simulated policy control decisions",
    ["decision_type", "result"]
)

ERROR_COUNT = Counter(
    "app_errors_total",
    "Total application errors",
    ["error_type"]
)

# ──────────────────────────────────────────────
# Background simulation thread
# ──────────────────────────────────────────────
import threading

def simulate_background_traffic():
    """Simulates realistic 5G core NF traffic patterns in background."""
    nf_types = ["AMF", "SMF", "UDM", "PCF", "CHF"]
    decisions = ["PERMIT", "DENY", "REDIRECT", "THROTTLE"]
    results   = ["success", "success", "success", "failure"]  # ~75% success rate

    while True:
        # Simulate NF registrations
        nf = random.choice(nf_types)
        result = random.choice(results)
        NF_REGISTRATION_COUNT.labels(nf_type=nf, result=result).inc()

        # Simulate policy decisions
        decision = random.choice(decisions)
        res = random.choice(results)
        POLICY_DECISIONS.labels(decision_type=decision, result=res).inc()

        # Fluctuate active sessions (50–200 range)
        ACTIVE_SESSIONS.set(random.randint(50, 200))

        time.sleep(random.uniform(1, 3))

thread = threading.Thread(target=simulate_background_traffic, daemon=True)
thread.start()

# ──────────────────────────────────────────────
# Middleware: track every request
# ──────────────────────────────────────────────
@app.before_request
def start_timer():
    request._start_time = time.time()

@app.after_request
def record_metrics(response):
    latency = time.time() - request._start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.path
    ).observe(latency)
    logger.info("request handled", extra={
        "extra": {
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "latency_ms": round(latency * 1000, 2)
        }
    })
    return response

# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "sample-app", "timestamp": datetime.utcnow().isoformat()})

@app.route("/ready")
def ready():
    return jsonify({"status": "ready"})

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@app.route("/api/v1/nf/register", methods=["POST"])
def nf_register():
    """Simulates NRF NF registration endpoint."""
    nf_types = ["AMF", "SMF", "UDM", "PCF", "CHF", "SCP"]
    nf_type = request.json.get("nf_type", random.choice(nf_types)) if request.json else random.choice(nf_types)

    if random.random() < 0.05:  # 5% error simulation
        ERROR_COUNT.labels(error_type="registration_failure").inc()
        logger.warning("NF registration failed", extra={"extra": {"nf_type": nf_type}})
        return jsonify({"error": "registration_failed", "nf_type": nf_type}), 503

    logger.info("NF registered successfully", extra={"extra": {"nf_type": nf_type}})
    return jsonify({
        "nf_instance_id": f"nf-{nf_type.lower()}-{random.randint(1000, 9999)}",
        "nf_type": nf_type,
        "nf_status": "REGISTERED",
        "heartbeat_timer": 30
    })

@app.route("/api/v1/policy/decision", methods=["POST"])
def policy_decision():
    """Simulates PCF policy decision endpoint."""
    decisions = ["PERMIT", "DENY", "REDIRECT"]
    decision = random.choice(decisions)
    latency_sim = random.uniform(0.005, 0.15)
    time.sleep(latency_sim)

    logger.info("policy decision made", extra={"extra": {"decision": decision, "latency_ms": round(latency_sim*1000,2)}})
    return jsonify({"decision": decision, "policy_id": f"pol-{random.randint(100,999)}", "ttl": 3600})

@app.route("/api/v1/status")
def status():
    return jsonify({
        "service": "sample-app",
        "version": "1.0.0",
        "uptime_seconds": int(time.time()),
        "nf_types_supported": ["AMF", "SMF", "UDM", "PCF", "CHF", "SCP", "NRF"],
        "environment": os.getenv("APP_ENV", "dev")
    })

if __name__ == "__main__":
    logger.info("sample-app starting", extra={"extra": {"port": 8080}})
    app.run(host="0.0.0.0", port=8080, debug=False)

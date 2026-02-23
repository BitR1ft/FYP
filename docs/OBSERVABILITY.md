# Observability Guide

This document describes the monitoring, logging, and tracing stack.

## Stack Overview

| Component | Port | Purpose |
|-----------|------|---------|
| Prometheus | 9090 | Metrics collection |
| Grafana | 3001 | Dashboards & alerts |
| OpenTelemetry | — | Distributed tracing |

## Quick Start

```bash
cp .env.example .env          # set GRAFANA_PASSWORD
docker-compose up prometheus grafana
```

Open Grafana at http://localhost:3001 (admin / value of GRAFANA_PASSWORD).

## Metrics

All metrics are exposed at `GET /metrics` (Prometheus format).

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | method, endpoint, status_code | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | method, endpoint | Request latency |
| `tool_executions_total` | Counter | tool_name, status | Tool executions |
| `active_scans_total` | Gauge | — | Currently running scans |
| `queued_jobs_total` | Gauge | — | Jobs awaiting execution |

## Logging

All log output is structured JSON by default (`LOG_FORMAT=json`).

Key fields:
- `correlation_id` — matches the `X-Request-ID` request header
- `duration_ms` — total request duration

## Tracing

Set `OTEL_EXPORTER_OTLP_ENDPOINT` to export spans to an OTel collector.
Without this variable, spans are printed to stdout (development mode).

## Alert Rules

Alert rules live in `docker/monitoring/prometheus-alerts.yml`.

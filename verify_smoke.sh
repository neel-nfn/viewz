#!/usr/bin/env bash
set -euo pipefail
curl -s http://localhost:8000/api/v1/integrations | jq .
curl -s "http://localhost:8000/api/v1/analytics/channel_snapshot?window=7d" | jq .
curl -s "http://localhost:8000/api/v1/analytics/keywords?q=verstappen" | jq .
curl -s http://localhost:8000/api/v1/tasks/today | jq .
curl -s http://localhost:8000/api/v1/analytics/recommendations | jq .
curl -s http://localhost:8000/metrics | head -n 30

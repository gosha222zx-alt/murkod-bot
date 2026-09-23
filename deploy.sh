#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  echo "Missing .env. Copy .env.example to .env and fill in the tokens."
  exit 1
fi

if grep -q "your_telegram_bot_token\|your_groq_api_key" .env; then
  echo "Replace the placeholder values in .env before deployment."
  exit 1
fi

docker compose up -d --build
echo "Murkod is running. Recent logs:"
docker compose logs --tail=50 murkod

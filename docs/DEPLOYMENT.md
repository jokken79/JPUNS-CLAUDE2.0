# Deployment Guide

1. Copy `.env.example` to `.env` and configure secrets.
2. Run `docker-compose up -d --build`.
3. For production, set `ENVIRONMENT=production` and update `BACKEND_CORS_ORIGINS`.
4. Monitor health endpoints at `/api/monitoring/health`.

.PHONY: up down api dev

up:
	cd infra && docker compose up -d --build

down:
	cd infra && docker compose down

api:
	cd backend && source ~/.venvs/viewz/bin/activate && uvicorn app.main:app --reload --port 8000

dev:
	cd frontend && npm i && npm run dev

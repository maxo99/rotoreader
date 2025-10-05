


clear_db:
	docker compose exec -T postgres psql -U postgres -d rotoreader -c "DROP TABLE IF EXISTS teamdata CASCADE; DROP TABLE IF EXISTS feeddata CASCADE;"
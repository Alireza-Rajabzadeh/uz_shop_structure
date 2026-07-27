# UzShop Workspace - AGENTS.md

## Project

Top-level orchestration repository for UzShop. It owns Docker Compose, Nginx, shared environment configuration, and the Git submodule references for the backend and admin panel.

Application code lives in child repositories:

- `back/` - Django REST API backend
- `admin_panel/` - Next.js admin frontend

Read the child repository's `AGENTS.md` before changing application code there. The nearest agent file takes precedence for files inside that submodule.

## Repository Structure

```text
uz_shop_django/
├── back/             # Backend Git submodule
├── admin_panel/      # Frontend Git submodule
├── nginx/            # Backend reverse-proxy configuration
├── docker-compose.yml
├── .env.example
└── AGENTS.md
```

Do not recreate the previous `app/` directory. Docker builds and mounts the backend from `./back`.

## Submodules

| Path | Repository |
|---|---|
| `back/` | `https://github.com/Alireza-Rajabzadeh/uz_shop_django.git` |
| `admin_panel/` | `git@github.com:Alireza-Rajabzadeh/uz_shop_admin.git` |

Initialize a fresh checkout with:

```bash
git submodule update --init --recursive
```

### Submodule Workflow

Application changes must be committed inside the relevant child repository first. Then commit the updated submodule pointer in this top-level repository.

```bash
git -C back status
git -C admin_panel status
git status
```

When publishing changes, push child commits before pushing the top-level commit. Otherwise another checkout cannot resolve the referenced submodule revision.

Do not remove a child `.git` file/directory, copy child source into the top-level index, or replace a submodule with a normal directory.

## Docker Services

| Service | Purpose |
|---|---|
| `django` | Gunicorn-served Django backend on the internal port `8000` |
| `postgres` | PostgreSQL database |
| `redis` | Redis cache/infrastructure |
| `mongo` | MongoDB infrastructure/log storage |
| `nginx` | Reverse proxy exposed on `http://localhost:8080` |

The frontend is not currently a Docker Compose service. Run it from `admin_panel/`; its local API proxy should use `API_BACKEND_URL=http://localhost:8080/api`.

## Commands

Run these commands from the workspace root.

| Command | What it does |
|---|---|
| `docker compose up -d` | Start all backend infrastructure |
| `docker compose up -d --build django nginx` | Rebuild and restart the backend path |
| `docker compose restart django` | Reload mounted backend code under Gunicorn |
| `docker compose ps` | Show service status |
| `docker compose logs django` | Show backend logs |
| `docker compose exec -T django python manage.py migrate` | Apply migrations |
| `docker compose exec -T django python manage.py seed` | Seed development/reference data |
| `docker compose exec -T django python manage.py check` | Run Django system checks |
| `docker compose config --quiet` | Validate Compose configuration |

## Environment

Copy values from `.env.example` into the ignored top-level `.env` for Docker Compose.

Documented variables:

- `DEBUG`, `SECRET_KEY`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `REDIS_HOST`, `REDIS_PORT`
- `MONGO_HOST`, `MONGO_PORT`, `MONGO_USER`, `MONGO_PASSWORD`
- `UID`, `GID` when running the Django container as the host user

Never commit `.env` files or real credentials.

## Networking

- Public backend URL: `http://localhost:8080`
- Public API base: `http://localhost:8080/api`
- Django container: `django:8000`
- Nginx proxies requests to `django:8000`.
- PostgreSQL, Redis, and MongoDB are internal Compose services and are not published to host ports by default.

Keep the service name `django` and the `/app` container working directory unless Nginx, Compose, and deployment configuration are updated together.

## Change Boundaries

- Top-level changes: Compose, Nginx, workspace environment examples, submodule pointers, and orchestration documentation.
- Backend changes: make them inside `back/` and follow `back/AGENTS.md`.
- Frontend changes: make them inside `admin_panel/` and follow `admin_panel/AGENTS.md`.
- Do not mix application code into the orchestration repository.
- Do not modify both child repositories for a single concern unless the API contract actually requires coordinated changes.

## Important Gotchas

1. The top-level repository and backend must not share the same Git remote/branch history. The current backend remote belongs to the `back/` submodule; configure a separate remote if the orchestration repository is published.
2. Submodule pointers can reference local commits that have not been pushed. Verify child commits exist remotely before sharing or pushing the top-level repository.
3. Docker bind-mounts `./back:/app`; moving or renaming `back/` breaks the backend container.
4. The frontend uses its own `.next` directory. Do not run `next build` while `next dev` or `next start` is using that directory.
5. `.env` is shared by Compose, while Django also loads `back/.env` when run directly outside Compose.

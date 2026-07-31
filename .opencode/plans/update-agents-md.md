# Update AGENTS.md for client_panel submodule

## Changes needed

### 1. Application code description (line 9-11)
Change:
```
- `back/` - Django REST API backend
- `admin_panel/` - Next.js admin frontend
```
To:
```
- `back/` - Django REST API backend
- `admin_panel/` - Next.js admin frontend
- `client_panel/` - Next.js customer-facing frontend
```

### 2. Repository structure (line 16-24)
Change:
```text
uz_shop_django/
├── back/             # Backend Git submodule
├── admin_panel/      # Frontend Git submodule
├── nginx/            # Backend reverse-proxy configuration
├── docker-compose.yml
├── .env.example
└── AGENTS.md
```
To:
```text
uz_shop_django/
├── back/             # Backend Git submodule
├── admin_panel/      # Admin frontend Git submodule
├── client_panel/     # Customer-facing frontend Git submodule
├── nginx/            # Backend reverse-proxy configuration
├── docker-compose.yml
├── .env.example
└── AGENTS.md
```

### 3. Submodules table (line 30-33)
Change:
```
| `back/` | `https://github.com/Alireza-Rajabzadeh/uz_shop_django.git` |
| `admin_panel/` | `git@github.com:Alireza-Rajabzadeh/uz_shop_admin.git` |
```
To:
```
| `back/` | `https://github.com/Alireza-Rajabzadeh/uz_shop_django.git` |
| `admin_panel/` | `git@github.com:Alireza-Rajabzadeh/uz_shop_admin.git` |
| `client_panel/` | `git@github.com:Alireza-Rajabzadeh/uz_shop_next.git` |
```

### 4. Submodule workflow status commands (line 46-48)
Change:
```bash
git -C back status
git -C admin_panel status
git status
```
To:
```bash
git -C back status
git -C admin_panel status
git -C client_panel status
git status
```

### 5. Change Boundaries (line 108-114)
Change:
```
- Top-level changes: Compose, Nginx, workspace environment examples, submodule pointers, and orchestration documentation.
- Backend changes: make them inside `back/` and follow `back/AGENTS.md`.
- Frontend changes: make them inside `admin_panel/` and follow `admin_panel/AGENTS.md`.
- Do not mix application code into the orchestration repository.
- Do not modify both child repositories for a single concern unless the API contract actually requires coordinated changes.
```
To:
```
- Top-level changes: Compose, Nginx, workspace environment examples, submodule pointers, and orchestration documentation.
- Backend changes: make them inside `back/` and follow `back/AGENTS.md`.
- Admin frontend changes: make them inside `admin_panel/` and follow `admin_panel/AGENTS.md`.
- Customer frontend changes: make them inside `client_panel/` and follow `client_panel/AGENTS.md`.
- Do not mix application code into the orchestration repository.
- Do not modify multiple child repositories for a single concern unless the API contract actually requires coordinated changes.
```

### 6. Important Gotchas (line 116+)
Add a gotcha:
```
7. `client_panel/` is the customer-facing Next.js frontend. Follow its `AGENTS.md` for its specific conventions and tech stack.
```

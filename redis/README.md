# Redis ACL Setup

UzShop uses one internal Redis instance with separate `backend` and `client`
ACL users. Redis is not published to the host.

The backend user can read and write `backend:*`, `public:*`, and `private:*`
keys. It has channel access for Celery control/event fanout. The client user can
only read `public:*` keys and has no write or Pub/Sub permissions.
`CACHE_PUBLIC_PREFIX` and `CACHE_PRIVATE_PREFIX` must remain aligned with these
ACL namespaces; backend startup rejects mismatched values.

## Provision Local Credentials

1. Set a URL-safe `BACKEND_REDIS_PASSWORD` in the ignored root `.env` file and
   put a different client password in the server-only `CLIENT_REDIS_URL` in
   `client_panel/.env`. Set a third password in `infra/backups/.env` only when
   Redis snapshots are enabled. Hex-encoded random values avoid URL-encoding
   ambiguity.
2. Copy `users.acl.example` to the ignored `users.acl` file.
3. Replace each hash placeholder with the lowercase SHA-256 hash of the
   corresponding password. Redis ACL password hashes use `#<sha256>` syntax.

For example, calculate a hash without adding a newline:

```bash
printf %s 'password' | sha256sum
```

Each deployed password and its hash in `users.acl` must match. Redis
configuration files do not expand environment variables, so Compose mounts the
real ACL file as a file-backed secret. Production deployments should provide
the same secret from their deployment secret manager rather than committing it.

The optional `backup` user can only inspect persistence state and request an
RDB snapshot. It has no key access. Leave it disabled by omitting the user from
the deployed `users.acl` when Redis backups are not used.

The backend constructs authenticated database 1 and database 2 URLs from
`BACKEND_REDIS_PASSWORD`. A containerized customer panel should receive this
server-only URL from its deployment environment:

```text
redis://client:<password>@redis:6379/0
```

## Namespace Cutover

Before the first ACL-enabled deployment, stop producers and drain both Celery
queues. Existing unprefixed broker keys are not consumed after the
`backend:` prefix is enabled. Existing confirmation challenges contain stored
key references; allow their maximum 15-minute lifetime to expire before the
cutover.

## Verification

Use `REDISCLI_AUTH` rather than placing passwords directly in command arguments:

```bash
docker compose exec -T redis sh -c 'REDISCLI_AUTH="$BACKEND_REDIS_PASSWORD" redis-cli --user backend SET public:smoke ok'
```

Run the equivalent client check from `client_panel` or another container on the
application network using its deployment credential. The client must be able to
read `public:smoke`, but writes and all `private:*` access must receive `NOPERM`.
An unauthenticated `PING` must receive `NOAUTH` because the `default` user is
disabled.

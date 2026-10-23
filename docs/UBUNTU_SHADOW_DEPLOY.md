# Ubuntu SHADOW deployment

This deploys virtual trading only, using public REST data and QUANT_ONLY. No .env,
API keys, account dump or LIVE authorization is passed into the container. Market
constraints/fees are research assumptions from the existing example, not certified
current account limits. Existing dashboard Compose remains independent.

Prerequisites: Ubuntu with Docker Engine and Docker Compose v2 installed; repository
uploaded/cloned to a directory owned by the deployment user. No server access or
Docker installation was performed from this workspace.

From the repository root on the server:

```bash
docker compose -f compose.shadow.yaml build
docker compose -f compose.shadow.yaml up -d
docker compose -f compose.shadow.yaml ps
docker compose -f compose.shadow.yaml logs --tail=100 -f shadow
```

Ctrl+C exits log following without stopping the service. The daemon must itself
be enabled at server boot (`sudo systemctl enable --now docker`). `unless-stopped`
restarts exited containers, including after reboot unless explicitly stopped.
Unhealthy status alone does NOT automatically restart a still-running container.
Initial history collection may take time; inspect health and acquisition errors.

```bash
docker compose -f compose.shadow.yaml exec shadow python -m quantpilot.shadow.cli health --db /app/data/session.sqlite
docker compose -f compose.shadow.yaml exec shadow python -m quantpilot.shadow.cli portfolio --db /app/data/session.sqlite
docker compose -f compose.shadow.yaml exec shadow python -m quantpilot.shadow.cli export --db /app/data/session.sqlite --output /app/data/export
docker compose -f compose.shadow.yaml cp shadow:/app/data/export ./shadow-export
```

No ports are published. Health binds loopback inside the container and is accessible
through Compose exec. Named volume `shadow-state` retains financial and decision
state when containers are replaced. Never use `down -v` against retained evidence.
Run only one writer against this database; do not scale replicas.

Stop without selling or deleting state:

```bash
docker compose -f compose.shadow.yaml stop shadow
```

SIGINT requests normal Python cleanup; 150 seconds allows the bounded feed poll
to finish. A hard crash can leave a temporary lease; do not delete lock/database
contents to bypass it. Existing atomic checkpoint/recovery handles pending frames.

Before updates, stop the service and back up the ENTIRE volume while stopped,
including SQLite WAL files. Preserve the original image/source for old replay.
New source/config hashes can reject old journals. Use a new Compose project name
for a fresh session, retaining the old volume and image:

```bash
docker compose -p quantpilot-shadow-v2 -f compose.shadow.yaml up -d --build
```

Stop the old project first. This fresh project does not inherit prior virtual
positions. It is not a journal migration. Pin image/dependency versions for a
reviewed production release; this Dockerfile follows existing repository ranges.

Files were prepared locally. Remote build, Ubuntu runtime, restart/reboot and
external Wallex connectivity must be verified on the actual server. This is not
LIVE deployment or a claim of profitable trading.

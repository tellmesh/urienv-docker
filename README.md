> **DEPRECATED (2026-06-18):** the Docker deployment now lives inside the `urienv` package at [`urienv/docker/`](https://github.com/tellmesh/urienv/tree/main/docker). This repo is no longer maintained.

# urisys-env-docker

Pełna, minimalna implementacja `env://` dla `urisys` uruchamiana w Docker Compose.

Cel:

```text
transport: HTTP /uri/call
komenda:   env://runtime/...
runtime:   urisys-edge
pack:      urienv
policy:    allowlist public vars + masked secrets + explicit secret gate
```

## Uruchomienie

```bash
docker compose up --build urisys-env
```

Health:

```bash
curl http://127.0.0.1:8790/health
```

Lista tras:

```bash
curl http://127.0.0.1:8790/routes
```

## Przykłady `env://`

Publiczna zmienna:

```bash
curl -X POST http://127.0.0.1:8790/uri/call \
  -H 'Content-Type: application/json' \
  -d '{
    "uri": "env://runtime/var/APP_NAME/query/value",
    "payload": {},
    "context": {}
  }'
```

Startup snapshot:

```bash
curl -X POST http://127.0.0.1:8790/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"env://runtime/config/query/startup"}'
```

Sekret zamaskowany:

```bash
curl -X POST http://127.0.0.1:8790/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"env://runtime/secret/SMTP_PASSWORD/query/masked"}'
```

Pełna wartość sekretu jest celowo zablokowana, nawet przy `approved: true`, o ile runtime nie ma `allow_secret_read` albo `URISYS_ALLOW_SECRET_READ=1`:

```bash
curl -X POST http://127.0.0.1:8790/uri/call \
  -H 'Content-Type: application/json' \
  -d '{
    "uri":"env://runtime/secret/SMTP_PASSWORD/query/value",
    "context":{"approved":true}
  }'
```

Mutacja zmiennej procesowej, tylko allowlistowana zmienna i tylko w aktualnym procesie:

```bash
curl -X POST http://127.0.0.1:8790/uri/call \
  -H 'Content-Type: application/json' \
  -d '{
    "uri":"env://runtime/var/FEATURE_FLAG_DEMO/command/set",
    "payload":{"value":"on"},
    "context":{"approved":true}
  }'
```

## Test Docker e2e

```bash
./scripts/test-docker.sh
```

Test sprawdza:

- start serwera,
- odczyt publicznych zmiennych,
- snapshot startowy,
- maskowanie sekretów Docker secrets,
- blokadę pełnego sekretu,
- mutację procesowej zmiennej allowlistowanej.

## Test lokalny bez Dockera

```bash
./scripts/local-test.sh
```

## Pliki

```text
packages/python/urienv/              # env:// pack
packages/python/`uricore` (`uri_control.edge`)/          # mały runtime urisys: call/serve/flow
vendor/uricore/                      # parser/registry/dispatcher/policy/event store
docker-compose.yml                   # pełny stack demo
docker/config/env-policy.yaml        # allowlist i policy env://
docker/env/urisys.env                # demo env_file
docker/secrets/*.txt                 # demo Docker secrets
flows/*.uri.flow.yaml                # flow przykładowe
markpacts/*.markpact.md              # kontrakt i implementacja Markpact
```

## Zasada bezpieczeństwa

`env://` nie powinno być zwykłym wrapperem na `os.environ`. Ten przykład stosuje trzy bramki:

1. `public_vars` / `public_prefixes` — tylko one są czytelne jawnie.
2. `secret_vars` / `secret_prefixes` — domyślnie tylko masked.
3. Pełne sekrety wymagają `approved=true` oraz `allow_secret_read=true` albo `URISYS_ALLOW_SECRET_READ=1`.

W produkcji nie ustawiaj `URISYS_ALLOW_SECRET_READ=1`, chyba że uruchamiasz kontrolowany serwis wewnętrzny.

## Ekosystem TellMesh

Orchestrator: **[urisys](https://github.com/tellmesh/urisys)** · Mapa: **[MESH.md](https://github.com/tellmesh/urisys/blob/main/docs/MESH.md)** · Model: **[ECOSYSTEM.md](https://github.com/tellmesh/urisys/blob/main/../docs/ECOSYSTEM.md)**

| Pole | Wartość |
|------|---------|
| **Warstwa** | Docker glue |
| **Scheme** | `env://` |
| **Zależność** | uricore (`uri_control`) |

Runtime edge: **`uri_control.edge`** w pakiecie **`uricore`** (legacy `urisysedge` usunięty 2026-06).
Router intencji: **`urirouter`** (`uri_router`) — resolve + HTTP/MQTT delegate.

<!-- end-ecosystem -->

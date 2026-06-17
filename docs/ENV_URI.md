# `env://` w urisys

`env://` jest providerem konfiguracji startowej i sekretów runtime. Służy do tego, aby handler, flow albo zdalny klient mógł sprawdzić kontrolowany zestaw zmiennych, bez bezpośredniego dostępu do całego środowiska procesu.

## Dlaczego osobny provider?

Zamiast pisać w handlerach:

```python
os.environ['SMTP_PASSWORD']
```

lepiej kierować przez URI:

```text
env://runtime/secret/SMTP_PASSWORD/query/masked
env://runtime/var/APP_ENV/query/value
```

Dzięki temu każdy odczyt przechodzi przez:

```text
URI → registry → policy → env allowlist → event/result
```

## Transport a komenda

URL transportowy:

```text
http://device.local:8790/uri/call
```

Logiczna komenda:

```text
env://runtime/var/APP_NAME/query/value
```

Ten sam `env://` może działać lokalnie, przez HTTP, przez SSH tunnel, Docker Compose albo później jako provider w Kubernetes.

## Konfiguracja

Najważniejszy plik:

```text
docker/config/env-policy.yaml
```

Przykład:

```yaml
public_vars:
  - APP_NAME
  - APP_ENV
secret_vars:
  - SMTP_PASSWORD
mutable_vars:
  - FEATURE_FLAG_DEMO
docker_secrets_dir: /run/secrets
```

## URI

```text
env://runtime/query/health
env://runtime/query/list
env://runtime/config/query/startup
env://runtime/var/{NAME}/query/exists
env://runtime/var/{NAME}/query/value
env://runtime/secret/{NAME}/query/masked
env://runtime/secret/{NAME}/query/value
env://runtime/var/{NAME}/command/set
env://runtime/var/{NAME}/command/unset
```

## Flow

```yaml
flow:
  id: startup-env-check

do:
  - env://runtime/query/health
  - env://runtime/config/query/startup
  - env://runtime/var/APP_NAME/query/value
  - env://runtime/secret/SMTP_PASSWORD/query/masked
```

Uruchomienie lokalne:

```bash
urisys flow flows/startup-env-check.uri.flow.yaml --packs env --env-config docker/config/env-policy.yaml
```

# UriContract: urienv

`env://` exposes startup/runtime configuration through a controlled URI layer.
It is intended for boot diagnostics and safe configuration lookup, not as a free
secret dump.

```yaml markpact:contract
apiVersion: urisys.io/v1
kind: UriContract
metadata:
  id: urienv.contract
  version: 1.0.0
  title: Environment URI Contract
scheme: env
resources:
  - pattern: env://runtime
  - pattern: env://runtime/var/{name}
  - pattern: env://runtime/secret/{name}
queries:
  - id: env.health
    pattern: env://runtime/query/health
    output:
      type: object
  - id: env.list
    pattern: env://runtime/query/list
    input:
      type: object
      properties:
        include_values:
          type: boolean
    output:
      type: object
  - id: env.startup_config
    pattern: env://runtime/config/query/startup
    output:
      type: object
  - id: env.var.exists
    pattern: env://runtime/var/{name}/query/exists
    output:
      type: object
  - id: env.var.value
    pattern: env://runtime/var/{name}/query/value
    output:
      type: object
  - id: env.secret.masked
    pattern: env://runtime/secret/{name}/query/masked
    output:
      type: object
  - id: env.secret.value
    pattern: env://runtime/secret/{name}/query/value
    requires_approval: true
    security:
      requires_context:
        allow_secret_read: true
commands:
  - id: env.var.set
    pattern: env://runtime/var/{name}/command/set
    side_effects: true
    requires_approval: true
    input:
      type: object
      required: [value]
      properties:
        value: {}
  - id: env.var.unset
    pattern: env://runtime/var/{name}/command/unset
    side_effects: true
    requires_approval: true
events:
  - id: env.query.completed
  - id: env.var.changed
  - id: env.policy.denied
```

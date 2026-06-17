# UriImplementation: urienv-python

Python implementation for `env://` in `urisys-edge`.

```yaml markpact:implementation
apiVersion: urisys.io/v1
kind: UriImplementation
metadata:
  id: urienv-python
  version: 0.1.0
  language: python
  platform: linux-container
implements:
  contract: urienv.contract
  version: ^1.0.0
runtime:
  type: python
  package: urienv
  service_command: urisys serve --packs env --env-config /etc/urisys/env-policy.yaml
capabilities:
  - contract_query: env.health
    handler: python://urienv.handlers:health
  - contract_query: env.list
    handler: python://urienv.handlers:list_vars
  - contract_query: env.startup_config
    handler: python://urienv.handlers:startup_config
  - contract_query: env.var.value
    handler: python://urienv.handlers:var_value
  - contract_query: env.secret.masked
    handler: python://urienv.handlers:secret_masked
  - contract_query: env.secret.value
    handler: python://urienv.handlers:secret_value
  - contract_command: env.var.set
    handler: python://urienv.handlers:var_set
  - contract_command: env.var.unset
    handler: python://urienv.handlers:var_unset
configuration:
  env_config_file: /etc/urisys/env-policy.yaml
  docker_secrets_dir: /run/secrets
```

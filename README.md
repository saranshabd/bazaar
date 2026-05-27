# arize_phoenix_playground

Playground project for toying around with Phoenix and LLM observability auto-instrumentation.

### Local development setup

```shell
poetry env use python3.10   # set the Python version
eval $(poetry env activate) # activate Poetry shell
poetry install              # install dependencies
```

### Spin up Phoenix dashboard

The following command will start serving the Phoenix dashboard locally on `http://localhost:6006`

- It uses SQLite as the default database.

```shell
phoenix serve
```

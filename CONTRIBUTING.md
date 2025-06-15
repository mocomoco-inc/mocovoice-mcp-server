# mocovoice-mcp-server への貢献


## 開発方法

### docker build
```bash
docker build . -t mocovoice-mcp-server
```

### format
```bash
uv run ruff format
```

### lint
```bash
uv run ruff check .
```

### pytest

```bash
uv run pytest
```
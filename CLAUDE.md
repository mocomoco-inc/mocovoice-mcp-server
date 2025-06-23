# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server for mocoVoice, a Japanese transcription service. The server enables Claude Desktop to interact with the mocoVoice API for audio/video transcription tasks.

## Architecture

The codebase follows a modular structure:

- **server.py**: Main MCP server using FastMCP framework with 6 tools for transcription operations
- **api.py**: HTTP client wrapper with error handling and timeout management
- **constant.py**: Configuration constants including API endpoints, file format mappings, and error codes
- **utils.py**: Utility functions for validation, path checking, UUID validation, and data extraction

## Key Components

### MCP Tools
The server exposes 6 tools:
- `SHOW_USAGE`: Display functionality overview
- `SHOW_AVAILABLE_FORMATS`: List supported audio/video formats
- `SHOW_AVAILABLE_FILES`: Scan allowed directory for processable files
- `START_TRANSCRIPTION_JOB`: Upload and start transcription job
- `SHOW_TRANSCRIPTION_RESULT`: Retrieve completed transcription
- `CHECK_TRANSCRIPTION_STATUSES`: List transcription history

### Environment Configuration
- `MOCOVOICE_API_KEY`: Required API key with READ/WRITE permissions
- `MOCOVOICE_API_URL`: API endpoint (defaults to https://api.mocomoco.ai/api/v1)
- `ALLOWED_DIR`: Directory path for accessible files (defaults to /workspace)

### File Handling
- Max file size: 3GB
- Supported formats defined in `SUPPORT_MEDIA_CONTENT_TYPES`
- Path validation ensures files are within allowed directory

## Development Commands

### Build
```bash
docker build . -t mocovoice-mcp-server
```

### Formatting
```bash
uv run ruff format
```

### Linting
```bash
uv run ruff check .
```

### Testing
```bash
uv run pytest
```

## Dependencies

- **httpx**: Async HTTP client for API calls
- **mcp[cli]**: Model Context Protocol framework
- **pytest**: Testing framework
- **ruff**: Code formatting and linting

## Error Handling

The API module includes comprehensive error handling:
- HTTP status code mapping with Japanese error messages
- Timeout handling (configurable, defaults to 10s for most operations, 3600s for uploads)
- Network error recovery
- JSON decode error handling

## Security Considerations

- API key validation for all authenticated endpoints
- Path traversal protection via `is_path_allowed()`
- File validation including size limits and format checking
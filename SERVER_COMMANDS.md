# WN-PrinterHub Server Commands

## Quick Start

```bash
# Development mode (default) - with hot reload
./runserver.sh

# Production mode - optimized for deployment
./runserver.sh prod
```

## Command Details

### Development Mode
```bash
./runserver.sh dev
# or simply
./runserver.sh
```
- ✅ Hot reload enabled
- ✅ Debug logging
- ✅ File watching for changes
- ✅ Best for development

### Production Mode
```bash
./runserver.sh prod
```
- ✅ Optimized performance
- ✅ Single worker process
- ✅ Production logging
- ✅ Best for deployment

## Environment Variables

Create `.env` file for configuration:

```bash
# Authentication (set false for dev, true for prod)
USE_AUTH=true
WN_API_TOKEN=your_secure_token_here

# Server settings
WN_HOST=0.0.0.0
WN_PORT=8088

# CORS settings
WN_ALLOWED_ORIGINS=*

# Printer settings  
WN_PRINTER_DEFAULT_PORT=9100
```

## Access Points

- **API Server**: http://localhost:8088
- **Interactive Docs**: http://localhost:8088/docs
- **Health Check**: http://localhost:8088/health

## Troubleshooting

1. **Permission denied**: `chmod +x runserver.sh`
2. **uv not found**: Install from https://github.com/astral-sh/uv
3. **Port in use**: Change `WN_PORT` in `.env`
4. **Auth issues**: Set `USE_AUTH=false` in `.env` for development
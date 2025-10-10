# Redis Setup for Edurise LMS WebSocket Support

This guide will help you set up Redis for WebSocket functionality in the Edurise LMS.

## Option 1: Using Docker (Recommended)

### Install Docker Desktop
1. Download Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Install and start Docker Desktop

### Run Redis Container
```bash
# Pull and run Redis container
docker run -d --name edurise-redis -p 6379:6379 redis:7-alpine

# Verify Redis is running
docker ps
```

### Test Redis Connection
```bash
# Connect to Redis CLI
docker exec -it edurise-redis redis-cli

# Test basic commands
ping
set test "Hello Redis"
get test
exit
```

## Option 2: Using WSL2 (Windows Subsystem for Linux)

### Install WSL2
```powershell
# Run in PowerShell as Administrator
wsl --install
```

### Install Redis in WSL2
```bash
# Open WSL2 terminal
wsl

# Update package list
sudo apt update

# Install Redis
sudo apt install redis-server

# Start Redis
sudo service redis-server start

# Test Redis
redis-cli ping
```

## Option 3: Using Chocolatey (Windows Package Manager)

### Install Chocolatey
```powershell
# Run in PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### Install Redis
```powershell
# Install Redis using Chocolatey
choco install redis-64

# Start Redis service
redis-server
```

## Option 4: Manual Installation (Windows)

### Download Redis for Windows
1. Go to [https://github.com/microsoftarchive/redis/releases](https://github.com/microsoftarchive/redis/releases)
2. Download the latest `.msi` file
3. Install Redis
4. Start Redis service from Services panel

## Configuration

### Update Django Settings
Your Django settings are already configured for Redis:

```python
# In backend/config/settings/base.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

### Environment Variables
Add to your `.env.development`:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Testing the Setup

### Test Django Channels with Redis
```bash
cd backend
python manage.py shell
```

```python
# Test channel layer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

# Test basic functionality
async_to_sync(channel_layer.group_add)("test_group", "test_channel")
print("Channel layer working!")
```

### Test WebSocket Connection
1. Start Django development server:
```bash
cd backend
python manage.py runserver
```

2. Start frontend development server:
```bash
cd frontend
npm run dev
```

3. Navigate to a live class page and check browser console for WebSocket connection logs

## Troubleshooting

### Redis Connection Issues
```bash
# Check if Redis is running
redis-cli ping

# Check Redis logs (Docker)
docker logs edurise-redis

# Check Redis logs (WSL2)
sudo tail -f /var/log/redis/redis-server.log
```

### Django Channels Issues
```bash
# Check if channels_redis is installed
pip list | grep channels-redis

# Test channel layer in Django shell
python manage.py shell
from channels.layers import get_channel_layer
print(get_channel_layer())
```

### Port Conflicts
If port 6379 is already in use:

```bash
# Find process using port 6379
netstat -ano | findstr :6379

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use a different port in settings
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6380)],  # Different port
        },
    },
}
```

## Production Considerations

### Redis Security
- Set up Redis authentication
- Configure firewall rules
- Use Redis Sentinel for high availability
- Enable Redis persistence

### Performance Tuning
- Adjust Redis memory settings
- Configure connection pooling
- Monitor Redis performance
- Set up Redis clustering for scale

## Next Steps

After Redis is running:

1. **Start the Django server**: `python manage.py runserver`
2. **Test WebSocket connections** in the live classes interface
3. **Monitor Redis** for WebSocket message traffic
4. **Check Django logs** for any WebSocket-related errors

## Support

If you encounter issues:
1. Check the Redis logs
2. Verify Django Channels configuration
3. Test WebSocket connections in browser developer tools
4. Review Django server logs for errors
# Redis Setup for WebSocket Notifications

## Windows Installation

### Option 1: Using WSL (Recommended)
1. Install WSL2 if not already installed
2. Install Redis in WSL:
```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

### Option 2: Using Docker
```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

### Option 3: Windows Native (Redis for Windows)
1. Download Redis for Windows from: https://github.com/microsoftarchive/redis/releases
2. Install and start the Redis service
3. Verify connection: `redis-cli ping` should return `PONG`

## Configuration
Update your `.env.development` file:
```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Verification
Run this command to test Redis connection:
```bash
python manage.py shell -c "import redis; r = redis.Redis(); print('Redis connected:', r.ping())"
```
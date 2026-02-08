# Background Task Queue System

This directory contains the background task processing system using Celery and Redis.

## Overview

The task queue system provides:
- **FIFO queuing per agent**: Each agent has its own queue, tasks are processed in order
- **Priority handling**: Critical and high-priority tasks are processed first
- **Automatic retries**: Failed tasks are automatically retried up to 3 times
- **Status tracking**: Real-time task status updates
- **Error handling**: Comprehensive error logging and recovery

## Architecture

```
User Request → API → Task Service → Task Queue (Redis)
                                         ↓
                                    Celery Worker
                                         ↓
                                    Task Processor
                                         ↓
                                    Agent Execution
                                         ↓
                                    Update Status & Results
```

## Components

### 1. Celery App (`app/core/celery_app.py`)
- Configures Celery with Redis broker
- Sets up task routing and worker settings
- Defines task serialization and timeout settings

### 2. Background Worker (`app/workers/background_worker.py`)
- **TaskProcessor**: Executes tasks by running agents
- **AgentQueueManager**: Manages FIFO queues per agent
- **Celery Tasks**: Defines the `process_task` Celery task

### 3. Task Service (`app/services/task_service.py`)
- CRUD operations for tasks
- Task status management
- Task filtering and pagination

### 4. Agent Status Service (`app/services/agent_status_service.py`)
- Tracks agent availability (available, busy, idle)
- Manages queue lengths
- Updates agent status during task processing

## Usage

### Starting the Worker

```bash
# No need to start Redis - we're using Redis Cloud!

# Start Celery worker
python celery_worker.py

# Or with custom options
celery -A app.core.celery_app worker --loglevel=info --concurrency=4
```

### Testing Redis Cloud Connection

```bash
# Test connection
python -m app.core.redis_client

# Expected output:
# ✓ Redis connection successful
#   Redis version: 7.x.x
#   Connected to: redis-12792.c274.us-east-1-3.ec2.cloud.redislabs.com:12792
```

### Creating a Task

```python
from app.schemas.task import TaskCreate, TaskType, TaskPriority
from app.services.task_service import TaskService
from app.workers.background_worker import enqueue_task

# Create task
task_data = TaskCreate(
    title="Analyze Q4 Expenses",
    description="Analyze all expenses from Q4 2025",
    agent_type="finance",
    task_type=TaskType.BACKGROUND,
    priority=TaskPriority.HIGH,
    input_data={"quarter": "Q4", "year": 2025}
)

# Save to database
task = task_service.create_task(user_id=1, task_data=task_data)

# Enqueue for processing
result = enqueue_task(task.id)
```

### Checking Queue Status

```python
from app.workers.background_worker import get_queue_status

# Get queue status for an agent
status = get_queue_status(user_id=1, agent_type="finance")

print(f"Agent Status: {status['agent_status']}")
print(f"Tasks in Queue: {status['tasks_in_queue']}")
print(f"Current Task: {status['current_task_id']}")
```

### Cancelling a Task

```python
from app.workers.background_worker import cancel_task

# Cancel a pending or queued task
result = cancel_task(task_id=123, user_id=1)

if result['success']:
    print("Task cancelled successfully")
```

## Task Lifecycle

1. **PENDING**: Task created, waiting to be queued
2. **QUEUED**: Task added to agent's queue, waiting for processing
3. **IN_PROGRESS**: Task is currently being processed by agent
4. **COMPLETED**: Task completed successfully
5. **FAILED**: Task failed after all retries
6. **CANCELLED**: Task cancelled by user

## Priority Handling

Tasks are processed in the following order:
1. **CRITICAL**: Highest priority, processed immediately
2. **HIGH**: High priority, processed before medium/low
3. **MEDIUM**: Normal priority (default)
4. **LOW**: Lowest priority, processed last

Within the same priority level, tasks are processed FIFO (first in, first out).

## Error Handling

- **Automatic Retries**: Failed tasks are retried up to 3 times (configurable)
- **Retry Delay**: 60 seconds between retries (configurable)
- **Error Logging**: All errors are logged with full stack traces
- **Task History**: All status changes are recorded in task_history table

## Configuration

Environment variables (in `.env`):

```bash
# Redis Cloud Configuration
REDIS_HOST=redis-12792.c274.us-east-1-3.ec2.cloud.redislabs.com
REDIS_PORT=12792
REDIS_USERNAME=default
REDIS_PASSWORD=cQidNJeKkIOwLGwGve2SVsGsK1rSA3ls
REDIS_DB=0
REDIS_SSL=true

# Task Queue Settings
TASK_MAX_RETRIES=3
TASK_RETRY_DELAY=60
```

**Note:** Redis Cloud uses SSL/TLS by default. The configuration automatically handles secure connections.

## Monitoring

### Celery Flower (Web UI)

```bash
# Install Flower
pip install flower

# Start Flower
celery -A app.core.celery_app flower --port=5555
```

Access at: http://localhost:5555

### Redis CLI

```bash
# Connect to Redis Cloud
redis-cli -h redis-12792.c274.us-east-1-3.ec2.cloud.redislabs.com \
          -p 12792 \
          -a cQidNJeKkIOwLGwGve2SVsGsK1rSA3ls \
          --tls

# Check queue length
LLEN celery

# View pending tasks
LRANGE celery 0 -1
```

**Note:** Redis Cloud requires TLS/SSL connection (use `--tls` flag).

## API Endpoints

### Create Task
```
POST /api/v1/tasks
```

### List Tasks
```
GET /api/v1/tasks?status=pending&agent_type=finance
```

### Get Task
```
GET /api/v1/tasks/{task_id}
```

### Update Task
```
PATCH /api/v1/tasks/{task_id}
```

### Cancel Task
```
POST /api/v1/tasks/{task_id}/cancel
```

### Get Queue Status
```
GET /api/v1/tasks/agents/{agent_type}/queue
```

## Best Practices

1. **Use Background Tasks for Long Operations**: Any operation taking > 5 seconds should be a background task
2. **Set Appropriate Priorities**: Use CRITICAL sparingly, reserve for urgent tasks
3. **Monitor Queue Lengths**: Keep an eye on queue lengths to prevent backlogs
4. **Handle Failures Gracefully**: Implement proper error handling in agents
5. **Clean Up Old Tasks**: Periodically archive or delete completed tasks

## Troubleshooting

### Worker Not Processing Tasks
- Check if Redis is running: `redis-cli ping`
- Check if worker is running: `celery -A app.core.celery_app inspect active`
- Check worker logs for errors

### Tasks Stuck in QUEUED
- Check agent status: Agent might be stuck in BUSY state
- Restart worker to reset agent status
- Check for errors in task execution

### High Memory Usage
- Reduce worker concurrency
- Implement task result expiration
- Clean up old task results from Redis

## Development

### Running Tests
```bash
pytest tests/test_background_worker.py -v
```

### Debugging Tasks
```bash
# Run worker in debug mode
celery -A app.core.celery_app worker --loglevel=debug

# Run single task synchronously (for debugging)
from app.workers.background_worker import process_task
result = process_task(task_id=123)
```

## Production Deployment

### Systemd Service (Linux)

Create `/etc/systemd/system/topfloor-celery.service`:

```ini
[Unit]
Description=TopFloor Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=topfloor
Group=topfloor
WorkingDirectory=/opt/topfloor
Environment="PATH=/opt/topfloor/venv/bin"
ExecStart=/opt/topfloor/venv/bin/celery -A app.core.celery_app worker --loglevel=info --concurrency=4 --detach
ExecStop=/opt/topfloor/venv/bin/celery -A app.core.celery_app control shutdown
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable topfloor-celery
sudo systemctl start topfloor-celery
```

### Docker

```dockerfile
# Celery worker container
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["celery", "-A", "app.core.celery_app", "worker", "--loglevel=info", "--concurrency=4"]
```

### Scaling

To handle more load:
1. Increase worker concurrency: `--concurrency=8`
2. Run multiple worker instances
3. Use separate queues for different agent types
4. Scale Redis with Redis Cluster

## Support

For issues or questions:
- Check logs: `celery -A app.core.celery_app events`
- Monitor with Flower: http://localhost:5555
- Review task history in database

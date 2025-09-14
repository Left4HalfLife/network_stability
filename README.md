# Network Stability Monitor

A Flask web application that monitors internet connectivity by pinging 8.8.8.8 every minute and displays the results in a real-time graph interface.

## Features

- **Real-time monitoring**: Pings 8.8.8.8 every minute
- **Web dashboard**: Clean, responsive interface showing connection stability
- **Data persistence**: Daily JSON files with configurable timezone
- **Auto cleanup**: Configurable retention period for old data files
- **Docker support**: Easy deployment with Docker/Docker Compose
- **Statistics**: Success rate, average response time, failed pings count
- **Interactive graph**: Real-time chart showing ping response times

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd network_stability

# Start the application
docker-compose up -d

# Access the web interface
open http://localhost:5000
```

### Using Docker

```bash
# Build the image
docker build -t network-stability .

# Run the container
docker run -d -p 5000:5000 \
  -e TIMEZONE=America/New_York \
  -e CLEANUP_DAYS=30 \
  -v $(pwd)/data:/app/data \
  network-stability

# Access the web interface
open http://localhost:5000
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access the web interface
open http://localhost:5000
```

## Configuration

The application can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `TIMEZONE` | `UTC` | Timezone for daily file generation (e.g., `America/New_York`, `Europe/London`) |
| `CLEANUP_DAYS` | `30` | Number of days to keep data files (older files are deleted) |
| `DATA_DIR` | `./data` | Directory to store ping data files |
| `MOCK_PING` | `false` | Enable mock ping data for testing (when true, generates fake data) |

## API Endpoints

- `GET /` - Web dashboard
- `GET /api/data` - Get today's ping data as JSON
- `GET /api/stats` - Get statistics (total pings, success rate, etc.)

## Data Format

Data is stored in daily JSON files with the format `ping_data_YYYY-MM-DD.json`:

```json
[
  {
    "timestamp": "2025-09-14T04:48:19.783614+00:00",
    "response_time": 41.56,
    "success": true
  },
  {
    "timestamp": "2025-09-14T04:49:19.784419+00:00",
    "response_time": null,
    "success": false
  }
]
```

## Network Requirements

- The container/host must have network access to ping external hosts
- Port 5000 should be accessible for the web interface
- ICMP traffic must be allowed for ping functionality

## Troubleshooting

### Ping not working
If ping fails (common in some Docker environments), set `MOCK_PING=true` to generate mock data for testing.

### Permission issues
Ensure the data directory is writable by the application user.

### Timezone issues
Use standard timezone names (e.g., `America/New_York`, `Europe/London`). Invalid timezones will default to UTC.

## Development

The application consists of:

- `app.py` - Main Flask application
- `templates/index.html` - Web dashboard template
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-container setup

## License

See LICENSE file for details.

# 🌍 Terremoto - Earthquake Alert System

A Go application that sends daily notifications about earthquakes in your area using the [EMSC (European-Mediterranean Seismological Centre)](https://www.seismicportal.eu/) API and [Pushover](https://pushover.net) for notifications.

## Features

- 🌍 **Real-time earthquake data** from EMSC's global network
- 📍 **Location-based filtering** with customizable radius
- 🔔 **Daily push notifications** via Pushover
- 📊 **Detailed earthquake information** including magnitude, location, and distance
- 📝 **Comprehensive logging** for monitoring and debugging
- ⏰ **Scheduled alerts** at configurable times
- 🚀 **High performance** with Go's concurrency and efficiency
- 🌐 **Global coverage** including micro-earthquakes

## Prerequisites

1. **Go 1.21+** installed on your system
2. **Pushover account** - Sign up at [pushover.net](https://pushover.net)
3. **Your location coordinates** (latitude and longitude)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd terremoto
   ```

2. **Install dependencies:**
   ```bash
   go mod tidy
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   ```
   
   Edit the `.env` file with your configuration:
   ```env
   # Your location coordinates
   LATITUDE=40.7128
   LONGITUDE=-74.0060
   RADIUS_KM=100
   
   # Pushover credentials (get these from pushover.net)
   PUSHOVER_USER_KEY=your_user_key_here
   PUSHOVER_APP_TOKEN=your_app_token_here
   
   # Optional settings
   ALERT_TIME=08:00
   LOG_LEVEL=INFO
   ```

## Pushover Setup

1. **Create a Pushover account** at [pushover.net](https://pushover.net)
2. **Get your User Key** from the main page after logging in
3. **Create an application** to get your App Token:
   - Go to "Your Applications" → "Create an Application"
   - Name it "Earthquake Alert" or similar
   - Copy the App Token

## Usage

### Test the System

Before running the full system, test it to ensure everything works:

```bash
go run cmd/test/main.go
```

This will:
- Test the earthquake data fetching
- Verify message formatting
- Check distance calculations
- **No actual notifications will be sent**

### Run the Alert System

```bash
go run main.go
```

The system will:
- Start the scheduled daily alerts
- Run immediately if `RUN_IMMEDIATELY=true` is set in your `.env` file
- Continue running until stopped with Ctrl+C

### Run with Immediate Check

To run an immediate check without waiting for the scheduled time:

```bash
RUN_IMMEDIATELY=true go run main.go
```

### Build and Run

You can also build the application for production:

```bash
go build -o terremoto main.go
./terremoto
```

## Configuration Options

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LATITUDE` | Your latitude coordinate | - | Yes |
| `LONGITUDE` | Your longitude coordinate | - | Yes |
| `RADIUS_KM` | Search radius in kilometers | 100 | No |
| `PUSHOVER_USER_KEY` | Your Pushover User Key | - | Yes |
| `PUSHOVER_APP_TOKEN` | Your Pushover App Token | - | Yes |
| `ALERT_TIME` | Daily alert time (24h format) | 08:00 | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO | No |

## Sample Output

The system will send notifications like this:

```
🌍 Earthquake Alert - Last 24 Hours
📍 Location: 40.7128, -74.0060
📏 Radius: 100km
📊 Found 2 earthquake(s):

1. Magnitude 3.2 - 5km NE of New York, NY
   📅 2024-01-15 14:30 UTC
   📍 Distance: 45.2km

2. Magnitude 2.1 - 10km SW of Newark, NJ
   📅 2024-01-15 12:15 UTC
   📍 Distance: 78.9km
```

## Logging

The application creates detailed logs in `earthquake_alerts.log` and also outputs to the console. Log levels can be configured via the `LOG_LEVEL` environment variable.

## Project Structure

```
terremoto/
├── main.go                 # Main application entry point
├── go.mod                  # Go module definition
├── go.sum                  # Go module checksums
├── pkg/
│   └── earthquake/
│       └── alert.go        # Core earthquake alert functionality
├── cmd/
│   └── test/
│       └── main.go         # Test command
├── env.example             # Environment variables template
├── earthquake_alerts.log   # Application logs
└── README.md              # This file
```

## Deployment Options

### Local Machine
Run the application directly on your local machine. It will continue running until stopped.

### Server/VPS
Deploy on a server for 24/7 operation:
```bash
go build -o terremoto main.go
nohup ./terremoto > earthquake.log 2>&1 &
```

### Docker
Create a Dockerfile for containerized deployment:
```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go mod download
RUN go build -o terremoto main.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/terremoto .
CMD ["./terremoto"]
```

## Troubleshooting

### Common Issues

1. **"PUSHOVER_USER_KEY and PUSHOVER_APP_TOKEN must be set"**
   - Ensure your `.env` file is properly configured
   - Check that the environment variables are loaded

2. **"Error fetching earthquake data"**
   - Check your internet connection
   - The EMSC API might be temporarily unavailable

3. **"Error sending Pushover notification"**
   - Verify your Pushover credentials
   - Check your internet connection
   - Ensure your Pushover account is active

### Debug Mode

Enable debug logging by setting:
```env
LOG_LEVEL=DEBUG
```

## API Information

This application uses the [EMSC (European-Mediterranean Seismological Centre) FDSN Web Service](https://www.seismicportal.eu/fdsnws/event/1/) for earthquake data. The service provides:

- Global earthquake data with excellent European coverage
- Real-time updates
- Multiple data formats (JSON, XML)
- No API key required
- Includes micro-earthquakes and smaller seismic events

## Performance

The Go implementation provides:
- **Fast startup times** - typically under 100ms
- **Low memory usage** - ~5-10MB RAM
- **Efficient HTTP handling** - built-in connection pooling
- **Concurrent processing** - can handle multiple requests efficiently

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This application is for informational purposes only. Always follow official emergency procedures and local authorities' guidance during earthquakes.
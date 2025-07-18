# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Terremoto is a Go-based earthquake alert system that fetches earthquake data from the EMSC (European-Mediterranean Seismological Centre) API and sends daily notifications via Pushover. The system monitors earthquakes within a configurable radius around a specified location.

## Common Commands

### Development Commands
- `go run main.go` - Run the main application
- `go run cmd/test/main.go` - Run test mode (no notifications sent)
- `go mod tidy` - Install/update dependencies
- `go build -o terremoto main.go` - Build the application

### Makefile Commands
- `make help` - Show available targets
- `make build` - Build the application
- `make test` - Run tests (executes cmd/test/main.go)
- `make run` - Run the application
- `make clean` - Clean build artifacts
- `make install` - Install dependencies

### Environment Setup
1. Copy `env.example` to `.env`
2. Configure required environment variables:
   - `LATITUDE`, `LONGITUDE` - Your location coordinates
   - `PUSHOVER_USER_KEY`, `PUSHOVER_APP_TOKEN` - Pushover credentials
   - Optional: `RADIUS_KM` (default: 100), `ALERT_TIME` (default: 08:00), `LOG_LEVEL` (default: INFO)

### Testing
- Run `make test` or `go run cmd/test/main.go` to test the system without sending notifications
- Use `RUN_IMMEDIATELY=true go run main.go` to run an immediate check

## Architecture

### Core Components

1. **main.go** - Application entry point that initializes and starts the alert system
2. **pkg/earthquake/alert.go** - Core earthquake alert functionality containing:
   - `Alert` struct - Main application state and configuration
   - `Config` struct - Application configuration from environment variables
   - EMSC API integration for earthquake data fetching
   - Pushover notification system
   - Cron-based scheduling for daily alerts

### Key Structures

- **Earthquake data models**: QuakeML (XML), EMSC JSON, and internal `Earthquake` struct
- **Alert system**: Handles configuration, logging, data fetching, filtering, and notifications
- **Distance calculation**: Uses Haversine formula for geographical distance

### Data Flow

1. Configuration loaded from environment variables and `.env` file
2. Cron scheduler runs daily alerts at configured time
3. Earthquake data fetched from EMSC API (last 24 hours)
4. Data filtered by radius from configured location
5. Formatted message sent via Pushover notification
6. All activities logged to `earthquake_alerts.log`

## Dependencies

- `github.com/joho/godotenv` - Environment variable loading
- `github.com/robfig/cron/v3` - Cron scheduling
- Standard Go libraries for HTTP, JSON/XML parsing, logging

## Key Features

- Real-time earthquake monitoring from EMSC global network
- Location-based filtering with customizable radius
- Daily scheduled notifications via Pushover
- Comprehensive logging system
- Test mode for development without sending notifications
- Cross-platform builds (Linux, macOS, Windows)

## Configuration

The application uses environment variables for configuration. All settings are defined in the `Config` struct in `pkg/earthquake/alert.go`. Required variables are validated at startup.
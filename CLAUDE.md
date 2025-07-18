# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Terremoto is an earthquake monitoring system for the M5Stack Core S3 device, written in MicroPython. The system monitors earthquake data from the EMSC API and displays alerts on the device's LCD screen when earthquakes occur within a specified radius of a monitored location.

## Architecture

- **main.py**: Core application containing the complete earthquake monitoring logic
  - WiFi connection management with retry logic
  - EMSC API integration for real-time earthquake data
  - Haversine distance calculations for proximity filtering
  - M5Stack Core S3 LCD display interface
  - Continuous monitoring loop with configurable intervals

- **config.py**: Configuration file containing sensitive credentials and monitoring parameters
  - WiFi credentials (SSID/password)
  - Geographic coordinates for monitoring location
  - Timezone offset configuration
  - Monitoring radius and check interval settings

## Development Commands

### Deployment to M5Stack Core S3
```bash
make deploy
```
This command:
1. Checks for config.py existence
2. Copies main.py and config.py to the device via mpremote
3. Resets the device to start the new code

### Device Connection
```bash
make connect
```
Connects to the M5Stack Core S3 via serial for debugging/monitoring

### Configuration Setup
If config.py doesn't exist, the deploy command will create it from config.template.py. Edit config.py with:
- Your WiFi network credentials
- Your geographic coordinates for monitoring
- Desired monitoring radius and check interval

## Key Dependencies

- MicroPython environment on M5Stack Core S3
- M5 library for device hardware interface
- requests library for HTTP API calls
- network library for WiFi connectivity
- mpremote tool for device communication

## Device Communication

The system uses `/dev/tty.usbmodem1101` as the default USB serial device for M5Stack Core S3 communication. Ensure the device is connected via USB before running deployment commands.
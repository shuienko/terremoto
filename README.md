# Terremoto - M5Stack Core S3 Earthquake Monitor

This project turns an M5Stack Core S3 into a real-time earthquake monitor. It fetches data from the EMSC (European-Mediterranean Seismological Centre) API and displays information about recent earthquakes within a specified radius of your location.

## Features

- **Real-time Monitoring**: Checks for new earthquake data at regular intervals.
- **Location-based Filtering**: Only shows earthquakes within a configurable radius of your GPS coordinates.
- **Magnitude Filtering**: Ignores earthquakes below a minimum magnitude.
- **Clear Display**: Shows key information on the M5Stack's screen:
    - Magnitude
    - Location name
    - Distance from your location
    - Time of the event
- **Audio Alerts**: Plays a tone when a new earthquake is detected.
- **WiFi Connectivity**: Connects to your WiFi network to fetch data.
- **Time Synchronization**: Syncs with an NTP server to ensure accurate time.
- **Resilient**: Handles WiFi disconnection and API errors gracefully.
- **Easy Configuration**: All settings are managed in a `config.py` file.
- **Do Not Disturb**: A configurable "do not disturb" mode to silence alerts for minor earthquakes during specific hours.
- **Automatic Display Dimming**: The display brightness is automatically reduced during "do not disturb" hours to save power and avoid being too bright at night.

## Requirements

### Hardware

- M5Stack Core S3

### Software

- MicroPython for M5Stack Core S3
- `urequests` library for MicroPython

## Setup

1.  **Install MicroPython**: Make sure your M5Stack Core S3 is flashed with the correct version of MicroPython.

2.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/terremoto.git
    cd terremoto
    ```

3.  **Install Libraries**:
    This project requires the `urequests` library. You can install it on your M5Stack using `upip`:
    ```python
    import upip
    upip.install('micropython-urequests')
    ```

4.  **Create `config.py`**:
    Copy the `config.template.py` file to `config.py`:
    ```bash
    cp config.template.py config.py
    ```

5.  **Configure the monitor**:
    Open `config.py` and edit the following settings:
    - `WIFI_SSID`: Your WiFi network name.
    - `WIFI_PASSWORD`: Your WiFi password.
    - `MONITOR_LATITUDE`: Your latitude.
    - `MONITOR_LONGITUDE`: Your longitude.
    - `MONITOR_RADIUS_KM`: The radius (in km) around your location to monitor for earthquakes.
    - `TIMEZONE_OFFSET_HOURS`: The hour difference from UTC for your local time.
    - `DO_NOT_DISTURB_START_HOUR` and `DO_NOT_DISTURB_END_HOUR`: The start and end hours for the "do not disturb" period (e.g., 23 and 9 for 11 PM to 9 AM). During this time, alerts for earthquakes with a magnitude of less than 5.0 will be silenced, and the display will dim.
    - `NORMAL_BRIGHTNESS_PERCENT` and `DIM_BRIGHTNESS_PERCENT`: The display brightness for normal operation and for the "do not disturb" period, respectively.
    - You can also adjust other settings like the check interval, minimum magnitude, etc.

## Transferring Files to M5Stack

This project includes a `Makefile` to simplify the process of transferring your code to the M5Stack.

1.  **Connect your M5Stack**: Plug your M5Stack Core S3 into your computer via USB.

2.  **Find your device's serial port**: You may need to identify the correct serial port for your M5Stack. On macOS, it will likely be something like `/dev/tty.usbmodem...`, and on Linux, `/dev/ttyUSB0` or similar. You might need to edit the `Makefile` to specify the correct port (`AMPY_PORT`).

3.  **Deploy the code**: Run the following command in your terminal:
    ```bash
    make deploy
    ```
    This command will:
    - Check if `config.py` exists. If not, it will remind you to create one.
    - Copy all `.py` files to your M5Stack.
    - Reset the device to start running the new code.

    To connect to the device's REPL (Read-Eval-Print Loop), run:
    ```bash
    make connect
    ```

## Usage

Once the setup is complete and the files are deployed, the M5Stack will automatically run `main.py`. The device will:
1.  Initialize and display a startup message with your monitoring settings.
2.  Connect to your WiFi network.
3.  Synchronize its time with an NTP server.
4.  Start the main monitoring loop:
    - Fetch earthquake data from the EMSC API.
    - If a new, significant earthquake is detected within your configured radius, it will display an alert and play a tone.
    - If no earthquakes are found, it will show an "ALL CLEAR" message with a summary of worldwide events.
    - The screen updates at the interval defined in `config.py`.

## File Descriptions

-   `main.py`: The main application script. It initializes the device, handles network connections, and runs the monitoring loop.
-   `api.py`: Handles all interactions with the EMSC earthquake API, including building the request URL, fetching data, and parsing the response.
-   `config.py`: Your local configuration file (not tracked by Git). You must create this from the template.
-   `config.template.py`: A template for the configuration file, containing all available settings.
-   `device.py`: Contains functions for interacting with the M5Stack hardware, such as initializing the screen, speaker, and controlling display brightness.
-   `display.py`: Manages what is shown on the M5Stack's screen, including message formatting, UI colors, and different display templates for alerts, info, and status messages.
-   `network_utils.py`: Provides functions for managing WiFi connectivity (including reconnections) and NTP time synchronization.
-   `utils.py`: A collection of utility functions, primarily for formatting timestamps into a human-readable format based on your local timezone.
-   `LICENSE`: The project's license.
-   `README.md`: This file.
-   `Makefile`: Contains helper commands for deploying code to the device and connecting to its REPL.

## Troubleshooting

- **WiFi Connection Issues**:
    - Double-check your `WIFI_SSID` and `WIFI_PASSWORD` in `config.py`.
    - Ensure your M5Stack is within range of your WiFi router.
    - The device will automatically try to reconnect if the connection is lost.

- **API Errors**:
    - The monitor will display a "CONNECTION ERROR" message if it cannot reach the EMSC API. This is often temporary.
    - The device will continue to retry at the specified interval.

- **Incorrect Time**:
    - Ensure the `TIMEZONE_OFFSET_HOURS` in `config.py` is set correctly for your location.
    - If the device fails to sync with the NTP server, it will display a warning. A successful time sync is required for accurate earthquake event times.

## Contributing

Contributions are welcome! Please feel free to submit a pull request. 
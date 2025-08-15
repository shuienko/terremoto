# Simple Clock - M5Stack Core S3

This project turns an M5Stack Core S3 into a simple digital clock that displays the current time in HH:MM format. It connects to WiFi to synchronize time with an NTP server and displays the time with a clean, readable interface.

## Features

- **Simple Time Display**: Shows current time in HH:MM format with a large, clear font
- **Date Display**: Shows current date below the time
- **WiFi Connectivity**: Connects to your WiFi network for time synchronization
- **Time Synchronization**: Syncs with an NTP server to ensure accurate time
- **Resilient**: Handles WiFi disconnection gracefully and continues to show time
- **Easy Configuration**: All settings are managed in a `config.py` file
- **Do Not Disturb**: A configurable "do not disturb" mode that dims the display during specific hours
- **Automatic Display Dimming**: The display brightness is automatically reduced during "do not disturb" hours to save power and avoid being too bright at night

## Requirements

### Hardware

- M5Stack Core S3

### Software

- MicroPython for M5Stack Core S3

## Setup

1.  **Install MicroPython**: Make sure your M5Stack Core S3 is flashed with the correct version of MicroPython.

2.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/terremoto.git
    cd terremoto
    ```

3.  **Create `config.py`**:
    Copy the `config.template.py` file to `config.py`:
    ```bash
    cp config.template.py config.py
    ```

4.  **Configure the clock**:
    Open `config.py` and edit the following settings:
    - `WIFI_SSID`: Your WiFi network name.
    - `WIFI_PASSWORD`: Your WiFi password.
    - `TIMEZONE_OFFSET_HOURS`: The hour difference from UTC for your local time.
    - `UPDATE_INTERVAL_SECONDS`: How often to update the display (default: 1 second).
    - `DO_NOT_DISTURB_START_HOUR` and `DO_NOT_DISTURB_END_HOUR`: The start and end hours for the "do not disturb" period (e.g., 23 and 9 for 11 PM to 9 AM). During this time, the display will dim.
    - `NORMAL_BRIGHTNESS_PERCENT` and `DIM_BRIGHTNESS_PERCENT`: The display brightness for normal operation and for the "do not disturb" period, respectively.

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
1.  Initialize and display a startup message.
2.  Connect to your WiFi network.
3.  Synchronize its time with an NTP server.
4.  Start the main clock loop:
    - Display the current time in HH:MM format
    - Show the current date below the time
    - Update the display every second (or as configured)
    - Automatically dim the display during "do not disturb" hours

## File Descriptions

-   `main.py`: The main application script. It initializes the device, handles network connections, and runs the clock loop.
-   `config.py`: Your local configuration file (not tracked by Git). You must create this from the template.
-   `config.template.py`: A template for the configuration file, containing all available settings.
-   `device.py`: Contains functions for interacting with the M5Stack hardware, such as initializing the screen and controlling display brightness.
-   `display.py`: Manages what is shown on the M5Stack's screen, including the clock display and startup message.
-   `network_utils.py`: Provides functions for managing WiFi connectivity (including reconnections) and NTP time synchronization.
-   `utils.py`: A collection of utility functions, primarily for formatting time into HH:MM format based on your local timezone.
-   `LICENSE`: The project's license.
-   `README.md`: This file.
-   `Makefile`: Contains helper commands for deploying code to the device and connecting to its REPL.

## Troubleshooting

- **WiFi Connection Issues**:
    - Double-check your `WIFI_SSID` and `WIFI_PASSWORD` in `config.py`.
    - Ensure your M5Stack is within range of your WiFi router.
    - The device will continue to show time even without WiFi connection.

- **Incorrect Time**:
    - Ensure the `TIMEZONE_OFFSET_HOURS` in `config.py` is set correctly for your location.
    - If the device fails to sync with the NTP server, it will continue to show time based on the device's internal clock.

## Contributing

Contributions are welcome! Please feel free to submit a pull request. 
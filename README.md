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
- **WiFi Connectivity**: Connects to your WiFi network to fetch data.
- **Time Synchronization**: Syncs with an NTP server to ensure accurate time.
- **Resilient**: Handles WiFi disconnection and API errors gracefully.
- **Easy Configuration**: All settings are managed in a `config.py` file.

## Requirements

### Hardware

- M5Stack Core S3

### Software

- MicroPython for M5Stack Core S3
- `requests` library for MicroPython

## Setup

1.  **Install MicroPython**: Make sure your M5Stack Core S3 is flashed with the correct version of MicroPython.

2.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/terremoto.git
    cd terremoto
    ```

3.  **Install libraries**: You will need to install the `requests` library. You can use `upip` for this.

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
    - You can also adjust other settings like the check interval, minimum magnitude, etc.

## Transferring Files to M5Stack

This project includes a `Makefile` to simplify the process of transferring your code to the M5Stack.

1.  **Connect your M5Stack**: Plug your M5Stack Core S3 into your computer via USB.

2.  **Find your device's serial port**: You may need to identify the correct serial port for your M5Stack. On macOS, it will likely be something like `/dev/tty.usbmodem...`, and on Linux, `/dev/ttyUSB0` or similar. You might need to edit the `Makefile` to specify the correct port.

3.  **Deploy the code**: Run the following command in your terminal:
    ```bash
    make deploy
    ```
    This command will:
    - Check if `config.py` exists. If not, it will create one from the template.
    - Copy `main.py` and `config.py` to your M5Stack.
    - Reset the device to start running the new code.

    If you just want to connect to the device's REPL, you can run:
    ```bash
    make connect
    ```

## Usage

Once the setup is complete, you can run the `main.py` script on your M5Stack Core S3. The device will:
1.  Initialize and display a startup message.
2.  Connect to your WiFi network.
3.  Synchronize its time with an NTP server.
4.  Start the monitoring loop:
    - Fetch earthquake data from the EMSC API.
    - If an earthquake is detected within your radius, it will be displayed on the screen.
    - If there are no earthquakes, it will show an "ALL CLEAR" message.
    - The screen will update at the interval defined in `config.py`.

## File Descriptions

-   `main.py`: The main application script.
-   `config.py`: Your local configuration (you need to create this).
-   `config.template.py`: A template for the configuration file.
-   `LICENSE`: The project's license.
-   `README.md`: This file.

## Contributing

Contributions are welcome! Please feel free to submit a pull request. 
# Function to find MicroPython device port
define find_mp_device
	$(shell ls /dev/tty.usbmodem* 2>/dev/null | head -1)
endef

# Function to find MicroPython device port with better detection
define find_mp_device_advanced
	$(shell for port in /dev/tty.usbmodem* /dev/tty.usbserial*; do \
		if [ -e "$$port" ]; then \
			echo "$$port"; \
			break; \
		fi; \
	done)
endef

# Get the device port dynamically
MP_DEVICE := $(call find_mp_device_advanced)

deploy:
	@echo "Checking for config.py..."
	@if [ ! -f config.py ]; then \
		echo "Error: config.py not found. Creating from template..."; \
		cp config.template.py config.py; \
		echo "Please edit config.py with your WiFi credentials"; \
		exit 1; \
	fi
	@echo "Looking for MicroPython device..."
	@if [ -z "$(MP_DEVICE)" ]; then \
		echo "Error: No MicroPython device found. Please connect your device."; \
		echo "Available USB devices:"; \
		ls /dev/tty.usb* 2>/dev/null || echo "No USB devices found"; \
		exit 1; \
	fi
	@echo "Using device: $(MP_DEVICE)"
	mpremote connect $(MP_DEVICE) cp main.py :main.py
	mpremote connect $(MP_DEVICE) cp config.py :config.py
	mpremote connect $(MP_DEVICE) cp device.py :device.py
	mpremote connect $(MP_DEVICE) cp display.py :display.py
	mpremote connect $(MP_DEVICE) cp network_utils.py :network_utils.py
	mpremote connect $(MP_DEVICE) cp utils.py :utils.py
	mpremote connect $(MP_DEVICE) reset

connect:
	@echo "Looking for MicroPython device..."
	@if [ -z "$(MP_DEVICE)" ]; then \
		echo "Error: No MicroPython device found. Please connect your device."; \
		echo "Available USB devices:"; \
		ls /dev/tty.usb* 2>/dev/null || echo "No USB devices found"; \
		exit 1; \
	fi
	@echo "Connecting to: $(MP_DEVICE)"
	mpremote connect $(MP_DEVICE)

# Helper target to list available USB devices
list-devices:
	@echo "Available USB devices:"
	@ls /dev/tty.usb* 2>/dev/null || echo "No USB devices found"
	@echo ""
	@echo "MicroPython device found: $(MP_DEVICE)"
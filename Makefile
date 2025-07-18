deploy:
	@echo "Checking for config.py..."
	@if [ ! -f config.py ]; then \
		echo "Error: config.py not found. Creating from template..."; \
		cp config.template.py config.py; \
		echo "Please edit config.py with your WiFi credentials and coordinates"; \
		exit 1; \
	fi
	mpremote connect /dev/tty.usbmodem1101 cp main.py :main.py
	mpremote connect /dev/tty.usbmodem1101 cp config.py :config.py
	mpremote connect /dev/tty.usbmodem1101 reset

connect:
	mpremote connect /dev/tty.usbmodem1101
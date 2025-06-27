.PHONY: build test run clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  build    - Build the application"
	@echo "  test     - Run tests"
	@echo "  run      - Run the application"
	@echo "  clean    - Clean build artifacts"
	@echo "  install  - Install dependencies"

# Build the application
build:
	@echo "Building terremoto..."
	go build -o terremoto main.go
	@echo "Build complete: ./terremoto"

# Run tests
test:
	@echo "Running tests..."
	go run cmd/test/main.go

# Run the application
run:
	@echo "Running terremoto..."
	go run main.go

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f terremoto
	@echo "Clean complete"

# Install dependencies
install:
	@echo "Installing dependencies..."
	go mod tidy
	go mod download
	@echo "Dependencies installed"

# Build for different platforms
build-linux:
	@echo "Building for Linux..."
	GOOS=linux GOARCH=amd64 go build -o terremoto-linux main.go

build-darwin:
	@echo "Building for macOS..."
	GOOS=darwin GOARCH=amd64 go build -o terremoto-darwin main.go

build-windows:
	@echo "Building for Windows..."
	GOOS=windows GOARCH=amd64 go build -o terremoto-windows.exe main.go

# Build all platforms
build-all: build-linux build-darwin build-windows
	@echo "All platform builds complete" 
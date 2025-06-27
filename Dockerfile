# Build stage
FROM golang:1.21-alpine AS builder

# Install git and ca-certificates (needed for go mod download)
RUN apk add --no-cache git ca-certificates

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build for ARMv7 (Raspberry Pi 3)
RUN CGO_ENABLED=0 GOOS=linux GOARCH=arm GOARM=7 go build -a -installsuffix cgo -o terremoto main.go

# Runtime stage
FROM alpine:latest

# Install ca-certificates for HTTPS requests
RUN apk --no-cache add ca-certificates

# Create non-root user
RUN addgroup -g 1001 -S terremoto && \
    adduser -u 1001 -S terremoto -G terremoto

WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /app/terremoto .

# Copy environment example
COPY --from=builder /app/env.example .

# Change ownership to non-root user
RUN chown -R terremoto:terremoto /app

# Switch to non-root user
USER terremoto

# Expose port (if needed for health checks)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Run the application
CMD ["./terremoto"] 
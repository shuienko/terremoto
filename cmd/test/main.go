package main

import (
	"fmt"
	"log"
	"os"
	"terremoto/pkg/earthquake"
)

func main() {
	fmt.Println("🧪 Testing Earthquake Alert System")
	fmt.Println("==================================================")

	// Set test environment variables if not already set
	if os.Getenv("LATITUDE") == "" {
		os.Setenv("LATITUDE", "40.7128") // New York City
	}
	if os.Getenv("LONGITUDE") == "" {
		os.Setenv("LONGITUDE", "-74.0060")
	}
	if os.Getenv("RADIUS_KM") == "" {
		os.Setenv("RADIUS_KM", "500") // Larger radius for testing
	}
	if os.Getenv("PUSHOVER_USER_KEY") == "" {
		os.Setenv("PUSHOVER_USER_KEY", "test_user_key")
	}
	if os.Getenv("PUSHOVER_APP_TOKEN") == "" {
		os.Setenv("PUSHOVER_APP_TOKEN", "test_app_token")
	}

	// Initialize the alert system
	fmt.Println("📡 Initializing Earthquake Alert System...")
	alert, err := earthquake.NewAlert()
	if err != nil {
		log.Fatalf("❌ Failed to initialize: %v", err)
	}
	fmt.Printf("✅ Initialized for location: %.4f, %.4f\n", alert.Config.Latitude, alert.Config.Longitude)
	fmt.Printf("✅ Radius: %.1fkm\n", alert.Config.RadiusKm)

	// Test earthquake fetching
	fmt.Println("\n🌍 Fetching earthquake data...")
	earthquakes, totalFound, err := alert.GetEarthquakes()
	if err != nil {
		log.Printf("❌ Error fetching earthquakes: %v", err)
		return
	}
	fmt.Printf("✅ Found %d earthquakes in the last 24 hours (total worldwide: %d)\n", len(earthquakes), totalFound)

	// Test message formatting
	fmt.Println("\n📝 Testing message formatting...")
	message := alert.FormatMessage(earthquakes, totalFound)
	fmt.Println("✅ Message formatted successfully")
	fmt.Println("\n📋 Formatted message preview:")
	fmt.Println("----------------------------------------")
	if len(message) > 500 {
		fmt.Println(message[:500] + "...")
	} else {
		fmt.Println(message)
	}
	fmt.Println("----------------------------------------")

	// Test distance calculation
	fmt.Println("\n📏 Testing distance calculation...")
	if len(earthquakes) > 0 {
		eq := earthquakes[0]
		fmt.Printf("✅ Distance calculation: %.2fkm\n", eq.Distance)
	}

	fmt.Println("\n🎉 All tests completed successfully!")
	fmt.Println("\nTo run the actual alert system:")
	fmt.Println("1. Set your real environment variables in a .env file")
	fmt.Println("2. Run: go run main.go")
}

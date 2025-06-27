package earthquake

import (
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"log"
	"math"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/joho/godotenv"
	"github.com/robfig/cron/v3"
)

// QuakeML structures for XML parsing
type QuakeML struct {
	XMLName         xml.Name        `xml:"quakeml"`
	EventParameters EventParameters `xml:"eventParameters"`
}

type EventParameters struct {
	Events []Event `xml:"event"`
}

type Event struct {
	PublicID    string      `xml:"publicID,attr"`
	Description Description `xml:"description"`
	Origin      Origin      `xml:"origin"`
	Magnitude   Magnitude   `xml:"magnitude"`
}

type Description struct {
	Text string `xml:"text"`
	Type string `xml:"type"`
}

type Origin struct {
	Longitude Longitude `xml:"longitude"`
	Latitude  Latitude  `xml:"latitude"`
	Time      Time      `xml:"time"`
}

type Longitude struct {
	Value float64 `xml:"value"`
}

type Latitude struct {
	Value float64 `xml:"value"`
}

type Time struct {
	Value string `xml:"value"`
}

type Magnitude struct {
	Mag Mag `xml:"mag"`
}

type Mag struct {
	Value float64 `xml:"value"`
}

// Earthquake represents a processed earthquake event
type Earthquake struct {
	Magnitude float64
	Latitude  float64
	Longitude float64
	Time      time.Time
	Place     string
	Distance  float64
}

// Config holds application configuration
type Config struct {
	Latitude         float64
	Longitude        float64
	RadiusKm         float64
	PushoverUserKey  string
	PushoverAppToken string
	AlertTime        string
	LogLevel         string
}

// Alert handles earthquake alert functionality
type Alert struct {
	Config Config
	Logger *log.Logger
}

// USGS GeoJSON structures
// Only the fields we need

type usgsFeatureCollection struct {
	Features []usgsFeature `json:"features"`
}

type usgsFeature struct {
	Properties usgsProperties `json:"properties"`
	Geometry   usgsGeometry   `json:"geometry"`
}

type usgsProperties struct {
	Mag   float64 `json:"mag"`
	Place string  `json:"place"`
	Time  int64   `json:"time"`
}

type usgsGeometry struct {
	Coordinates []float64 `json:"coordinates"` // [longitude, latitude, depth]
}

// EMSC JSON structures
// Only the fields we need
type emscFeatureCollection struct {
	Features []emscFeature `json:"features"`
}

type emscFeature struct {
	Properties emscProperties `json:"properties"`
	Geometry   emscGeometry   `json:"geometry"`
}

type emscProperties struct {
	Mag   float64 `json:"mag"`
	Place string  `json:"flynn_region"`
	Time  string  `json:"time"`
}

type emscGeometry struct {
	Coordinates []float64 `json:"coordinates"` // [longitude, latitude, depth]
}

// NewAlert creates a new earthquake alert instance
func NewAlert() (*Alert, error) {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Println("Warning: .env file not found, using system environment variables")
	}

	config := Config{
		Latitude:         getEnvFloat("LATITUDE", 0),
		Longitude:        getEnvFloat("LONGITUDE", 0),
		RadiusKm:         getEnvFloat("RADIUS_KM", 100),
		PushoverUserKey:  os.Getenv("PUSHOVER_USER_KEY"),
		PushoverAppToken: os.Getenv("PUSHOVER_APP_TOKEN"),
		AlertTime:        getEnvString("ALERT_TIME", "08:00"),
		LogLevel:         getEnvString("LOG_LEVEL", "INFO"),
	}

	// Validate required configuration
	if config.PushoverUserKey == "" || config.PushoverAppToken == "" {
		return nil, fmt.Errorf("PUSHOVER_USER_KEY and PUSHOVER_APP_TOKEN must be set")
	}

	// Setup logging
	logFile, err := os.OpenFile("earthquake_alerts.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return nil, fmt.Errorf("failed to open log file: %v", err)
	}

	logger := log.New(io.MultiWriter(os.Stdout, logFile), "", log.LstdFlags)
	logger.Printf("Initialized Earthquake Alert for location: %.4f, %.4f, radius: %.1fkm",
		config.Latitude, config.Longitude, config.RadiusKm)

	return &Alert{
		Config: config,
		Logger: logger,
	}, nil
}

// GetEarthquakes fetches earthquakes from EMSC for the last 24 hours
func (ea *Alert) GetEarthquakes() ([]Earthquake, int, error) {
	endTime := time.Now().UTC()
	startTime := endTime.Add(-24 * time.Hour)

	startStr := startTime.Format("2006-01-02T15:04:05")
	endStr := endTime.Format("2006-01-02T15:04:05")

	ea.Logger.Printf("Querying earthquakes from %s to %s", startStr, endStr)

	// Build EMSC query URL
	baseURL := "https://www.seismicportal.eu/fdsnws/event/1/query"
	params := url.Values{}
	params.Add("format", "json")
	params.Add("starttime", startStr)
	params.Add("endtime", endStr)
	params.Add("minmag", "0") // Get all earthquakes

	reqURL := baseURL + "?" + params.Encode()

	// Make HTTP request
	resp, err := http.Get(reqURL)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to fetch earthquake data: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		body, _ := io.ReadAll(resp.Body)
		return nil, 0, fmt.Errorf("API request failed with status %d: %s", resp.StatusCode, string(body))
	}

	// Parse JSON response
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to read response body: %v", err)
	}

	var fc emscFeatureCollection
	if err := json.Unmarshal(body, &fc); err != nil {
		return nil, 0, fmt.Errorf("failed to parse EMSC JSON: %v", err)
	}

	var earthquakes []Earthquake
	for _, feature := range fc.Features {
		if len(feature.Geometry.Coordinates) < 2 {
			continue
		}
		lat := feature.Geometry.Coordinates[1]
		lon := feature.Geometry.Coordinates[0]
		t, err := time.Parse("2006-01-02T15:04:05.000Z", feature.Properties.Time)
		if err != nil {
			t, err = time.Parse("2006-01-02T15:04:05Z", feature.Properties.Time)
			if err != nil {
				ea.Logger.Printf("Warning: failed to parse time: %v", err)
				t = time.Time{}
			}
		}
		eq := Earthquake{
			Magnitude: feature.Properties.Mag,
			Latitude:  lat,
			Longitude: lon,
			Place:     feature.Properties.Place,
			Time:      t,
		}
		// Calculate distance
		eq.Distance = ea.haversineDistance(ea.Config.Latitude, ea.Config.Longitude, eq.Latitude, eq.Longitude)
		earthquakes = append(earthquakes, eq)
	}

	totalFound := len(earthquakes)
	ea.Logger.Printf("Found %d earthquakes in the time period", totalFound)

	// Filter earthquakes within radius
	filtered := ea.filterByRadius(earthquakes)
	ea.Logger.Printf("Found %d earthquakes within %.1fkm radius", len(filtered), ea.Config.RadiusKm)

	return filtered, totalFound, nil
}

// filterByRadius filters earthquakes within the specified radius
func (ea *Alert) filterByRadius(earthquakes []Earthquake) []Earthquake {
	var filtered []Earthquake
	for _, eq := range earthquakes {
		if eq.Distance <= ea.Config.RadiusKm {
			filtered = append(filtered, eq)
		}
	}
	return filtered
}

// haversineDistance calculates distance between two points using Haversine formula
func (ea *Alert) haversineDistance(lat1, lon1, lat2, lon2 float64) float64 {
	const earthRadius = 6371 // Earth's radius in kilometers

	// Convert to radians
	lat1Rad := lat1 * (math.Pi / 180)
	lon1Rad := lon1 * (math.Pi / 180)
	lat2Rad := lat2 * (math.Pi / 180)
	lon2Rad := lon2 * (math.Pi / 180)

	// Haversine formula
	dlat := lat2Rad - lat1Rad
	dlon := lon2Rad - lon1Rad
	a := math.Sin(dlat/2)*math.Sin(dlat/2) + math.Cos(lat1Rad)*math.Cos(lat2Rad)*math.Sin(dlon/2)*math.Sin(dlon/2)
	c := 2 * math.Asin(math.Sqrt(a))

	return c * earthRadius
}

// FormatMessage formats earthquake data into a readable message
func (ea *Alert) FormatMessage(earthquakes []Earthquake, totalFound int) string {
	if len(earthquakes) == 0 {
		return fmt.Sprintf("🌍 No earthquakes detected in your area in the last 24 hours.\n📊 Total earthquakes found worldwide: %d", totalFound)
	}

	var sb strings.Builder
	sb.WriteString("⏰ Last 24 Hours\n")
	sb.WriteString(fmt.Sprintf("📍 Location: %.4f, %.4f\n", ea.Config.Latitude, ea.Config.Longitude))
	sb.WriteString(fmt.Sprintf("📏 Radius: %.1fkm\n", ea.Config.RadiusKm))
	sb.WriteString(fmt.Sprintf("📊 Found %d earthquake(s) in your area (out of %d total worldwide):\n\n", len(earthquakes), totalFound))

	// Limit to 10 earthquakes
	maxQuakes := 10
	if len(earthquakes) < maxQuakes {
		maxQuakes = len(earthquakes)
	}

	for i, eq := range earthquakes[:maxQuakes] {
		sb.WriteString(fmt.Sprintf("%d. Magnitude %.1f - %s\n", i+1, eq.Magnitude, eq.Place))
		sb.WriteString(fmt.Sprintf("   📅 %s\n", eq.Time.Format("2006-01-02 15:04 UTC")))
		sb.WriteString(fmt.Sprintf("   📍 Distance: %.1fkm\n\n", eq.Distance))
	}

	if len(earthquakes) > 10 {
		sb.WriteString(fmt.Sprintf("... and %d more earthquakes", len(earthquakes)-10))
	}

	return sb.String()
}

// SendPushoverNotification sends notification via Pushover
func (ea *Alert) SendPushoverNotification(message string) error {
	data := url.Values{}
	data.Set("token", ea.Config.PushoverAppToken)
	data.Set("user", ea.Config.PushoverUserKey)
	data.Set("message", message)
	data.Set("title", "🌍 Earthquake Alert")
	data.Set("priority", "0")
	data.Set("sound", "cosmic")

	resp, err := http.PostForm("https://api.pushover.net/1/messages.json", data)
	if err != nil {
		return fmt.Errorf("failed to send Pushover notification: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("Pushover API error: %d - %s", resp.StatusCode, string(body))
	}

	ea.Logger.Println("Pushover notification sent successfully")
	return nil
}

// RunDailyAlert runs the daily earthquake alert
func (ea *Alert) RunDailyAlert() {
	ea.Logger.Println("Starting daily earthquake alert check")

	earthquakes, totalFound, err := ea.GetEarthquakes()
	if err != nil {
		ea.Logger.Printf("Error getting earthquakes: %v", err)
		return
	}

	message := ea.FormatMessage(earthquakes, totalFound)

	if err := ea.SendPushoverNotification(message); err != nil {
		ea.Logger.Printf("Error sending notification: %v", err)
	} else {
		ea.Logger.Println("Daily earthquake alert completed successfully")
	}
}

// Start starts the scheduled alert system
func (ea *Alert) Start() error {
	c := cron.New(cron.WithSeconds())

	// Parse the alert time (format: HH:MM)
	timeParts := strings.Split(ea.Config.AlertTime, ":")
	if len(timeParts) != 2 {
		return fmt.Errorf("invalid alert time format: %s (expected HH:MM)", ea.Config.AlertTime)
	}

	hour, err := strconv.Atoi(timeParts[0])
	if err != nil {
		return fmt.Errorf("failed to parse hour from alert time: %v", err)
	}

	minute, err := strconv.Atoi(timeParts[1])
	if err != nil {
		return fmt.Errorf("failed to parse minute from alert time: %v", err)
	}

	// Validate time values
	if hour < 0 || hour > 23 {
		return fmt.Errorf("invalid hour: %d (must be 0-23)", hour)
	}
	if minute < 0 || minute > 59 {
		return fmt.Errorf("invalid minute: %d (must be 0-59)", minute)
	}

	// Schedule daily alert (cron format: second minute hour day month weekday)
	schedule := fmt.Sprintf("0 %d %d * * *", minute, hour)
	_, err = c.AddFunc(schedule, ea.RunDailyAlert)
	if err != nil {
		return fmt.Errorf("failed to schedule alert: %v", err)
	}

	ea.Logger.Printf("Earthquake alert system started. Daily alerts scheduled for %s", ea.Config.AlertTime)
	ea.Logger.Println("Press Ctrl+C to stop the application")

	// Run immediately if requested
	if os.Getenv("RUN_IMMEDIATELY") == "true" {
		ea.Logger.Println("Running immediate check...")
		ea.RunDailyAlert()
	}

	c.Start()
	select {} // Keep the application running
}

// Helper functions
func getEnvString(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvFloat(key string, defaultValue float64) float64 {
	if value := os.Getenv(key); value != "" {
		if f, err := strconv.ParseFloat(value, 64); err == nil {
			return f
		}
	}
	return defaultValue
}

package main

import (
	"log"
	"terremoto/pkg/earthquake"
)

func main() {
	alert, err := earthquake.NewAlert()
	if err != nil {
		log.Fatalf("Failed to initialize earthquake alert: %v", err)
	}

	if err := alert.Start(); err != nil {
		log.Fatalf("Failed to start earthquake alert: %v", err)
	}
}

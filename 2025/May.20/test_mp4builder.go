package main

import (
	"fmt"
	"genuary/may20/mp4builder"
	"log"
	"os"
	"path/filepath"
)

func test() {
	framesDir := filepath.Join("_output", "frames")
	outputDir := "_output"

	// Check if frames directory exists
	if _, err := os.Stat(framesDir); os.IsNotExist(err) {
		log.Fatalf("Frames directory does not exist: %s", framesDir)
	}

	// Create MP4 configuration
	config := mp4builder.Config{
		FramesFolder: framesDir,
		OutputFolder: outputDir,
		TempFolder:   filepath.Join(outputDir, "temp"),
		OutputVideo:  filepath.Join(outputDir, "test-output.mp4"),
		FPS:          16,
	}

	// Create MP4 from frames
	fmt.Println("Creating MP4 video from frames...")
	err := mp4builder.CreateMP4FromFrames(config)
	if err != nil {
		log.Fatalf("Failed to create MP4: %v", err)
	}

	fmt.Println("MP4 video created successfully!")
}

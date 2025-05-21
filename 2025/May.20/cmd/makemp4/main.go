package main

import (
	"flag"
	"fmt"
	"genuary/may20/mp4builder"
	"os"
	"path/filepath"
)

func main() {
	// Command line flags
	framesFolder := flag.String("frames", "", "Path to folder containing SVG frames")
	outputVideo := flag.String("output", "", "Output MP4 file path")
	fps := flag.Int("fps", 16, "Frames per second")

	flag.Parse()

	// Validate required flags
	if *framesFolder == "" || *outputVideo == "" {
		fmt.Println("Error: Both frames folder and output path are required")
		fmt.Println("Usage:")
		flag.PrintDefaults()
		os.Exit(1)
	}

	// Ensure frames folder exists
	if _, err := os.Stat(*framesFolder); os.IsNotExist(err) {
		fmt.Printf("Error: Frames folder does not exist: %s\n", *framesFolder)
		os.Exit(1)
	}

	// Create temporary folder
	outputDir := filepath.Dir(*outputVideo)
	tempFolder := filepath.Join(outputDir, "temp")

	// Create configuration
	config := mp4builder.Config{
		FramesFolder: *framesFolder,
		OutputFolder: outputDir,
		TempFolder:   tempFolder,
		OutputVideo:  *outputVideo,
		FPS:          *fps,
	}

	// Create MP4 from frames
	err := mp4builder.CreateMP4FromFrames(config)
	if err != nil {
		fmt.Printf("Error creating MP4: %v\n", err)
		os.Exit(1)
	}
}

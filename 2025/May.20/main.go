package main

import (
	"fmt"
	"genuary/may20/gensvg"
	"genuary/may20/utils"
	"log"
	"os"
	"path/filepath"
)

func main() {
	// Ensure directories exists
	outputDir := "output"
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		log.Fatalf("Failed to create output directory: %v", err)
	}

	// Generate and save equilateral septagon
	svgContent := gensvg.Septagon()
	outputPath := filepath.Join(outputDir, "septagon.svg")
	if err := os.WriteFile(outputPath, []byte(svgContent), 0644); err != nil {
		log.Fatalf("Failed to write SVG file: %v", err)
	}
	fmt.Printf("SVG with equilateral septagon saved to %s\n", outputPath)

	// Generate star SVG content
	starSVGContent := gensvg.Star()

	// Save star SVG to file
	starOutputPath := filepath.Join(outputDir, "star.svg")
	if err := os.WriteFile(starOutputPath, []byte(starSVGContent), 0644); err != nil {
		log.Fatalf("Failed to write star SVG file: %v", err)
	}
	fmt.Printf("SVG with star pattern saved to %s\n", starOutputPath)

	// Generate and save complex star
	complexSVGContent := gensvg.ComplexStar()
	complexOutputPath := filepath.Join(outputDir, "complex.svg")
	if err := os.WriteFile(complexOutputPath, []byte(complexSVGContent), 0644); err != nil {
		log.Fatalf("Failed to write complex SVG file: %v", err)
	}
	fmt.Printf("SVG with complex pattern saved to %s\n", complexOutputPath)

	// Generate animation frames
	{
		// scope braces for folding porpoises 🐬
		totalFrames := 16
		fmt.Println("Generating animation frames...")
		// Create frames directory
		framesDir := filepath.Join(outputDir, "frames")
		if err := os.MkdirAll(framesDir, 0755); err != nil {
			log.Fatalf("Failed to create frames directory: %v", err)
		}

		for i := 0; i < totalFrames; i++ {
			// Generate frame with noise level based on frame number
			frameContent := utils.GenerateNoiseFrame(i, totalFrames)

			// Save frame to file
			framePath := filepath.Join(framesDir, fmt.Sprintf("frame_%02d.svg", i))
			if err := os.WriteFile(framePath, []byte(frameContent), 0644); err != nil {
				log.Fatalf("Failed to write frame file: %v", err)
			}

			fmt.Printf("Frame %d/%d saved to %s\n", i+1, totalFrames, framePath)
		}
		fmt.Println(utils.TimeInfo())
	}
}

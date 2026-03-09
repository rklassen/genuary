package main

import (
	"fmt"
	"genuary/may20/gensvg"
	"genuary/may20/mp4builder"
	"genuary/may20/utils"
	"log"
	"os"
	"path/filepath"
)

func main() {
	// Ensure directories exists
	outputDir := "_output"
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		log.Fatalf("Failed to create output directory: %v", err)
	}

	// septagon svg
	svgContent := gensvg.Septagon()
	outputPath := filepath.Join(outputDir, "septagon.svg")
	if err := os.WriteFile(outputPath, []byte(svgContent), 0644); err != nil {
		log.Fatalf("Failed to write SVG file: %v", err)
	}
	fmt.Printf("SVG with equilateral septagon saved to %s\n", outputPath)

	// star svg
	starSVGContent := gensvg.Star()
	starOutputPath := filepath.Join(outputDir, "star.svg")
	if e := os.WriteFile(starOutputPath, []byte(starSVGContent), 0644); e != nil {
		log.Fatalf("Failed to write star SVG file: %v", e)
	}
	fmt.Printf("SVG with star pattern saved to %s\n", starOutputPath)

	// complex star
	complexOutputPath := filepath.Join(outputDir, "complex.svg")
	if e := os.WriteFile(complexOutputPath,
		[]byte(gensvg.ComplexStar()),
		0644); e != nil {
		log.Fatalf("Failed to write complex SVG file: %v", e)
	}
	fmt.Printf("SVG with complex pattern saved to %s\n", complexOutputPath)

	// Generate animation frames, scope for folding porpoises 🐬 only
	{
		totalFrames := 50
		fmt.Println("Generating animation frames...")

		// Create frames directory
		framesDir := filepath.Join(outputDir, "frames")
		if err := os.MkdirAll(framesDir, 0755); err != nil {
			log.Fatalf("Failed to create frames directory: %v", err)
		}

		// Generate noise vectors for animation (4 vectors per segment * 7 segments * 2 septagons = 56 vectors)
		sides := 7                       // Septagon has 7 sides
		requiredVectors := 4 * sides * 2 // 4 noise vectors per segment, 2 septagons (original + inverted)
		noiseVectors := make([][2]float64, requiredVectors)

		// Generate random noise vectors with lengths between 0.1 and 1.0
		for i := range noiseVectors {
			noiseVectors[i] = utils.GenerateNoiseVector(0.1, 1.0)
		}

		for i := range totalFrames {
			frameContent := utils.GenerateNoiseFrame(i, totalFrames, noiseVectors)
			framePath := filepath.Join(framesDir, fmt.Sprintf("frame_%02d.svg", i))
			if e := os.WriteFile(framePath, []byte(frameContent), 0644); e != nil {
				log.Fatalf("Failed to write frame file: %v", e)
			}
			fmt.Printf("Frame %d/%d saved to %s\n", i+1, totalFrames, framePath)
		}
		fmt.Println(utils.TimeInfo())

		// Create MP4 from the generated frames
		fmt.Println("Creating MP4 video from frames...")
		videoConfig := mp4builder.Config{
			FramesFolder: framesDir,
			OutputFolder: outputDir,
			TempFolder:   filepath.Join(outputDir, "png"),
			OutputVideo:  filepath.Join(outputDir, "lawful-chaotic.mp4"),
			FPS:          60,
		}

		if err := mp4builder.CreateMP4FromFrames(videoConfig); err != nil {
			log.Fatalf("Failed to create MP4: %v", err)
		}
	}
}

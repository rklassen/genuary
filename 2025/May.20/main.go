package main

import (
	"fmt"
	"genuary/may20/utils"
	"log"
	"math"
	"math/rand"
	"os"
	"path/filepath"
	"time"
)

func main() {
	// Seed random number generator
	rand.Seed(time.Now().UnixNano())

	// Ensure output directory exists
	outputDir := "output"
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		log.Fatalf("Failed to create output directory: %v", err)
	}

	// Ensure frames directory exists
	framesDir := filepath.Join(outputDir, "frames")
	if err := os.MkdirAll(framesDir, 0755); err != nil {
		log.Fatalf("Failed to create frames directory: %v", err)
	}

	// Generate SVG content for equilateral septagon
	svgContent := generateSeptagolSVG()

	// Save SVG to file
	outputPath := filepath.Join(outputDir, "septagon.svg")
	if err := os.WriteFile(outputPath, []byte(svgContent), 0644); err != nil {
		log.Fatalf("Failed to write SVG file: %v", err)
	}

	fmt.Printf("SVG with equilateral septagon saved to %s\n", outputPath)

	// Generate star SVG content
	starSVGContent := generateStarSVG()

	// Save star SVG to file
	starOutputPath := filepath.Join(outputDir, "star.svg")
	if err := os.WriteFile(starOutputPath, []byte(starSVGContent), 0644); err != nil {
		log.Fatalf("Failed to write star SVG file: %v", err)
	}

	fmt.Printf("SVG with star pattern saved to %s\n", starOutputPath)

	// Generate complex SVG content
	complexSVGContent := generateComplexSVG()

	// Save complex SVG to file
	complexOutputPath := filepath.Join(outputDir, "complex.svg")
	if err := os.WriteFile(complexOutputPath, []byte(complexSVGContent), 0644); err != nil {
		log.Fatalf("Failed to write complex SVG file: %v", err)
	}

	fmt.Printf("SVG with complex pattern saved to %s\n", complexOutputPath)

	// Generate animation frames
	totalFrames := 16
	fmt.Println("Generating animation frames...")

	for i := 0; i < totalFrames; i++ {
		// Generate frame with noise level based on frame number
		frameContent := generateNoiseFrame(i, totalFrames)

		// Save frame to file
		framePath := filepath.Join(framesDir, fmt.Sprintf("frame_%02d.svg", i))
		if err := os.WriteFile(framePath, []byte(frameContent), 0644); err != nil {
			log.Fatalf("Failed to write frame file: %v", err)
		}

		fmt.Printf("Frame %d/%d saved to %s\n", i+1, totalFrames, framePath)
	}
	fmt.Println(utils.TimeInfo())
}

// generateSeptagolSVG generates a 256x256 SVG with an equilateral septagon
func generateSeptagolSVG() string {
	const (
		width, height    = 256, 256
		centerX, centerY = 128, 128
		sides            = 7 // Septagon has 7 sides
	)
	radius := float64(110) // Slightly less than half the width for margin

	// Start SVG content
	svg := fmt.Sprintf(`<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">
	<rect width="100%%" height="100%%" fill="#f0f0f0"/>
	<polygon points="`, width, height)

	// Calculate the points of the equilateral septagon
	points := ""
	for i := 0; i < sides; i++ {
		// Calculate angle and point coordinates
		angle := 2 * math.Pi * float64(i) / float64(sides)
		// Rotate by -math.Pi/2 to start at the top
		angle -= math.Pi / 2
		x := float64(centerX) + radius*math.Cos(angle)
		y := float64(centerY) + radius*math.Sin(angle)
		points += fmt.Sprintf("%.2f,%.2f ", x, y)
	}

	// Complete SVG content
	svg += points + `" fill="#4a90e2" stroke="#2c3e50" stroke-width="2"/>
</svg>`

	return svg
}

// generateStarSVG generates a 256x256 SVG with a star pattern based on septagon
func generateStarSVG() string {
	const (
		width, height    = 256, 256
		centerX, centerY = 128, 128
		sides            = 7   // Septagon has 7 sides
		ratio            = 0.6 // Ratio for scaling middle points inward
	)
	radius := float64(110) // Slightly less than half the width for margin

	// Generate the vertices of the regular septagon
	vertices := make([][2]float64, sides)
	for i := 0; i < sides; i++ {
		angle := 2 * math.Pi * float64(i) / float64(sides)
		// Rotate by -math.Pi/2 to start at the top
		angle -= math.Pi / 2
		x := float64(centerX) + radius*math.Cos(angle)
		y := float64(centerY) + radius*math.Sin(angle)
		vertices[i] = [2]float64{x, y}
	}

	// Start SVG content
	svg := fmt.Sprintf(`<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">
	<rect width="100%%" height="100%%" fill="#f0f0f0"/>
	<path d="`, width, height)

	// Create the star pattern by replacing each edge with a three-point linestring
	pathData := ""
	for i := 0; i < sides; i++ {
		start := vertices[i]
		end := vertices[(i+1)%sides] // Wrap around to the first vertex at the end

		// Calculate midpoint
		midX := (start[0] + end[0]) / 2
		midY := (start[1] + end[1]) / 2

		// Scale midpoint toward the center (origin)
		scaledMidX := float64(centerX) + ratio*(midX-float64(centerX))
		scaledMidY := float64(centerY) + ratio*(midY-float64(centerY))

		// Add to path
		if i == 0 {
			pathData += fmt.Sprintf("M%.2f,%.2f ", start[0], start[1])
		}
		pathData += fmt.Sprintf("L%.2f,%.2f L%.2f,%.2f ", scaledMidX, scaledMidY, end[0], end[1])
	}
	// Close the path
	pathData += "Z"

	// Complete SVG content
	svg += pathData + `" fill="#4a90e2" stroke="none"/>
</svg>`

	return svg
}

// generateComplexSVG generates a 256x256 SVG with a star pattern and its y-inverted copy
func generateComplexSVG() string {
	const (
		width, height    = 256, 256
		centerX, centerY = 128, 128
		sides            = 7   // Septagon has 7 sides
		ratio            = 0.6 // Ratio for scaling middle points inward
	)
	radius := float64(110) // Slightly less than half the width for margin

	// Generate the vertices of the regular septagon
	vertices := make([][2]float64, sides)
	for i := 0; i < sides; i++ {
		angle := 2 * math.Pi * float64(i) / float64(sides)
		// Rotate by -math.Pi/2 to start at the top
		angle -= math.Pi / 2
		x := float64(centerX) + radius*math.Cos(angle)
		y := float64(centerY) + radius*math.Sin(angle)
		vertices[i] = [2]float64{x, y}
	}

	// Start SVG content
	svg := fmt.Sprintf(`<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">
	<rect width="100%%" height="100%%" fill="#f0f0f0"/>`, width, height)

	// Create the original star pattern
	pathData := createStarPath(vertices, centerX, centerY, ratio)
	svg += fmt.Sprintf(`
	<path d="%s" fill="#4a90e2" stroke="none"/>`, pathData)

	// Create the y-inverted star pattern
	invertedVertices := make([][2]float64, sides)
	for i, v := range vertices {
		// Invert Y-coordinate (2*centerY - y flips around the horizontal center line)
		invertedVertices[i] = [2]float64{v[0], float64(2*centerY) - v[1]}
	}

	invertedPathData := createStarPath(invertedVertices, centerX, centerY, ratio)
	svg += fmt.Sprintf(`
	<path d="%s" fill="#e24a90" stroke="none"/>
</svg>`, invertedPathData)

	return svg
}

// Helper function to create a star path from vertices
func createStarPath(vertices [][2]float64, centerX, centerY int, ratio float64) string {
	sides := len(vertices)
	pathData := ""

	for i := 0; i < sides; i++ {
		start := vertices[i]
		end := vertices[(i+1)%sides] // Wrap around to the first vertex at the end

		// Calculate midpoint
		midX := (start[0] + end[0]) / 2
		midY := (start[1] + end[1]) / 2

		// Scale midpoint toward the center (origin)
		scaledMidX := float64(centerX) + ratio*(midX-float64(centerX))
		scaledMidY := float64(centerY) + ratio*(midY-float64(centerY))

		// Add to path
		if i == 0 {
			pathData += fmt.Sprintf("M%.2f,%.2f ", start[0], start[1])
		}
		pathData += fmt.Sprintf("L%.2f,%.2f L%.2f,%.2f ", scaledMidX, scaledMidY, end[0], end[1])
	}
	// Close the path
	pathData += "Z"

	return pathData
}

// generateNoiseFrame generates a frame for the animation with specified noise level
func generateNoiseFrame(frameNumber int, totalFrames int) string {
	const (
		width, height    = 256, 256
		centerX, centerY = 128, 128
		sides            = 7   // Septagon has 7 sides
		ratio            = 0.6 // Ratio for scaling middle points inward
	)
	noiseRatio := float64(totalFrames-frameNumber-1) / float64(totalFrames-1) // 100% at frame 0, 0% at final frame
	radius := float64(110)                                                    // Slightly less than half the width for margin
	noiseScale := ratio * 0.5                                                 // Maximum noise distance is half of the ratio

	// Generate the vertices of the regular septagon
	vertices := make([][2]float64, sides)
	for i := 0; i < sides; i++ {
		angle := 2 * math.Pi * float64(i) / float64(sides)
		// Rotate by -math.Pi/2 to start at the top
		angle -= math.Pi / 2
		x := float64(centerX) + radius*math.Cos(angle)
		y := float64(centerY) + radius*math.Sin(angle)
		vertices[i] = [2]float64{x, y}
	}

	// Generate random noise vectors for each vertex
	noiseVectors := make([][2]float64, sides)
	for i := 0; i < sides; i++ {
		// Random angle between 0 and 2π
		theta := 2 * math.Pi * rand.Float64()
		// Noise vector with length noiseScale
		nx := noiseScale * math.Cos(theta)
		ny := noiseScale * math.Sin(theta)
		noiseVectors[i] = [2]float64{nx, ny}
	}

	// Apply noise to vertices based on noise ratio
	noisyVertices := make([][2]float64, sides)
	for i := 0; i < sides; i++ {
		nx, ny := noiseVectors[i][0], noiseVectors[i][1]
		noisyVertices[i] = [2]float64{
			vertices[i][0] + nx*noiseRatio*100, // Scale by 100 for significant visible effect
			vertices[i][1] + ny*noiseRatio*100,
		}
	}

	// Create inverted noisy vertices
	invertedNoisyVertices := make([][2]float64, sides)
	for i, v := range noisyVertices {
		// Invert Y-coordinate (2*centerY - y flips around the horizontal center line)
		invertedNoisyVertices[i] = [2]float64{v[0], float64(2*centerY) - v[1]}
	}

	// Start SVG content
	svg := fmt.Sprintf(`<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">
	<rect width="100%%" height="100%%" fill="#f0f0f0"/>`, width, height)

	// Draw the original noisy star
	svg += createBrokenStarSVG(noisyVertices, centerX, centerY, ratio, "#4a90e2")

	// Draw the y-inverted noisy star
	svg += createBrokenStarSVG(invertedNoisyVertices, centerX, centerY, ratio, "#e24a90")

	svg += `
</svg>`

	return svg
}

// createBrokenStarSVG creates an SVG path for a star with broken edges
func createBrokenStarSVG(vertices [][2]float64, centerX, centerY int, ratio float64, color string) string {
	sides := len(vertices)
	svg := ""

	// Draw each edge as a separate path
	for i := 0; i < sides; i++ {
		start := vertices[i]
		end := vertices[(i+1)%sides] // Wrap around to the first vertex at the end

		// Calculate midpoint
		midX := (start[0] + end[0]) / 2
		midY := (start[1] + end[1]) / 2

		// Scale midpoint toward the center (origin)
		scaledMidX := float64(centerX) + ratio*(midX-float64(centerX))
		scaledMidY := float64(centerY) + ratio*(midY-float64(centerY))

		// Create a path for this edge
		pathData := fmt.Sprintf("M%.2f,%.2f L%.2f,%.2f L%.2f,%.2f",
			start[0], start[1],
			scaledMidX, scaledMidY,
			end[0], end[1])

		svg += fmt.Sprintf(`
	<path d="%s" fill="none" stroke="%s" stroke-width="2"/>`, pathData, color)
	}

	return svg
}

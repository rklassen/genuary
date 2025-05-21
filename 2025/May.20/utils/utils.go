package utils

import (
	"fmt"
	"math"
	"math/rand"
	"time"
)

// TimeInfo returns a formatted string with the current date and time
func TimeInfo() string {
	now := time.Now()
	return fmt.Sprintf("Current time: %s", now.Format(time.RFC1123))
}

// GenerateID creates a simple unique identifier based on timestamp
func GenerateID() string {
	return fmt.Sprintf("genuary-%d", time.Now().UnixNano())
}

// CreateStarPath creates a star path from vertices
func CreateStarPath(vertices [][2]float64, centerX, centerY int, ratio float64) string {
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

// GenerateNoiseFrame generates a frame for the animation with specified noise level
func GenerateNoiseFrame(frameNumber int, totalFrames int) string {
	const (
		width, height    = 256, 256
		centerX, centerY = 128, 128
		sides            = 7          // Septagon has 7 sides
		ratio            = 0.6        // Ratio for scaling middle points inward
		radius           = 110.0      // Slightly less than half the width for margin
		noiseL, noiseH   = 50.0, 80.0 // Noise range
	)
	noiseRatio := float64(frameNumber) / float64(totalFrames-1) // 0% at frame 0, 100% at final frame

	// Generate the vertices of the regular septagon
	vertices := make([][2]float64, sides)
	for i := range sides {
		angle := 2 * math.Pi * float64(i) / float64(sides)
		angle -= math.Pi / 2 // half rotation to point up
		x := float64(centerX) + radius*math.Cos(angle)
		y := float64(centerY) + radius*math.Sin(angle)
		vertices[i] = [2]float64{x, y}
	}

	// Start SVG content
	svg := fmt.Sprintf(`<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">
	<rect width="100%%" height="100%%" fill="#f0f0f0"/>`, width, height)

	// Create star segments with noise for the original star
	svg += CreateNoisyStarSegments(vertices, centerX, centerY, ratio, "#4a90e2", noiseRatio, noiseL, noiseH)

	// Create inverted vertices
	invertedVertices := make([][2]float64, sides)
	for i, v := range vertices {
		// Invert Y-coordinate (2*centerY - y flips around the horizontal center line)
		invertedVertices[i] = [2]float64{v[0], float64(2*centerY) - v[1]}
	}

	// Create star segments with noise for the inverted star
	svg += CreateNoisyStarSegments(invertedVertices, centerX, centerY, ratio, "#e24a90", noiseRatio, noiseL, noiseH)

	svg += `
</svg>`

	return svg
}

// CreateNoisyStarSegments creates SVG paths for star segments with noise applied to each point
func CreateNoisyStarSegments(
	vertices [][2]float64,
	centerX,
	centerY int,
	ratio float64,
	color string,
	noiseRatio float64,
	noiseL float64,
	noiseH float64,
) string {
	sides := len(vertices)
	svg := ""

	// Process each edge of the septagon
	for i := 0; i < sides; i++ {
		cleanStart := vertices[i]
		cleanEnd := vertices[(i+1)%sides] // Wrap around to the first vertex at the end

		// Calculate midpoint
		midX := (cleanStart[0] + cleanEnd[0]) / 2
		midY := (cleanStart[1] + cleanEnd[1]) / 2

		// Scale midpoint toward the center (origin)
		cleanScaledMidX := float64(centerX) + ratio*(midX-float64(centerX))
		cleanScaledMidY := float64(centerY) + ratio*(midY-float64(centerY))

		// Split the three-point linestring into two separate two-point segments

		// First segment: start to mid
		// Generate noise for the two points in first segment
		startNoise1 := GenerateNoiseVector(noiseL, noiseH)
		midNoise1 := GenerateNoiseVector(noiseL, noiseH)

		// Apply noise to each point
		noisyStart1 := [2]float64{
			cleanStart[0] + startNoise1[0]*noiseRatio*100,
			cleanStart[1] + startNoise1[1]*noiseRatio*100,
		}

		noisyMid1 := [2]float64{
			cleanScaledMidX + midNoise1[0]*noiseRatio*100,
			cleanScaledMidY + midNoise1[1]*noiseRatio*100,
		}

		// Create a path for the first segment
		pathData1 := fmt.Sprintf("M%.2f,%.2f L%.2f,%.2f",
			noisyStart1[0], noisyStart1[1],
			noisyMid1[0], noisyMid1[1])

		svg += fmt.Sprintf(`
	<path d="%s" fill="none" stroke="#000" stroke-width="2"/>`, pathData1)

		// Second segment: mid to end
		// Generate noise for the two points in second segment
		midNoise2 := GenerateNoiseVector(noiseL, noiseH)
		endNoise2 := GenerateNoiseVector(noiseL, noiseH)

		// Apply noise to each point
		noisyMid2 := [2]float64{
			cleanScaledMidX + midNoise2[0]*noiseRatio*100,
			cleanScaledMidY + midNoise2[1]*noiseRatio*100,
		}

		noisyEnd2 := [2]float64{
			cleanEnd[0] + endNoise2[0]*noiseRatio*100,
			cleanEnd[1] + endNoise2[1]*noiseRatio*100,
		}

		// Create a path for the second segment
		pathData2 := fmt.Sprintf("M%.2f,%.2f L%.2f,%.2f",
			noisyMid2[0], noisyMid2[1],
			noisyEnd2[0], noisyEnd2[1])

		svg += fmt.Sprintf(`
	<path d="%s" fill="none" stroke="#000" stroke-width="2"/>`, pathData2)
	}

	return svg
}

// GenerateNoiseVector generates a random noise vector with a specified scale
func GenerateNoiseVector(
	noiseLowerBound float64,
	noiseUpperBound float64,
) [2]float64 {
	noiseScale := noiseLowerBound + rand.Float64()*(noiseUpperBound-noiseLowerBound)

	// Random angle between 0 and 2π
	theta := 2 * math.Pi * rand.Float64()
	// Noise vector with length noiseScale
	nx := noiseScale * math.Cos(theta)
	ny := noiseScale * math.Sin(theta)
	return [2]float64{nx, ny}
}

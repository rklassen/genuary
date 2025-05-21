package gensvg

import (
	"fmt"
	"genuary/may20/utils"
	"math"
)

// GenSeptagon generates a 256x256 SVG with an equilateral septagon
func Septagon() string {
	const (
		width, height    = 256, 256
		centerX, centerY = 128, 128
		sides            = 7     // Septagon has 7 sides
		radius           = 110.0 // Slightly less than half the width for margin
	)

	// SVG header
	svg := fmt.Sprintf(`<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">
	<rect width="100%%" height="100%%" fill="#f0f0f0"/>
	<polygon points="`, width, height)

	// Calculate the points of the equilateral septagon
	points := ""
	for index := range sides {
		angle := 2 * math.Pi * float64(index) / float64(sides)
		angle -= math.Pi / 2 // half rotation so star points up
		x := float64(centerX) + radius*math.Cos(angle)
		y := float64(centerY) + radius*math.Sin(angle)
		points += fmt.Sprintf("%.2f,%.2f ", x, y)
	}

	// finish svg codes
	svg += points + `" fill="#4a90e2" stroke="#2c3e50" stroke-width="2"/>
</svg>`

	return svg
}

// GenerateStar generates a 256x256 SVG with a star pattern based on septagon
func Star() string {
	const (
		width, height    = 256, 256
		centerX, centerY = 128, 128
		sides            = 7     // septagon
		ratio            = 0.6   // Ratio for scaling midpoints inward
		radius           = 110.0 // Slightly less than half the width for margin
	)

	// Generate the vertices of the regular septagon
	vertices := make([][2]float64, sides)
	for index := range vertices {
		angle := 2 * math.Pi * float64(index) / float64(sides)
		angle -= math.Pi / 2 // Start at the top
		x := float64(centerX) + radius*math.Cos(angle)
		y := float64(centerY) + radius*math.Sin(angle)
		vertices[index] = [2]float64{x, y}
	}

	// Start SVG content
	svg := fmt.Sprintf(`<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">
	<rect width="100%%" height="100%%" fill="#f0f0f0"/>
	<path d="`, width, height)

	// Create the star pattern by inserting a midpoint to each end then scaling towards origin
	pathData := ""
	for i := 0; i < sides; i++ {

		start := vertices[i]
		end := vertices[(i+1)%sides] // Wrap around to the first vertex at the end

		// insert midpoint and scale toward the center (origin)
		midX := (start[0] + end[0]) / 2
		midY := (start[1] + end[1]) / 2
		scaledMidX := float64(centerX) + ratio*(midX-float64(centerX))
		scaledMidY := float64(centerY) + ratio*(midY-float64(centerY))
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

// GenerateComplexStar generates a 256x256 SVG with a star pattern and its y-inverted copy
func ComplexStar() string {
	const (
		width, height    = 256, 256
		centerX, centerY = 128, 128
		sides            = 7     // septagon
		ratio            = 0.6   // Ratio for scaling mdidpoints inward
		radius           = 110.0 // Slightly less than half the width for margin
	)

	// Generate the vertices of the regular septagon
	vertices := make([][2]float64, sides)
	for i := range sides {
		angle := 2 * math.Pi * float64(i) / float64(sides)
		angle -= math.Pi / 2 // Start at the top
		x := float64(centerX) + radius*math.Cos(angle)
		y := float64(centerY) + radius*math.Sin(angle)
		vertices[i] = [2]float64{x, y}
	}

	// svg header
	svg := fmt.Sprintf(`<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">
	<rect width="100%%" height="100%%" fill="#f0f0f0"/>`, width, height)

	// default star
	pathData := utils.CreateStarPath(vertices, centerX, centerY, ratio)
	svg += fmt.Sprintf(`
	<path d="%s" fill="#4a90e2" stroke="none"/>`, pathData)

	// inverted star
	invertedVertices := make([][2]float64, sides)
	for i := range sides {
		v := vertices[i]
		invertedVertices[i] = [2]float64{v[0], float64(2*centerY) - v[1]}
	}

	// svg footer
	invertedPathData := utils.CreateStarPath(invertedVertices, centerX, centerY, ratio)
	svg += fmt.Sprintf(`
	<path d="%s" fill="#e24a90" stroke="none"/>
</svg>`, invertedPathData)

	return svg
}

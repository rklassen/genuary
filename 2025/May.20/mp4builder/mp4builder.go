package mp4builder

import (
	"bytes"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/srwiley/oksvg"
	"github.com/srwiley/rasterx"
)

// ConvertSvgToPng converts an SVG file to PNG using oksvg and rasterx
func ConvertSvgToPng(svgPath, pngPath string) error {
	// Read and parse the SVG file
	icon, err := oksvg.ReadIcon(svgPath, oksvg.StrictErrorMode)
	if err != nil {
		return fmt.Errorf("error reading SVG: %w", err)
	}

	// Get the dimensions for the output image
	w, h := int(icon.ViewBox.W), int(icon.ViewBox.H)
	if w == 0 || h == 0 {
		// Set default size if ViewBox is not set
		w, h = 800, 800
		icon.SetTarget(0, 0, float64(w), float64(h))
	}

	// Create a new RGBA image
	img := image.NewRGBA(image.Rect(0, 0, w, h))

	// Fill the background with #556 color
	bg := color.RGBA{0x55, 0x55, 0x66, 0xff} // #556 with full opacity
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			img.Set(x, y, bg)
		}
	}

	// Create the rasterizer
	scanner := rasterx.NewScannerGV(w, h, img, img.Bounds())
	raster := rasterx.NewDasher(w, h, scanner)

	// Render the SVG to the image
	icon.Draw(raster, 1.0)

	// Create output file
	outFile, err := os.Create(pngPath)
	if err != nil {
		return fmt.Errorf("error creating output file: %w", err)
	}
	defer outFile.Close()

	// Encode the image as PNG
	err = png.Encode(outFile, img)
	if err != nil {
		return fmt.Errorf("error encoding PNG: %w", err)
	}

	return nil
}

// Config holds configuration for the video creation process
type Config struct {
	FramesFolder string
	OutputFolder string
	TempFolder   string
	OutputVideo  string
	FPS          int
}

// CreateMP4FromFrames converts SVG frames to PNG and creates an MP4 video
func CreateMP4FromFrames(config Config) error {
	// Create output and temp directories if they don't exist
	if err := os.MkdirAll(config.OutputFolder, 0755); err != nil {
		return fmt.Errorf("failed to create output directory: %w", err)
	}

	// Make sure temp folder is created with absolute path to avoid any path issues
	absTemp, err := filepath.Abs(config.TempFolder)
	if err != nil {
		return fmt.Errorf("failed to get absolute path for temp folder: %w", err)
	}
	config.TempFolder = absTemp

	if err := os.MkdirAll(config.TempFolder, 0755); err != nil {
		return fmt.Errorf("failed to create temp directory: %w", err)
	}

	// Get all SVG files from frames folder
	files, err := os.ReadDir(config.FramesFolder)
	if err != nil {
		return fmt.Errorf("error reading frames directory: %w", err)
	}

	// Filter for SVG files and sort them alphabetically
	var svgFiles []string
	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(strings.ToLower(file.Name()), ".svg") {
			svgFiles = append(svgFiles, file.Name())
		}
	}
	sort.Strings(svgFiles)

	if len(svgFiles) == 0 {
		return fmt.Errorf("no SVG files found in the frames folder")
	}

	fmt.Printf("Found %d SVG files. Converting to PNG...\n", len(svgFiles))

	// Convert SVGs to PNGs
	// First create a map to extract frame number from SVG filenames
	frameMap := make(map[string]int)
	frameOrder := make([]string, len(svgFiles))

	// Extract frame numbers from filenames (assuming they follow frame_XX.svg pattern)
	for i, svgFile := range svgFiles {
		frameOrder[i] = svgFile
		// Try to parse the frame number from the filename
		var frameNum int
		if n, err := fmt.Sscanf(svgFile, "frame_%d.svg", &frameNum); n == 1 && err == nil {
			frameMap[svgFile] = frameNum
		} else {
			// If we can't parse a number, use the index as a fallback
			frameMap[svgFile] = i
		}
	}

	// Sort SVG files by their numeric frame number
	sort.Slice(frameOrder, func(i, j int) bool {
		return frameMap[frameOrder[i]] < frameMap[frameOrder[j]]
	})

	// Convert SVGs to PNGs with sequential numbering
	for i, svgFile := range frameOrder {
		svgPath := filepath.Join(config.FramesFolder, svgFile)
		// Create PNG filename with padding for proper sorting
		pngFile := fmt.Sprintf("frame_%04d.png", i)
		pngPath := filepath.Join(config.TempFolder, pngFile)

		err := ConvertSvgToPng(svgPath, pngPath)
		if err != nil {
			fmt.Printf("Error converting %s to PNG: %v\n", svgFile, err)
			continue
		}
		fmt.Printf("Converted %s to %s\n", svgFile, pngFile)
	}

	// Check if any PNGs were created
	pngFiles, err := os.ReadDir(config.TempFolder)
	if err != nil || len(pngFiles) == 0 {
		return fmt.Errorf("no PNG files were created")
	}

	// Sort the PNG files to ensure correct order
	var pngFilePaths []string
	for _, file := range pngFiles {
		if !file.IsDir() && strings.HasSuffix(strings.ToLower(file.Name()), ".png") {
			pngFilePaths = append(pngFilePaths, filepath.Join(config.TempFolder, file.Name()))
		}
	}
	sort.Strings(pngFilePaths)

	if len(pngFilePaths) == 0 {
		return fmt.Errorf("no PNG files found in the temp folder")
	}

	// Read the first frame to get dimensions
	firstImgFile, err := os.Open(pngFilePaths[0])
	if err != nil {
		return fmt.Errorf("error opening first frame: %w", err)
	}
	firstImg, err := png.Decode(firstImgFile)
	if err != nil {
		firstImgFile.Close()
		return fmt.Errorf("error decoding first frame: %w", err)
	}
	firstImgFile.Close()

	width := firstImg.Bounds().Dx()
	height := firstImg.Bounds().Dy()

	// Build the MP4 file using FFmpeg
	startTime := time.Now()
	// Use a direct pattern approach instead of individual files
	err = createMP4WithDirectPattern(config.OutputVideo, config.TempFolder, width, height, config.FPS)
	if err != nil {
		return fmt.Errorf("error creating MP4: %w", err)
	}

	elapsedTime := time.Since(startTime)
	fmt.Printf("Video created successfully: %s (processing time: %v)\n", config.OutputVideo, elapsedTime)

	// Clean up temporary PNG files and temp folder
	fmt.Println("Cleaning up temporary files...")

	// First remove all PNG files
	for _, pngPath := range pngFilePaths {
		if err := os.Remove(pngPath); err != nil {
			fmt.Printf("Warning: could not remove temporary file %s: %v\n", pngPath, err)
		}
	}

	// Then remove the temp folder
	if err := os.RemoveAll(config.TempFolder); err != nil {
		fmt.Printf("Warning: could not remove temp directory %s: %v\n", config.TempFolder, err)
	} else {
		fmt.Println("Temporary files cleaned up successfully.")
	}

	return nil
}

// createMP4WithDirectPattern creates an MP4 file using FFmpeg with a pattern-based approach
func createMP4WithDirectPattern(outputPath string, pngDir string, width, height, fps int) error {
	// Instead of using glob pattern, get all PNG files and sort them properly
	entries, err := os.ReadDir(pngDir)
	if err != nil {
		return fmt.Errorf("error reading PNG directory: %w", err)
	}

	// Filter PNG files
	var pngFiles []string
	for _, entry := range entries {
		if !entry.IsDir() && strings.HasSuffix(strings.ToLower(entry.Name()), ".png") {
			pngFiles = append(pngFiles, entry.Name())
		}
	}

	if len(pngFiles) == 0 {
		return fmt.Errorf("no PNG files found in directory")
	}

	// Custom numeric sort for frame_XXXX.png files
	sort.Slice(pngFiles, func(i, j int) bool {
		var numI, numJ int
		fmt.Sscanf(pngFiles[i], "frame_%d.png", &numI)
		fmt.Sscanf(pngFiles[j], "frame_%d.png", &numJ)
		return numI < numJ
	})

	// Create a temporary file list for FFmpeg
	tempDir, err := os.MkdirTemp("", "mp4builder-*")
	if err != nil {
		return fmt.Errorf("error creating temp directory: %w", err)
	}
	defer os.RemoveAll(tempDir)

	// Create file list
	listFile := filepath.Join(tempDir, "files.txt")
	file, err := os.Create(listFile)
	if err != nil {
		return fmt.Errorf("error creating file list: %w", err)
	}

	// Create a loop that goes forward and backward with pauses at extremes
	fmt.Println("Creating forward-backward loop with pauses at extremes...")

	// Forward sequence with pause at the start
	firstFile := pngFiles[0]
	firstFilePath := filepath.Join(pngDir, firstFile)
	firstAbsPath, err := filepath.Abs(firstFilePath)
	if err != nil {
		file.Close()
		return fmt.Errorf("error getting absolute path: %w", err)
	}

	// Add 4 frames of the first frame for a pause at the start
	for i := 0; i < 4; i++ {
		_, err = file.WriteString(fmt.Sprintf("file '%s'\nduration %f\n", firstAbsPath, 1.0/float64(fps)))
		if err != nil {
			file.Close()
			return fmt.Errorf("error writing to file list: %w", err)
		}
	}

	// Forward sequence
	for _, pngFile := range pngFiles {
		pngPath := filepath.Join(pngDir, pngFile)
		absPath, err := filepath.Abs(pngPath)
		if err != nil {
			file.Close()
			return fmt.Errorf("error getting absolute path: %w", err)
		}

		// Format each entry according to FFmpeg concat demuxer requirements
		_, err = file.WriteString(fmt.Sprintf("file '%s'\nduration %f\n", absPath, 1.0/float64(fps)))
		if err != nil {
			file.Close()
			return fmt.Errorf("error writing to file list: %w", err)
		}
	}

	// Add 4 frames of the last frame for a pause at the end
	lastFile := pngFiles[len(pngFiles)-1]
	lastFilePath := filepath.Join(pngDir, lastFile)
	lastAbsPath, err := filepath.Abs(lastFilePath)
	if err != nil {
		file.Close()
		return fmt.Errorf("error getting absolute path: %w", err)
	}

	for i := 0; i < 3; i++ {
		_, err = file.WriteString(fmt.Sprintf("file '%s'\nduration %f\n", lastAbsPath, 1.0/float64(fps)))
		if err != nil {
			file.Close()
			return fmt.Errorf("error writing to file list: %w", err)
		}
	}

	// Backward sequence (excluding first and last frame to avoid duplicates)
	for i := len(pngFiles) - 2; i > 0; i-- {
		pngFile := pngFiles[i]
		pngPath := filepath.Join(pngDir, pngFile)
		absPath, err := filepath.Abs(pngPath)
		if err != nil {
			file.Close()
			return fmt.Errorf("error getting absolute path: %w", err)
		}

		// Format each entry according to FFmpeg concat demuxer requirements
		_, err = file.WriteString(fmt.Sprintf("file '%s'\nduration %f\n", absPath, 1.0/float64(fps)))
		if err != nil {
			file.Close()
			return fmt.Errorf("error writing to file list: %w", err)
		}
	}

	// One more first frame to complete the loop
	_, err = file.WriteString(fmt.Sprintf("file '%s'\nduration %f\n", firstAbsPath, 1.0/float64(fps)))
	if err != nil {
		file.Close()
		return fmt.Errorf("error writing to file list: %w", err)
	}
	file.Close()

	// Use FFmpeg with the file list approach for exact order control
	cmdArgs := []string{
		"-y",           // Overwrite output files without asking
		"-f", "concat", // Use concat demuxer
		"-safe", "0", // Allow absolute paths
		"-i", listFile, // Input from file list
		"-framerate", fmt.Sprintf("%d", fps), // Output framerate
		"-c:v", "libx264", // Video codec
		"-profile:v", "high", // High profile for better quality
		"-crf", "18", // Quality level (lower is better, 18 is very good quality)
		"-pix_fmt", "yuv420p", // Pixel format for compatibility
		"-movflags", "+faststart", // Optimize for web streaming
		outputPath, // Output file
	}

	// Run FFmpeg command
	cmd := exec.Command("ffmpeg", cmdArgs...)

	// Capture stdout and stderr
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	// Execute the command
	fmt.Println("Running FFmpeg to create MP4 with direct pattern matching...")
	cmdErr := cmd.Run()
	if cmdErr != nil {
		return fmt.Errorf("FFmpeg error: %w\nStderr: %s", cmdErr, stderr.String())
	}

	fmt.Println("MP4 video created successfully!")
	return nil
}

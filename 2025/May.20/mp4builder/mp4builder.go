package mp4builder

import (
	"bytes"
	"fmt"
	"image"
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
	for i, svgFile := range svgFiles {
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
	err = createMP4WithFFmpeg(config.OutputVideo, pngFilePaths, width, height, config.FPS)
	if err != nil {
		return fmt.Errorf("error creating MP4: %w", err)
	}

	elapsedTime := time.Since(startTime)
	fmt.Printf("Video created successfully: %s (processing time: %v)\n", config.OutputVideo, elapsedTime)
	return nil
}

// createMP4WithFFmpeg creates an MP4 file using FFmpeg external command
func createMP4WithFFmpeg(outputPath string, pngFilePaths []string, width, height, fps int) error {
	// Create a temporary directory to store a frame list file
	tempDir, err := os.MkdirTemp("", "mp4builder-*")
	if err != nil {
		return fmt.Errorf("error creating temp directory: %w", err)
	}
	defer os.RemoveAll(tempDir)

	// Create a file that lists all the input frames
	frameListPath := filepath.Join(tempDir, "frames.txt")
	frameListFile, err := os.Create(frameListPath)
	if err != nil {
		return fmt.Errorf("error creating frame list file: %w", err)
	}

	// Write frame paths to the list file
	for _, pngPath := range pngFilePaths {
		// For FFmpeg concat protocol, paths should be relative or absolute but usable by FFmpeg
		// We'll use absolute paths for clarity
		absPath, err := filepath.Abs(pngPath)
		if err != nil {
			frameListFile.Close()
			return fmt.Errorf("error getting absolute path: %w", err)
		}
		// FFmpeg expects paths with escaped single quotes
		escapedPath := strings.ReplaceAll(absPath, "'", "\\'")
		_, err = frameListFile.WriteString(fmt.Sprintf("file '%s'\n", escapedPath))
		if err != nil {
			frameListFile.Close()
			return fmt.Errorf("error writing to frame list: %w", err)
		}
	}
	frameListFile.Close()

	// Build FFmpeg command to create video from the frames
	cmdArgs := []string{
		"-y",           // Overwrite output files without asking
		"-f", "concat", // Use the concat demuxer
		"-safe", "0", // Don't require safe filenames
		"-i", frameListPath, // Input file list
		"-framerate", fmt.Sprintf("%d", fps), // Set input framerate
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
	fmt.Println("Running FFmpeg to create MP4...")
	err = cmd.Run()
	if err != nil {
		return fmt.Errorf("FFmpeg error: %w\nStderr: %s", err, stderr.String())
	}

	fmt.Println("MP4 video created successfully!")
	return nil
}

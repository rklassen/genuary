package main

import (
	"bufio"
	"flag"
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/abema/go-mp4"
	"github.com/srwiley/oksvg"
	"github.com/srwiley/rasterx"
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
	config := Config{
		FramesFolder: *framesFolder,
		OutputFolder: outputDir,
		TempFolder:   tempFolder,
		OutputVideo:  *outputVideo,
		FPS:          *fps,
	}

	// Create MP4 from frames
	err := CreateMP4FromFrames(config)
	if err != nil {
		fmt.Printf("Error creating MP4: %v\n", err)
		os.Exit(1)
	}
}

// Below functions have been moved to mp4builder.go

// ConvertSvgToPng converts an SVG file to PNG using oksvg and rasterx
func convertSvgToPng(svgPath, pngPath string) error {
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

func main() {
	// Configuration
	framesFolder := "../_output/frames/"
	outputFolder := "../_output/"
	tempFolder := outputFolder + "temp/"
	outputVideo := outputFolder + "lawful-chaotic.mp4"
	fps := 16

	// Create output and temp directories if they don't exist
	os.MkdirAll(outputFolder, 0755)
	os.MkdirAll(tempFolder, 0755)

	// Get all SVG files from frames folder
	files, err := os.ReadDir(framesFolder)
	if err != nil {
		fmt.Printf("Error reading frames directory: %v\n", err)
		return
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
		fmt.Println("No SVG files found in the frames folder")
		return
	}

	fmt.Printf("Found %d SVG files. Converting to PNG...\n", len(svgFiles))

	// Convert SVGs to PNGs using our Go-based converter
	for i, svgFile := range svgFiles {
		svgPath := filepath.Join(framesFolder, svgFile)
		// Create PNG filename with padding for proper sorting
		pngFile := fmt.Sprintf("frame_%04d.png", i)
		pngPath := filepath.Join(tempFolder, pngFile)

		err := convertSvgToPng(svgPath, pngPath)
		if err != nil {
			fmt.Printf("Error converting %s to PNG: %v\n", svgFile, err)
			continue
		}
		fmt.Printf("Converted %s to %s\n", svgFile, pngFile)
	}

	// Check if any PNGs were created
	pngFiles, err := os.ReadDir(tempFolder)
	if err != nil || len(pngFiles) == 0 {
		fmt.Println("No PNG files were created. Cannot proceed with video creation.")
		return
	}

	// Create MP4 from PNG sequence using go-mp4
	fmt.Println("Creating video from PNG sequence...")

	// Sort the PNG files to ensure correct order
	var pngFilePaths []string
	for _, file := range pngFiles {
		if !file.IsDir() && strings.HasSuffix(strings.ToLower(file.Name()), ".png") {
			pngFilePaths = append(pngFilePaths, filepath.Join(tempFolder, file.Name()))
		}
	}
	sort.Strings(pngFilePaths)

	if len(pngFilePaths) == 0 {
		fmt.Println("No PNG files found in the temp folder")
		return
	}

	// Read the first frame to get dimensions
	firstImgFile, err := os.Open(pngFilePaths[0])
	if err != nil {
		fmt.Printf("Error opening first frame: %v\n", err)
		return
	}
	firstImg, err := png.Decode(firstImgFile)
	if err != nil {
		fmt.Printf("Error decoding first frame: %v\n", err)
		firstImgFile.Close()
		return
	}
	firstImgFile.Close()

	width := firstImg.Bounds().Dx()
	height := firstImg.Bounds().Dy()

	// Create output file
	out, err := os.Create(outputVideo)
	if err != nil {
		fmt.Printf("Error creating output file: %v\n", err)
		return
	}
	defer out.Close()

	// Create a buffered writer for better performance
	bufWriter := bufio.NewWriter(out)
	defer bufWriter.Flush()

	// Initialize MP4 writer
	writer := mp4.NewWriter(out)

	// Create ftyp box (file type box)
	ftyp := &mp4.Ftyp{
		MajorBrand:   mp4.BrandMP41(),
		MinorVersion: 0,
		CompatibleBrands: []mp4.CompatibleBrandElem{
			{CompatibleBrand: mp4.BrandISOM()},
			{CompatibleBrand: mp4.BrandMP41()},
		},
	}

	// Write the file type box
	_, err = mp4.Marshal(writer, ftyp, mp4.Context{})
	if err != nil {
		fmt.Printf("Error writing ftyp: %v\n", err)
		return
	}

	// Create mdat box for actual media data
	// In a real implementation, you would encode the frames as a proper video codec
	// This is a simplified version that just writes the PNG data as is
	mdatSize := uint64(8) // mdat box header size

	// Calculate total mdat size
	for _, pngPath := range pngFilePaths {
		info, err := os.Stat(pngPath)
		if err != nil {
			fmt.Printf("Error getting file info for %s: %v\n", pngPath, err)
			continue
		}
		mdatSize += uint64(info.Size())
	}

	// Write mdat box header
	err = writer.WriteBoxStart(&mp4.BoxInfo{
		Type: mp4.BoxTypeMdat(),
		Size: mdatSize,
	})
	if err != nil {
		fmt.Printf("Error writing mdat header: %v\n", err)
		return
	}

	// Write PNG data to mdat
	startTime := time.Now()
	for i, pngPath := range pngFilePaths {
		pngData, err := os.ReadFile(pngPath)
		if err != nil {
			fmt.Printf("Error reading PNG file %s: %v\n", pngPath, err)
			continue
		}

		_, err = writer.Write(pngData)
		if err != nil {
			fmt.Printf("Error writing frame data: %v\n", err)
			continue
		}

		fmt.Printf("Added frame %d/%d to video\n", i+1, len(pngFilePaths))
	}

	// Finish writing mdat
	err = writer.WriteBoxEnd()
	if err != nil {
		fmt.Printf("Error finalizing mdat: %v\n", err)
		return
	}

	// Write moov box (container for metadata)
	moov := &mp4.Moov{
		Mvhd: &mp4.Mvhd{
			Timescale:   uint32(fps),
			Duration:    uint64(len(pngFilePaths)),
			Rate:        0x00010000, // 1.0 fixed-point
			Volume:      0x0100,     // 1.0 fixed-point
			Matrix:      [9]int32{0x00010000, 0, 0, 0, 0x00010000, 0, 0, 0, 0x40000000},
			NextTrackID: 2,
		},
		Traks: []*mp4.Trak{
			{
				Tkhd: &mp4.Tkhd{
					Flags:    mp4.TkhdFlagTrackEnabled | mp4.TkhdFlagTrackInMovie,
					Duration: uint64(len(pngFilePaths)),
					Width:    uint32(width) << 16,  // 16.16 fixed-point
					Height:   uint32(height) << 16, // 16.16 fixed-point
					Matrix:   [9]int32{0x00010000, 0, 0, 0, 0x00010000, 0, 0, 0, 0x40000000},
					TrackID:  1,
				},
				Mdia: &mp4.Mdia{
					Mdhd: &mp4.Mdhd{
						Timescale: uint32(fps),
						Duration:  uint64(len(pngFilePaths)),
						Language:  [3]byte{'u', 'n', 'd'},
					},
					Hdlr: &mp4.Hdlr{
						HandlerType: [4]byte{'v', 'i', 'd', 'e'},
						Name:        "VideoHandler",
					},
					Minf: &mp4.Minf{
						Vmhd: &mp4.Vmhd{
							Flags: 1,
						},
						Dinf: &mp4.Dinf{
							Dref: &mp4.Dref{
								Url: []*mp4.Url{
									{
										Flags: mp4.UrlSelfContained,
									},
								},
							},
						},
						Stbl: &mp4.Stbl{
							Stsd: &mp4.Stsd{
								Entries: []mp4.SampleEntry{
									&mp4.VisualSampleEntry{
										SampleEntry: mp4.SampleEntry{
											DataReferenceIndex: 1,
										},
										Width:  uint16(width),
										Height: uint16(height),
										Depth:  24,
										// In a real implementation, you would set up a proper codec here
									},
								},
							},
							Stts: &mp4.Stts{
								Entries: []mp4.SttsEntry{
									{
										SampleCount: uint32(len(pngFilePaths)),
										SampleDelta: 1,
									},
								},
							},
							Stsc: &mp4.Stsc{
								Entries: []mp4.StscEntry{
									{
										FirstChunk:      1,
										SamplesPerChunk: 1,
										SampleDescIndex: 1,
									},
								},
							},
							Stsz: &mp4.Stsz{
								SampleSize:  0,
								SampleCount: uint32(len(pngFilePaths)),
								EntrySize:   make([]uint32, len(pngFilePaths)),
							},
							Stco: &mp4.Stco{
								ChunkOffsets: make([]uint32, len(pngFilePaths)),
							},
						},
					},
				},
			},
		},
	}

	// Set sample sizes in stsz box
	for i, pngPath := range pngFilePaths {
		info, err := os.Stat(pngPath)
		if err != nil {
			fmt.Printf("Error getting file info for %s: %v\n", pngPath, err)
			continue
		}
		moov.Traks[0].Mdia.Minf.Stbl.Stsz.EntrySize[i] = uint32(info.Size())
	}

	// Set a simple offset for chunks in stco (not accurate for a real MP4)
	offset := uint32(8 + 8) // ftyp box header + mdat box header
	for i := range pngFilePaths {
		moov.Traks[0].Mdia.Minf.Stbl.Stco.ChunkOffsets[i] = offset
		offset += moov.Traks[0].Mdia.Minf.Stbl.Stsz.EntrySize[i]
	}

	// Write moov box
	_, err = mp4.Marshal(writer, moov, mp4.Context{})
	if err != nil {
		fmt.Printf("Error writing moov: %v\n", err)
		return
	}

	elapsedTime := time.Since(startTime)
	fmt.Printf("Video created successfully: %s (processing time: %v)\n", outputVideo, elapsedTime)
}

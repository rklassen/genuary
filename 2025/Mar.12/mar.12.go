package main

import (
	"bytes"
	"fmt"
	"image/png"

	// "log"
	"os"

	"github.com/chai2010/webp"
)

func main() {
	var buf bytes.Buffer

	data, _ := os.ReadFile("./coffee_sq.png")
	img, _ := png.Decode(bytes.NewReader(data))
	_ = webp.Encode(&buf, img, &webp.Options{Lossless: false})
	_ = os.WriteFile("./coffee_sq.webp", buf.Bytes(), 0666)
	fmt.Println("Save ./coffee_sq.webp ok")
}

// func handleError(err error) {
// 	if err != nil {
// 		log.Println(err)
// 		os.Exit(1)
// 	}
// }

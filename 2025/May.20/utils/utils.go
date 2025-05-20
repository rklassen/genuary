package utils

import (
	"fmt"
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

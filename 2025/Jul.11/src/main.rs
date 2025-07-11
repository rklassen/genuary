mod models;

use models::Point;

fn main() {
    println!("Hello, Genuary 2025 - July 11!");
    
    // Create a point using the new constructor
    let point = Point::new(10.0, 20.0);
    println!("Created point: {:?}", point);
    
    // Access the x and y fields directly
    println!("Point coordinates: x = {}, y = {}", point.x, point.y);
    
    // Use the origin method
    let origin = Point::origin();
    println!("Origin point: {:?}", origin);
    
    // Calculate distance between two points
    let distance = point.distance_to(&origin);
    println!("Distance from point to origin: {}", distance);
}

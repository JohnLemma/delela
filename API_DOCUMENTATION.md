# Property Marketplace API Documentation

## Base URL
```
http://your-server:5000/api
```

## Authentication
Currently, the API is open and doesn't require authentication.

## Endpoints

### Properties

#### List Properties
```
GET /properties
```

Query Parameters:
- `type` (optional): Filter by property type ('house' or 'car')
- `sort` (optional): Sort properties ('newest', 'oldest', 'price_low', 'price_high')
- `search` (optional): Search in title, description, and location
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter

Response:
```json
[
  {
    "id": 1,
    "type": "house",
    "title": "Modern Villa with Pool",
    "description": "Luxurious 4-bedroom villa...",
    "price": 850000,
    "location": "Beverly Hills, CA",
    "image_url": "https://...",
    "created_at": "2024-01-01T12:00:00",
    "bedrooms": 4,
    "bathrooms": 3.5,
    "square_feet": 3200,
    "year_built": 2020
  }
]
```

#### Get Single Property
```
GET /properties/<property_id>
```

Response:
```json
{
  "id": 1,
  "type": "house",
  "title": "Modern Villa with Pool",
  "description": "Luxurious 4-bedroom villa...",
  "price": 850000,
  "location": "Beverly Hills, CA",
  "image_url": "https://...",
  "created_at": "2024-01-01T12:00:00",
  "bedrooms": 4,
  "bathrooms": 3.5,
  "square_feet": 3200,
  "year_built": 2020
}
```

#### Create Property
```
POST /properties
```

Request Body:
```json
{
  "type": "house",
  "title": "New Property",
  "description": "Property description",
  "price": 500000,
  "location": "Los Angeles, CA",
  "image_url": "https://...",
  "bedrooms": 3,
  "bathrooms": 2,
  "square_feet": 2000,
  "year_built": 2023
}
```

#### Update Property
```
PUT /properties/<property_id>
```

Request Body: Same as POST, but only include fields to update

#### Delete Property
```
DELETE /properties/<property_id>
```

### Additional Endpoints

#### Get Property Types
```
GET /properties/types
```

Response:
```json
{
  "types": ["house", "car"]
}
```

#### Get Property Statistics
```
GET /properties/stats
```

Response:
```json
{
  "total_properties": 15,
  "total_houses": 7,
  "total_cars": 8,
  "average_house_price": 725000.00,
  "average_car_price": 77686.25
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 500: Server Error

Error Response Format:
```json
{
  "message": "Error description"
}
```

## Sample Mobile App Integration

### React Native Example
```javascript
const fetchProperties = async () => {
  try {
    const response = await fetch('http://your-server:5000/api/properties');
    const data = await response.json();
    setProperties(data);
  } catch (error) {
    console.error('Error fetching properties:', error);
  }
};

const addProperty = async (propertyData) => {
  try {
    const response = await fetch('http://your-server:5000/api/properties', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(propertyData),
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error adding property:', error);
  }
};
```

### Swift Example
```swift
func fetchProperties() {
    guard let url = URL(string: "http://your-server:5000/api/properties") else { return }
    
    URLSession.shared.dataTask(with: url) { data, response, error in
        if let data = data {
            do {
                let properties = try JSONDecoder().decode([Property].self, from: data)
                DispatchQueue.main.async {
                    self.properties = properties
                }
            } catch {
                print("Error decoding data: \(error)")
            }
        }
    }.resume()
}
```

### Kotlin Example
```kotlin
fun fetchProperties() {
    val url = "http://your-server:5000/api/properties"
    
    CoroutineScope(Dispatchers.IO).launch {
        try {
            val response = URL(url).readText()
            val properties = Json.decodeFromString<List<Property>>(response)
            withContext(Dispatchers.Main) {
                // Update UI with properties
            }
        } catch (e: Exception) {
            println("Error fetching properties: ${e.message}")
        }
    }
}
```

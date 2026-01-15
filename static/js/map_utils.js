/**
 * MAP UTILITY FUNCTIONS
 * 
 * This file contains reusable functions for all map pages in the Ride-Share app.
 * It uses Leaflet.js with OpenStreetMap (100% FREE, no API keys needed!)
 * 
 * Functions included:
 * 1. initMap() - Create a new map
 * 2. addMarker() - Add a marker to the map
 * 3. addRoute() - Draw a route between two points
 * 4. geocodeAddress() - Convert address to coordinates (FREE!)
 */

// ============================================
// 1. INITIALIZE MAP
// ============================================
/**
 * Create a new Leaflet map
 * @param {string} elementId - ID of the HTML element to contain the map
 * @param {number} lat - Initial latitude (default: Mumbai)
 * @param {number} lng - Initial longitude (default: Mumbai)
 * @param {number} zoom - Initial zoom level (default: 12)
 * @returns {object} Leaflet map object
 */
function initMap(elementId, lat = 19.0760, lng = 72.8777, zoom = 12) {
    // Create map centered at given coordinates
    const map = L.map(elementId).setView([lat, lng], zoom);

    // Add OpenStreetMap tiles (FREE!)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    return map;
}

// ============================================
// 2. ADD MARKER TO MAP
// ============================================
/**
 * Add a marker to the map with popup
 * @param {object} map - Leaflet map object
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 * @param {string} title - Marker title
 * @param {string} popupContent - HTML content for popup
 * @param {string} color - Marker color ('blue', 'red', 'green', 'yellow')
 * @returns {object} Leaflet marker object
 */
function addMarker(map, lat, lng, title, popupContent, color = 'blue') {
    // Define custom marker icons
    const markerIcons = {
        blue: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        }),
        red: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        }),
        green: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        }),
        yellow: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    };

    // Create marker with custom icon
    const marker = L.marker([lat, lng], {
        icon: markerIcons[color] || markerIcons.blue,
        title: title
    }).addTo(map);

    // Add popup if content provided
    if (popupContent) {
        marker.bindPopup(popupContent);
    }

    return marker;
}

// ============================================
// 3. DRAW ROUTE BETWEEN TWO POINTS
// ============================================
/**
 * Draw a route between pickup and drop locations
 * @param {object} map - Leaflet map object
 * @param {number} startLat - Pickup latitude
 * @param {number} startLng - Pickup longitude
 * @param {number} endLat - Drop latitude
 * @param {number} endLng - Drop longitude
 * @param {string} color - Route color (default: '#FDBD01' - taxi yellow)
 * @returns {object} Leaflet routing control object
 */
function addRoute(map, startLat, startLng, endLat, endLng, color = '#FDBD01') {
    // Create routing control
    const routingControl = L.Routing.control({
        waypoints: [
            L.latLng(startLat, startLng),
            L.latLng(endLat, endLng)
        ],
        routeWhileDragging: false,
        show: false, // Hide turn-by-turn instructions
        lineOptions: {
            styles: [{
                color: color,
                opacity: 0.8,
                weight: 6
            }]
        },
        createMarker: function () { return null; } // Don't create default markers
    }).addTo(map);

    return routingControl;
}

// ============================================
// 4. GEOCODE ADDRESS (FREE!)
// ============================================
/**
 * Convert address to coordinates using OpenStreetMap Nominatim (FREE!)
 * @param {string} address - Address to geocode
 * @returns {Promise} Promise resolving to {lat, lng} or null
 */
async function geocodeAddress(address) {
    try {
        // Use OpenStreetMap Nominatim API (FREE, no API key needed!)
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`;

        const response = await fetch(url, {
            headers: {
                'User-Agent': 'RideShareApp/1.0' // Required by Nominatim
            }
        });

        const data = await response.json();

        if (data && data.length > 0) {
            return {
                lat: parseFloat(data[0].lat),
                lng: parseFloat(data[0].lon),
                displayName: data[0].display_name
            };
        }

        return null;
    } catch (error) {
        console.error('Geocoding error:', error);
        return null;
    }
}

// ============================================
// 5. REVERSE GEOCODE (Coordinates to Address)
// ============================================
/**
 * Convert coordinates to address (FREE!)
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 * @returns {Promise} Promise resolving to address string or null
 */
async function reverseGeocode(lat, lng) {
    try {
        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`;

        const response = await fetch(url, {
            headers: {
                'User-Agent': 'RideShareApp/1.0'
            }
        });

        const data = await response.json();

        if (data && data.display_name) {
            return data.display_name;
        }

        return null;
    } catch (error) {
        console.error('Reverse geocoding error:', error);
        return null;
    }
}

// ============================================
// 6. FIT MAP TO SHOW ALL MARKERS
// ============================================
/**
 * Adjust map zoom to show all markers
 * @param {object} map - Leaflet map object
 * @param {array} markers - Array of Leaflet marker objects
 */
function fitMapToMarkers(map, markers) {
    if (markers.length === 0) return;

    const group = L.featureGroup(markers);
    map.fitBounds(group.getBounds().pad(0.1)); // Add 10% padding
}

// ============================================
// 7. GET USER'S CURRENT LOCATION
// ============================================
/**
 * Get user's current location using browser geolocation
 * @returns {Promise} Promise resolving to {lat, lng} or null
 */
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation not supported'));
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                resolve({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                });
            },
            (error) => {
                reject(error);
            }
        );
    });
}

// ============================================
// 8. CREATE RIDE POPUP CONTENT
// ============================================
/**
 * Create HTML content for ride marker popup
 * @param {object} ride - Ride object with details
 * @returns {string} HTML string for popup
 */
function createRidePopup(ride) {
    return `
        <div class="ride-popup">
            <h6><i class="bi bi-car-front-fill"></i> ${ride.driver}</h6>
            <p class="mb-1">
                <strong>From:</strong> ${ride.start_location}<br>
                <strong>To:</strong> ${ride.end_location}
            </p>
            <p class="mb-1">
                <i class="bi bi-calendar"></i> ${ride.start_date}<br>
                <i class="bi bi-people"></i> ${ride.seats} seats available<br>
                <i class="bi bi-currency-rupee"></i> ₹${ride.price} per seat
            </p>
            <a href="/ride/${ride.id}" class="btn btn-sm btn-primary">View Details</a>
        </div>
    `;
}

// ============================================
// 9. CREATE SOS POPUP CONTENT
// ============================================
/**
 * Create HTML content for SOS emergency marker popup
 * @param {object} user - User object with SOS details
 * @returns {string} HTML string for popup
 */
function createSOSPopup(user) {
    return `
        <div class="sos-popup">
            <h6 class="text-danger">
                <i class="bi bi-exclamation-triangle-fill"></i> SOS EMERGENCY
            </h6>
            <p class="mb-1">
                <strong>User:</strong> ${user.username}<br>
                <strong>Location:</strong> ${user.sos_location}<br>
                <strong>Time:</strong> ${user.sos_timestamp}<br>
                <strong>Message:</strong> ${user.sos_message || 'Emergency!'}
            </p>
            <button class="btn btn-sm btn-danger" onclick="contactUser(${user.id})">
                <i class="bi bi-telephone"></i> Contact User
            </button>
        </div>
    `;
}

// ============================================
// 10. CALCULATE DISTANCE BETWEEN TWO POINTS
// ============================================
/**
 * Calculate distance between two coordinates (Haversine formula)
 * @param {number} lat1 - First point latitude
 * @param {number} lng1 - First point longitude
 * @param {number} lat2 - Second point latitude
 * @param {number} lng2 - Second point longitude
 * @returns {number} Distance in kilometers
 */
function calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;

    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLng / 2) * Math.sin(dLng / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c;

    return Math.round(distance * 10) / 10; // Round to 1 decimal place
}

console.log('✅ Map utilities loaded successfully!');

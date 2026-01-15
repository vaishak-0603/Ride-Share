/**
 * ADMIN MAP JAVASCRIPT
 * 
 * This file handles the admin map dashboard functionality.
 * It shows all rides, SOS emergencies, and allows filtering.
 * 
 * Features:
 * 1. Display all active rides on map
 * 2. Show SOS emergencies in RED
 * 3. Filter rides by location/status
 * 4. Auto-refresh every 30 seconds
 */

// Global variables
let adminMap;
let allMarkers = [];
let allRoutes = [];
let ridesData = [];
let sosData = [];

// ============================================
// INITIALIZE ADMIN MAP
// ============================================
document.addEventListener('DOMContentLoaded', function () {
    console.log('🗺️ Initializing Admin Map Dashboard...');

    // Load data from hidden script tags
    loadDataFromPage();

    // Initialize map (centered on India/Mumbai by default)
    adminMap = initMap('admin-map', 19.0760, 72.8777, 6);

    // Display all rides and SOS alerts
    displayAllRides();
    displaySOSAlerts();

    // Setup event listeners
    setupEventListeners();

    // Auto-refresh every 30 seconds
    setInterval(refreshMap, 30000);

    console.log('✅ Admin Map loaded successfully!');
});

// ============================================
// LOAD DATA FROM PAGE
// ============================================
function loadDataFromPage() {
    try {
        // Get rides data from hidden script tag
        const ridesScript = document.getElementById('rides-data');
        if (ridesScript) {
            ridesData = JSON.parse(ridesScript.textContent);
            console.log(`📊 Loaded ${ridesData.length} rides`);
        }

        // Get SOS data from hidden script tag
        const sosScript = document.getElementById('sos-data');
        if (sosScript) {
            sosData = JSON.parse(sosScript.textContent);
            console.log(`🚨 Loaded ${sosData.length} SOS alerts`);
        }
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// ============================================
// DISPLAY ALL RIDES ON MAP
// ============================================
function displayAllRides() {
    // Clear existing markers and routes
    clearMapElements();

    if (!ridesData || ridesData.length === 0) {
        console.log('No rides to display');
        return;
    }

    console.log(`🚗 Displaying ${ridesData.length} rides on map...`);

    ridesData.forEach(ride => {
        // Use default coordinates if not available
        const startLat = ride.start_lat || getRandomCoordinate(19.0760, 0.5);
        const startLng = ride.start_lng || getRandomCoordinate(72.8777, 0.5);
        const endLat = ride.end_lat || getRandomCoordinate(19.0760, 0.5);
        const endLng = ride.end_lng || getRandomCoordinate(72.8777, 0.5);

        // Create popup content
        const popupContent = `
            <div class="ride-popup">
                <h6><i class="bi bi-car-front-fill"></i> ${ride.driver.username}</h6>
                <p class="mb-1">
                    <strong>From:</strong> ${ride.start_location}<br>
                    <strong>To:</strong> ${ride.end_location}
                </p>
                <p class="mb-1">
                    <i class="bi bi-calendar"></i> ${new Date(ride.start_date).toLocaleString()}<br>
                    <i class="bi bi-people"></i> ${ride.available_seats} seats<br>
                    <i class="bi bi-currency-rupee"></i> ₹${ride.price_per_seat} per seat
                </p>
                <span class="badge bg-${ride.status === 'ONGOING' ? 'success' : 'info'}">
                    ${ride.status}
                </span>
                <br>
                <a href="/ride/${ride.id}" class="btn btn-sm btn-primary mt-2">View Details</a>
            </div>
        `;

        // Add pickup marker (Yellow - our theme color!)
        const pickupMarker = addMarker(
            adminMap,
            startLat,
            startLng,
            `Pickup: ${ride.start_location}`,
            popupContent,
            'yellow'
        );
        allMarkers.push(pickupMarker);

        // Add drop marker (Green)
        const dropMarker = addMarker(
            adminMap,
            endLat,
            endLng,
            `Drop: ${ride.end_location}`,
            popupContent,
            'green'
        );
        allMarkers.push(dropMarker);

        // Add route if checkbox is checked
        if (document.getElementById('show-routes').checked) {
            const route = addRoute(adminMap, startLat, startLng, endLat, endLng);
            allRoutes.push(route);
        }
    });

    // Fit map to show all markers
    if (allMarkers.length > 0) {
        fitMapToMarkers(adminMap, allMarkers);
    }
}

// ============================================
// DISPLAY SOS ALERTS ON MAP
// ============================================
function displaySOSAlerts() {
    if (!sosData || sosData.length === 0) {
        console.log('No SOS alerts');
        return;
    }

    console.log(`🚨 Displaying ${sosData.length} SOS alerts...`);

    sosData.forEach(user => {
        // Parse location (format: "lat, lng")
        let lat, lng;
        if (user.sos_location && user.sos_location.includes(',')) {
            const coords = user.sos_location.split(',');
            lat = parseFloat(coords[0]);
            lng = parseFloat(coords[1]);
        } else {
            // Default to Mumbai if location not available
            lat = 19.0760;
            lng = 72.8777;
        }

        // Create SOS popup
        const popupContent = `
            <div class="sos-popup">
                <h6 class="text-danger">
                    <i class="bi bi-exclamation-triangle-fill"></i> SOS EMERGENCY
                </h6>
                <p class="mb-1">
                    <strong>User:</strong> ${user.username}<br>
                    <strong>Email:</strong> ${user.email}<br>
                    <strong>Phone:</strong> ${user.phone || 'Not available'}<br>
                    <strong>Time:</strong> ${new Date(user.sos_timestamp).toLocaleString()}<br>
                    <strong>Message:</strong> ${user.sos_message || 'Emergency!'}
                </p>
                <button class="btn btn-sm btn-danger" onclick="alert('Call: ${user.phone || 'No phone'}')">
                    <i class="bi bi-telephone"></i> Contact User
                </button>
            </div>
        `;

        // Add RED marker for SOS
        const sosMarker = addMarker(
            adminMap,
            lat,
            lng,
            `SOS: ${user.username}`,
            popupContent,
            'red'
        );

        // Make SOS marker pulse/blink
        sosMarker.getElement().classList.add('sos-marker-pulse');

        allMarkers.push(sosMarker);
    });
}

// ============================================
// SETUP EVENT LISTENERS
// ============================================
function setupEventListeners() {
    // Location filter
    document.getElementById('location-filter').addEventListener('input', filterRides);

    // Status filter
    document.getElementById('status-filter').addEventListener('change', filterRides);

    // Show routes checkbox
    document.getElementById('show-routes').addEventListener('change', function () {
        displayAllRides();
        displaySOSAlerts();
    });
}

// ============================================
// FILTER RIDES
// ============================================
function filterRides() {
    const locationFilter = document.getElementById('location-filter').value.toLowerCase();
    const statusFilter = document.getElementById('status-filter').value;

    // Filter rides data
    let filteredRides = ridesData;

    // Apply location filter
    if (locationFilter) {
        filteredRides = filteredRides.filter(ride =>
            ride.start_location.toLowerCase().includes(locationFilter) ||
            ride.end_location.toLowerCase().includes(locationFilter)
        );
    }

    // Apply status filter
    if (statusFilter !== 'all') {
        filteredRides = filteredRides.filter(ride => ride.status === statusFilter);
    }

    // Clear map and display filtered rides
    clearMapElements();

    // Temporarily replace ridesData with filtered data
    const originalData = ridesData;
    ridesData = filteredRides;
    displayAllRides();
    ridesData = originalData;

    // Always show SOS alerts
    displaySOSAlerts();

    console.log(`🔍 Filtered to ${filteredRides.length} rides`);
}

// ============================================
// REFRESH MAP
// ============================================
function refreshMap() {
    console.log('🔄 Refreshing map data...');

    // In production, fetch fresh data from API
    // For now, just reload the page
    location.reload();
}

// ============================================
// VIEW SOS ON MAP
// ============================================
function viewSOSOnMap(userId) {
    // Find SOS user
    const user = sosData.find(u => u.id === userId);
    if (!user) return;

    // Parse location
    let lat, lng;
    if (user.sos_location && user.sos_location.includes(',')) {
        const coords = user.sos_location.split(',');
        lat = parseFloat(coords[0]);
        lng = parseFloat(coords[1]);
    } else {
        lat = 19.0760;
        lng = 72.8777;
    }

    // Zoom to SOS location
    adminMap.setView([lat, lng], 15);

    // Find and open the marker popup
    allMarkers.forEach(marker => {
        if (marker.getLatLng().lat === lat && marker.getLatLng().lng === lng) {
            marker.openPopup();
        }
    });
}

// ============================================
// CLEAR MAP ELEMENTS
// ============================================
function clearMapElements() {
    // Remove all markers
    allMarkers.forEach(marker => adminMap.removeLayer(marker));
    allMarkers = [];

    // Remove all routes
    allRoutes.forEach(route => adminMap.removeControl(route));
    allRoutes = [];
}

// ============================================
// HELPER: GET RANDOM COORDINATE (for demo)
// ============================================
function getRandomCoordinate(base, range) {
    return base + (Math.random() - 0.5) * range;
}

console.log('✅ Admin map script loaded!');

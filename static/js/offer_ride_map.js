/**
 * OFFER RIDE MAP - Leaflet Version (FREE!)
 * 
 * This replaces the old Google Maps functionality with Leaflet + OpenStreetMap.
 * Users can click on the map to select pickup and drop locations.
 */

let offerMap;
let pickupMarker;
let dropMarker;
let routeLine;

function initOfferRideMap() {
    // Initialize map centered on India
    offerMap = L.map('map').setView([20.5937, 78.9629], 5);

    // Add OpenStreetMap tiles (FREE!)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(offerMap);

    // Add click handler for map
    offerMap.on('click', function (e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        // If no pickup marker yet, create pickup
        if (!pickupMarker) {
            pickupMarker = L.marker([lat, lng], {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                }),
                draggable: true
            }).addTo(offerMap);

            pickupMarker.bindPopup('Pickup Location').openPopup();

            // Update origin field
            reverseGeocode(lat, lng, 'origin');

        } else if (!dropMarker) {
            // Create drop marker
            dropMarker = L.marker([lat, lng], {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                }),
                draggable: true
            }).addTo(offerMap);

            dropMarker.bindPopup('Drop Location').openPopup();

            // Update destination field
            reverseGeocode(lat, lng, 'destination');

            // Draw route
            drawRoute();
        }
    });

    console.log('✅ Offer ride map initialized!');
}

function reverseGeocode(lat, lng, fieldId) {
    // Use OpenStreetMap Nominatim for reverse geocoding (FREE!)
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`, {
        headers: {
            'User-Agent': 'CarpoolingApp/1.0'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data && data.address) {
                // Extract city name
                const city = data.address.city || data.address.town || data.address.village || data.address.state;
                document.getElementById(fieldId).value = city || data.display_name;
            }
        })
        .catch(error => {
            console.error('Geocoding error:', error);
            document.getElementById(fieldId).value = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        });
}

function drawRoute() {
    if (!pickupMarker || !dropMarker) return;

    const pickupLatLng = pickupMarker.getLatLng();
    const dropLatLng = dropMarker.getLatLng();

    // Remove old route if exists
    if (routeLine) {
        offerMap.removeLayer(routeLine);
    }

    // Draw simple line between points
    routeLine = L.polyline([pickupLatLng, dropLatLng], {
        color: '#FDBD01', // Taxi yellow!
        weight: 4,
        opacity: 0.7
    }).addTo(offerMap);

    // Fit map to show both markers
    offerMap.fitBounds([pickupLatLng, dropLatLng], { padding: [50, 50] });

    // Calculate distance
    const distance = offerMap.distance(pickupLatLng, dropLatLng) / 1000; // Convert to km
    document.getElementById('distance').value = distance.toFixed(1);

    // Show estimated duration
    const durationElement = document.getElementById('estimated-duration');
    if (durationElement) {
        const estimatedHours = distance / 60; // Assuming 60 km/h average
        const hours = Math.floor(estimatedHours);
        const minutes = Math.round((estimatedHours - hours) * 60);
        durationElement.textContent = `Estimated journey: ${hours}h ${minutes}m (${distance.toFixed(1)} km)`;
    }
}

function clearMap() {
    if (pickupMarker) {
        offerMap.removeLayer(pickupMarker);
        pickupMarker = null;
    }
    if (dropMarker) {
        offerMap.removeLayer(dropMarker);
        dropMarker = null;
    }
    if (routeLine) {
        offerMap.removeLayer(routeLine);
        routeLine = null;
    }
    document.getElementById('origin').value = '';
    document.getElementById('destination').value = '';
    document.getElementById('distance').value = '';
}

console.log('✅ Offer ride map script loaded!');

let map;
let originMarker;
let destinationMarker;
let directionsService;
let directionsRenderer;

function initMap() {
    // Initialize the map centered on India
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 20.5937, lng: 78.9629 },
        zoom: 5,
        mapTypeControl: false,
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true,
    });

    // Initialize markers
    originMarker = new google.maps.Marker({
        map: map,
        draggable: true,
        icon: {
            url: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
            scaledSize: new google.maps.Size(32, 32)
        }
    });

    destinationMarker = new google.maps.Marker({
        map: map,
        draggable: true,
        icon: {
            url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
            scaledSize: new google.maps.Size(32, 32)
        }
    });

    // Initialize search boxes
    initSearchBox('origin-search', originMarker, 'origin');
    initSearchBox('destination-search', destinationMarker, 'destination');

    // Add marker drag events
    originMarker.addListener('dragend', () => {
        updateAddress(originMarker, 'origin');
        updateRoute();
    });

    destinationMarker.addListener('dragend', () => {
        updateAddress(destinationMarker, 'destination');
        updateRoute();
    });
}

function initSearchBox(elementId, marker, fieldId) {
    const input = document.getElementById(elementId);
    const searchBox = new google.maps.places.SearchBox(input);

    searchBox.addListener('places_changed', () => {
        const places = searchBox.getPlaces();
        if (places.length === 0) return;

        const place = places[0];
        if (!place.geometry || !place.geometry.location) return;

        // Set marker position
        marker.setPosition(place.geometry.location);
        map.setCenter(place.geometry.location);
        map.setZoom(13);

        // Update the form field with city name
        const cityName = extractCityName(place.address_components);
        document.getElementById(fieldId).value = cityName;

        updateRoute();
    });
}

function extractCityName(addressComponents) {
    let city = '';
    for (const component of addressComponents) {
        if (component.types.includes('locality')) {
            city = component.long_name;
            break;
        } else if (component.types.includes('administrative_area_level_2')) {
            city = component.long_name;
            break;
        }
    }
    return city;
}

function updateAddress(marker, fieldId) {
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ location: marker.getPosition() }, (results, status) => {
        if (status === 'OK' && results[0]) {
            const cityName = extractCityName(results[0].address_components);
            document.getElementById(fieldId).value = cityName;
        }
    });
}

function updateRoute() {
    if (!originMarker.getPosition() || !destinationMarker.getPosition()) return;

    const request = {
        origin: originMarker.getPosition(),
        destination: destinationMarker.getPosition(),
        travelMode: google.maps.TravelMode.DRIVING
    };

    directionsService.route(request, (result, status) => {
        if (status === 'OK') {
            directionsRenderer.setDirections(result);

            // Update estimated duration if available
            if (result.routes[0] && result.routes[0].legs[0]) {
                const duration = result.routes[0].legs[0].duration.text;
                const distance = result.routes[0].legs[0].distance.text;
                const durationElement = document.getElementById('estimated-duration');
                if (durationElement) {
                    durationElement.textContent = `Estimated journey: ${duration} (${distance})`;
                }
            }
        }
    });
}

// Initialize the map when the window loads
window.initMap = initMap;

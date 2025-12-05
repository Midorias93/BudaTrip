import { map, startIcon, endIcon, stationIcon } from './init.js';
import { showLoading, hideLoading, showError } from './ui.js';
import { clearMarkers, clearRoute, addMarker, setStartMarker, setEndMarker, setRouteLayer } from './markers.js';
import { checkRainAndShowAlert } from './weather.js';

export async function calculateAndSaveRoute() {
    const startInput = document.getElementById('start-address');
    const startAddress = startInput.dataset.coordinates || startInput.value;
    const endAddress = document.getElementById('end-address').value;
    const transportMode = document.getElementById('transport-mode').value;

    if (!startAddress || !endAddress) {
        showError('Please enter both start and end addresses');
        return;
    }

    // Check for rain alert if bike or bubi mode
    if (transportMode === 'bike' || transportMode === 'bubi') {
        const shouldProceed = await checkRainAndShowAlert();
        if (shouldProceed === false) {
            return; // User cancelled due to rain
        }
    }

    showLoading();
    clearMarkers();
    clearRoute();

    try {
        const [startData, endData] = await Promise.all([
            geocodeAddress(startAddress),
            geocodeAddress(endAddress)
        ]);

        if (!startData.success || !endData.success) {
            showError('Unable to find addresses');
            return;
        }

        const startCoords = { lat: startData.latitude, lon: startData.longitude };
        const endCoords = { lat: endData.latitude, lon: endData.longitude };

        const startMark = addMarker(startCoords.lat, startCoords.lon, startIcon, '<b>Start</b>');
        setStartMarker(startMark);

        const endMark = addMarker(endCoords.lat, endCoords.lon, endIcon, '<b>End</b>');
        setEndMarker(endMark);

        let routeResult;
        
        switch(transportMode) {
            case 'bike':
                routeResult = await calculateSimpleRoute(startCoords, endCoords, 'bike');
                break;
            case 'bubi':
                routeResult = await calculateRouteWithStations(startCoords, endCoords);
                break;
            case 'transport':
                routeResult = await calculateTransportRoute(startCoords, endCoords);
                break;
            case 'car':
                routeResult = await calculateCarRoute(startCoords, endCoords);
                break;
            default:
                showError('Invalid transport mode');
                return;
        }

        if (routeResult) {
            // Save to database
            await saveRouteToTravels(startCoords, endCoords, transportMode, routeResult);
        }

        const bounds = L.latLngBounds([
            [startCoords.lat, startCoords.lon],
            [endCoords.lat, endCoords.lon]
        ]);
        map.fitBounds(bounds, { padding: [50, 50] });

    } catch (error) {
        showError('Error : ' + error.message);
    } finally {
        hideLoading();
    }
}

async function geocodeAddress(address) {
    const response = await fetch('/api/geocode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address })
    });
    return response.json();
}

async function calculateSimpleRoute(startCoords, endCoords, mode = 'bike') {
    const response = await fetch('/api/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            start_lat: startCoords.lat,
            start_lon: startCoords.lon,
            end_lat: endCoords.lat,
            end_lon: endCoords.lon,
            mode: mode
        })
    });

    const data = await response.json();
    if (data.success) {
        displaySimpleRoute(data.route, mode);
        return {
            distance: data.route.distance,
            duration: data.route.duration,
            cost: 0,
            co2: calculateCO2(data.route.distance, mode)
        };
    } else {
        showError('Unable to calculate the route');
        return null;
    }
}

async function calculateRouteWithStations(startCoords, endCoords) {
    const response = await fetch('/api/route-with-stations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            start_lat: startCoords.lat,
            start_lon: startCoords.lon,
            end_lat: endCoords.lat,
            end_lon: endCoords.lon
        })
    });

    const data = await response.json();
    if (data.success) {
        displayRouteWithStations(data);
        return {
            distance: data.total_distance,
            duration: data.total_duration,
            cost: 0,
            co2: calculateCO2(data.total_distance, 'bubi')
        };
    } else {
        showError('Unable to calculate the route');
        return null;
    }
}

function displaySimpleRoute(route, mode = 'bike') {
    const coords = route.coordinates.map(coord => [coord[1], coord[0]]);

    const modeColors = {
        'bike': '#3498db',
        'car': '#e74c3c'
    };

    const layer = L.polyline(coords, {
        color: modeColors[mode] || '#3498db',
        weight: 5,
        opacity: 0.7
    }).addTo(map);

    setRouteLayer(layer);

    const distance = (route.distance / 1000).toFixed(2);
    const duration = Math.round(route.duration / 60);

    const modeIcons = {
        'bike': 'bicycle',
        'car': 'car'
    };

    const modeNames = {
        'bike': 'Bike',
        'car': 'Car'
    };

    document.getElementById('route-info').style.display = 'block';
    document.getElementById('route-info').innerHTML = `
        <h3><i class="fas fa-${modeIcons[mode] || 'bicycle'}"></i> ${modeNames[mode] || 'Bike'} itinerary</h3>
        <p><strong>Distance :</strong> ${distance} km</p>
        <p><strong>Estimate time :</strong> ${duration} minutes</p>
    `;
}

function displayRouteWithStations(data) {
    const { start_station, end_station, routes, total_distance, total_duration } = data;

    if (start_station) {
        addMarker(start_station.lat, start_station.lon, stationIcon,
            `<b>Start station</b><br>${start_station.name}`);
    }

    if (end_station) {
        addMarker(end_station.lat, end_station.lon, stationIcon,
            `<b>End station</b><br>${end_station.name}`);
    }

    if (routes.walk_to_start) {
        const coords = routes.walk_to_start.coordinates.map(c => [c[1], c[0]]);
        L.polyline(coords, { color: '#95a5a6', weight: 4, opacity: 0.7, dashArray: '5, 10' }).addTo(map);
    }

    if (routes.bike) {
        const coords = routes.bike.coordinates.map(c => [c[1], c[0]]);
        const layer = L.polyline(coords, { color: '#27ae60', weight: 5, opacity: 0.8 }).addTo(map);
        setRouteLayer(layer);
    }

    if (routes.walk_from_end) {
        const coords = routes.walk_from_end.coordinates.map(c => [c[1], c[0]]);
        L.polyline(coords, { color: '#95a5a6', weight: 4, opacity: 0.7, dashArray: '5, 10' }).addTo(map);
    }

    const distance = (total_distance / 1000).toFixed(2);
    const duration = Math.round(total_duration / 60);

    document.getElementById('route-info').style.display = 'block';
    document.getElementById('route-info').innerHTML = `
        <h3><i class="fas fa-route"></i> Itinerary with bubi</h3>
        <div class="route-segment walk">
            <strong>🚶 Walk to the station</strong><br>
            ${start_station.name}<br>
            ${(start_station.distance).toFixed(2)} km
        </div>
        <div class="route-segment bike">
            <strong>🚴 Bike route</strong><br>
            ${start_station.name} → ${end_station.name}<br>
            ${(routes.bike.distance / 1000).toFixed(2)} km
        </div>
        <div class="route-segment walk">
            <strong>🚶 Walk from the station</strong><br>
            ${end_station.name}<br>
            ${(end_station.distance).toFixed(2)} km
        </div>
        <p><strong>Total distance : </strong> ${distance} km</p>
        <p><strong>Estimate Time : </strong> ${duration} minutes</p>
    `;
}

async function calculateTransportRoute(startCoords, endCoords) {
    const response = await fetch('/api/route/transport', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            start_lat: startCoords.lat,
            start_lon: startCoords.lon,
            end_lat: endCoords.lat,
            end_lon: endCoords.lon
        })
    });

    const data = await response.json();
    if (data.success && data.route) {
        displayTransportRoute(data.route);
        return {
            distance: data.route.distance || 0,
            duration: data.route.duration || 0,
            cost: data.route.cost || 0,
            co2: calculateCO2(data.route.distance || 0, 'transport')
        };
    } else {
        showError('Unable to calculate public transport route');
        return null;
    }
}

async function calculateCarRoute(startCoords, endCoords) {
    const response = await fetch('/api/route/car', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            start_lat: startCoords.lat,
            start_lon: startCoords.lon,
            end_lat: endCoords.lat,
            end_lon: endCoords.lon,
            mode: 'driving'
        })
    });

    const data = await response.json();
    if (data.success) {
        displaySimpleRoute(data.route, 'car');
        return {
            distance: data.route.distance,
            duration: data.route.duration,
            cost: 0,
            co2: calculateCO2(data.route.distance, 'car')
        };
    } else {
        showError('Unable to calculate car route');
        return null;
    }
}

function displayTransportRoute(route) {
    document.getElementById('route-info').style.display = 'block';
    
    const distance = route.distance ? (route.distance / 1000).toFixed(2) : 'N/A';
    const duration = route.duration ? Math.round(route.duration / 60) : 'N/A';
    
    document.getElementById('route-info').innerHTML = `
        <h3><i class="fas fa-train"></i> Public Transport itinerary</h3>
        <p><strong>Distance :</strong> ${distance} km</p>
        <p><strong>Estimate time :</strong> ${duration} minutes</p>
        <p class="info-note"><i class="fas fa-info-circle"></i> Detailed public transport route information is available through BKK.</p>
    `;
}

function calculateCO2(distance, mode) {
    // CO2 emissions in kg per km
    // Source: Average emissions based on transport mode
    // Bike/Bubi: 0 kg (zero emissions)
    // Public transport: 0.05 kg/km (average for buses/trains)
    // Car: 0.12 kg/km (average for gasoline car)
    const emissionFactors = {
        'bike': 0,
        'bubi': 0,
        'transport': 0.05,
        'car': 0.12
    };
    
    const distanceKm = distance / 1000;
    return distanceKm * (emissionFactors[mode] || 0);
}

async function saveRouteToTravels(startCoords, endCoords, transportMode, routeData) {
    try {
        // Check if user is logged in
        const userStr = localStorage.getItem('user');
        if (!userStr) {
            console.log('User not logged in, skipping travel save');
            return;
        }

        let user;
        try {
            user = JSON.parse(userStr);
        } catch (parseError) {
            console.error('Invalid user data in localStorage:', parseError);
            return;
        }
        
        // Get current weather ID if available
        let weatherId = null;
        try {
            const weatherResponse = await fetch('/api/weather/latest');
            const weatherData = await weatherResponse.json();
            if (weatherData.success && weatherData.weather && weatherData.weather.id) {
                weatherId = weatherData.weather.id;
            }
        } catch (e) {
            console.log('Could not fetch weather ID:', e);
        }

        // Prepare travel data
        const travelData = {
            user_id: user.id,
            duration: routeData.duration,
            distance: routeData.distance / 1000, // Convert to km
            start_lat: startCoords.lat,
            start_lon: startCoords.lon,
            end_lat: endCoords.lat,
            end_lon: endCoords.lon,
            transportType: transportMode,
            cost: routeData.cost || 0,
            CO2Emissions: routeData.co2 || 0,
            weather_id: weatherId,
            pass_id: null
        };

        // Save to database
        const response = await fetch('/api/travels', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(travelData)
        });

        const result = await response.json();
        
        if (result.success) {
            console.log('Travel saved successfully:', result.travel_id);
            // Show success notification
            showSuccess('Route calculated and saved to your travel history!');
        } else {
            console.error('Failed to save travel:', result.error);
            showError('Route calculated but could not be saved to history');
        }
    } catch (error) {
        console.error('Error saving travel:', error);
        showError('Route calculated but could not be saved to history');
    }
}

function showSuccess(message) {
    const notification = document.createElement('div');
    notification.className = 'notification success';
    notification.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
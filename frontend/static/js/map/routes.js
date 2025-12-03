import { map, startIcon, endIcon, stationIcon } from './init.js';
import { showLoading, hideLoading, showError } from './ui.js';
import { clearMarkers, clearRoute, addMarker, setStartMarker, setEndMarker, setRouteLayer } from './markers.js';

export async function calculateRoute() {
    const startInput = document.getElementById('start-address');
    const startAddress = startInput.dataset.coordinates || startInput.value;
    const endAddress = document.getElementById('end-address').value;
    const useBubi = document.getElementById('use-bubi').checked;

    if (!startAddress || !endAddress) {
        showError('Please enter both start and end addresses');
        return;
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
            showError('Impossible to find addresses');
            return;
        }

        const startCoords = { lat: startData.latitude, lon: startData.longitude };
        const endCoords = { lat: endData.latitude, lon: endData.longitude };

        const startMark = addMarker(startCoords.lat, startCoords.lon, startIcon, '<b>Start</b>');
        setStartMarker(startMark);

        const endMark = addMarker(endCoords.lat, endCoords.lon, endIcon, '<b>End</b>');
        setEndMarker(endMark);

        if (useBubi) {
            await calculateRouteWithStations(startCoords, endCoords);
        } else {
            await calculateSimpleRoute(startCoords, endCoords);
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

async function calculateSimpleRoute(startCoords, endCoords) {
    const response = await fetch('/api/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            start_lat: startCoords.lat,
            start_lon: startCoords.lon,
            end_lat: endCoords.lat,
            end_lon: endCoords.lon,
            mode: 'bike'
        })
    });

    const data = await response.json();
    if (data.success) {
        displaySimpleRoute(data.route);
    } else {
        showError('Impossible to calculate the route');
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
    } else {
        showError('Impossible to calculate the route');
    }
}

function displaySimpleRoute(route) {
    const coords = route.coordinates.map(coord => [coord[1], coord[0]]);

    const layer = L.polyline(coords, {
        color: '#3498db',
        weight: 5,
        opacity: 0.7
    }).addTo(map);

    setRouteLayer(layer);

    const distance = (route.distance / 1000).toFixed(2);
    const duration = Math.round(route.duration / 60);

    document.getElementById('route-info').style.display = 'block';
    document.getElementById('route-info').innerHTML = `
        <h3><i class="fas fa-bicycle"></i>Bike itinerary</h3>
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
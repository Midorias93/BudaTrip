const map = L.map('map').setView([47.4979, 19.0402], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// ============================================
// Center the map on user's location if available
// ============================================

async function initializeUserPosition() {
    showLoading();

    try {
        const response = await fetch('/api/my-location');
        const data = await response.json();

        if (data.success) {
            const { latitude, longitude } = data;

            map.setView([latitude, longitude], 15);

            console.log(`Position trouvée: ${latitude}, ${longitude}`);
        } else {
            console.warn('Impossible to get user location, defaulting to Budapest');
        }
    } catch (error) {
        console.error('Error while get position', error);
        showError('Position not found, defaulting to Budapest');
    } finally {
        hideLoading();
    }
}

initializeUserPosition();

// ============================================
// GLOBAL VARIABLES
// ============================================

let markers = [];
let routeLayer = null;
let stationsData = null;
let startMarker = null;
let endMarker = null;

// ============================================
// CUSTOM ICONS
// ============================================

const startIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

const endIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

const stationIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// ============================================
// USEFULLY FUNCTIONS
// ============================================

function showLoading() {
    document.getElementById('loading').classList.add('active');
}

function hideLoading() {
    document.getElementById('loading').classList.remove('active');
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.classList.add('active');
    setTimeout(() => {
        errorDiv.classList.remove('active');
    }, 5000);
}

function clearMarkers() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
}

function clearRoute() {
    if (routeLayer) {
        map.removeLayer(routeLayer);
        routeLayer = null;
    }
}

// ============================================
// ONGLETS
// ============================================

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    event.target.classList.add('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');

    clearMarkers();
    clearRoute();
}

// ============================================
// SEARCH ADDRESS
// ============================================

async function searchAddress() {
    const address = document.getElementById('search-address').value;
    if (!address) {
        showError('Please enter an address');
        return;
    }

    showLoading();
    clearMarkers();

    try {
        const response = await fetch('/api/geocode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ address })
        });

        const data = await response.json();

        if (data.success) {
            const { latitude, longitude, address: fullAddress } = data;

            map.setView([latitude, longitude], 16);

            const marker = L.marker([latitude, longitude])
                .addTo(map)
                .bindPopup(`<b>${fullAddress}</b>`)
                .openPopup();
            markers.push(marker);

            document.getElementById('search-info').style.display = 'block';
            document.getElementById('search-info').innerHTML = `
                <h3><i class="fas fa-info-circle"></i> Résultat</h3>
                <p><strong>Adresse:</strong> ${fullAddress}</p>
                <p><strong>Coordonnées:</strong> ${latitude.toFixed(5)}, ${longitude.toFixed(5)}</p>
            `;
        } else {
            showError(data.error || 'Adress not found');
        }
    } catch (error) {
        showError('Error while searching ' + error.message);
    } finally {
        hideLoading();
    }
}

// ============================================
// GET MY LOCATION
// ============================================

async function getMyLocation() {
    showLoading();
    clearMarkers();

    try {
        const response = await fetch('/api/my-location');
        const data = await response.json();

        if (data.success) {
            const { latitude, longitude } = data;

            map.setView([latitude, longitude], 16);

            const marker = L.marker([latitude, longitude])
                .addTo(map)
                .bindPopup('<b>Your Position</b>')
                .openPopup();
            markers.push(marker);

            document.getElementById('search-info').style.display = 'block';
            document.getElementById('search-info').innerHTML = `
                <h3><i class="fas fa-location-arrow"></i> Votre position</h3>
                <p><strong>Latitude:</strong> ${latitude.toFixed(5)}</p>
                <p><strong>Longitude:</strong> ${longitude.toFixed(5)}</p>
            `;
        } else {
            showError('Impossible to get your location');
        }
    } catch (error) {
        showError('Error : ' + error.message);
    } finally {
        hideLoading();
    }
}

// ============================================
// GET ITINERARY
// ============================================

async function calculateRoute() {
    const startAddress = document.getElementById('start-address').value;
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
        const startResponse = await fetch('/api/geocode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address: startAddress })
        });
        const startData = await startResponse.json();

        const endResponse = await fetch('/api/geocode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address: endAddress })
        });
        const endData = await endResponse.json();

        if (!startData.success || !endData.success) {
            showError('Impossible to find addresses');
            return;
        }

        const startCoords = {
            lat: startData.latitude,
            lon: startData.longitude
        };
        const endCoords = {
            lat: endData.latitude,
            lon: endData.longitude
        };

        startMarker = L.marker([startCoords.lat, startCoords.lon], { icon: startIcon })
            .addTo(map)
            .bindPopup('<b>Départ</b>');
        markers.push(startMarker);

        endMarker = L.marker([endCoords.lat, endCoords.lon], { icon: endIcon })
            .addTo(map)
            .bindPopup('<b>Arrivée</b>');
        markers.push(endMarker);

        if (useBubi) {
            const routeResponse = await fetch('/api/route-with-stations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    start_lat: startCoords.lat,
                    start_lon: startCoords.lon,
                    end_lat: endCoords.lat,
                    end_lon: endCoords.lon
                })
            });
            const routeData = await routeResponse.json();

            if (routeData.success) {
                displayRouteWithStations(routeData);
            } else {
                showError('Impossible to calculate the route');
            }
        } else {
            const routeResponse = await fetch('/api/route', {
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
            const routeData = await routeResponse.json();

            if (routeData.success) {
                displaySimpleRoute(routeData.route);
            } else {
                showError('Impossible to calculate the route');
            }
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

// ============================================
// DISPLAY ROUTE
// ============================================

function displaySimpleRoute(route) {
    const coords = route.coordinates.map(coord => [coord[1], coord[0]]);

    routeLayer = L.polyline(coords, {
        color: '#3498db',
        weight: 5,
        opacity: 0.7
    }).addTo(map);

    const distance = (route.distance / 1000).toFixed(2);
    const duration = Math.round(route.duration / 60);

    document.getElementById('route-info').style.display = 'block';
    document.getElementById('route-info').innerHTML = `
        <h3><i class="fas fa-bicycle"></i> Itinéraire à vélo</h3>
        <p><strong>Distance:</strong> ${distance} km</p>
        <p><strong>Durée estimée:</strong> ${duration} minutes</p>
    `;
}

function displayRouteWithStations(data) {
    const { start_station, end_station, routes, total_distance, total_duration } = data;

    if (start_station) {
        const stationMarker = L.marker([start_station.lat, start_station.lon], { icon: stationIcon })
            .addTo(map)
            .bindPopup(`<b>Station de départ</b><br>${start_station.name}`);
        markers.push(stationMarker);
    }

    if (end_station) {
        const stationMarker = L.marker([end_station.lat, end_station.lon], { icon: stationIcon })
            .addTo(map)
            .bindPopup(`<b>Station d'arrivée</b><br>${end_station.name}`);
        markers.push(stationMarker);
    }

    if (routes.walk_to_start) {
        const coords = routes.walk_to_start.coordinates.map(c => [c[1], c[0]]);
        L.polyline(coords, { color: '#95a5a6', weight: 4, opacity: 0.7, dashArray: '5, 10' }).addTo(map);
    }

    if (routes.bike) {
        const coords = routes.bike.coordinates.map(c => [c[1], c[0]]);
        routeLayer = L.polyline(coords, { color: '#27ae60', weight: 5, opacity: 0.8 }).addTo(map);
    }

    if (routes.walk_from_end) {
        const coords = routes.walk_from_end.coordinates.map(c => [c[1], c[0]]);
        L.polyline(coords, { color: '#95a5a6', weight: 4, opacity: 0.7, dashArray: '5, 10' }).addTo(map);
    }

    const distance = (total_distance / 1000).toFixed(2);
    const duration = Math.round(total_duration / 60);

    document.getElementById('route-info').style.display = 'block';
    document.getElementById('route-info').innerHTML = `
        <h3><i class="fas fa-route"></i> Itinéraire avec Bubi</h3>

        <div class="route-segment walk">
            <strong>🚶 Marche jusqu'à la station</strong><br>
            ${start_station.name}<br>
            ${(start_station.distance).toFixed(2)} km
        </div>

        <div class="route-segment bike">
            <strong>🚴 Trajet à vélo</strong><br>
            ${start_station.name} → ${end_station.name}<br>
            ${(routes.bike.distance / 1000).toFixed(2)} km
        </div>

        <div class="route-segment walk">
            <strong>🚶 Marche depuis la station</strong><br>
            ${end_station.name}<br>
            ${(end_station.distance).toFixed(2)} km
        </div>

        <p><strong>Distance totale:</strong> ${distance} km</p>
        <p><strong>Durée totale estimée:</strong> ${duration} minutes</p>
    `;
}

// ============================================
// MANAGE STATIONS
// ============================================

async function showAllStations() {
    showLoading();
    clearMarkers();

    try {
        const response = await fetch('/api/stations');
        const data = await response.json();

        if (data.success) {
            stationsData = data.stations;

            data.stations.forEach(station => {
                const marker = L.marker([station.lat, station.lon], { icon: stationIcon })
                    .addTo(map)
                    .bindPopup(`<b>${station.name}</b>`);
                markers.push(marker);
            });

            document.getElementById('station-info').style.display = 'block';
            document.getElementById('station-info').innerHTML = `
                <h3><i class="fas fa-bicycle"></i> Stations Bubi</h3>
                <p><strong>Nombre de stations:</strong> ${data.stations.length}</p>
            `;

            const bounds = L.latLngBounds(data.stations.map(s => [s.lat, s.lon]));
            map.fitBounds(bounds, { padding: [50, 50] });
        } else {
            showError('Impossible to load stations');
        }
    } catch (error) {
        showError('Error : ' + error.message);
    } finally {
        hideLoading();
    }
}

async function findNearestStation() {
    showLoading();
    clearMarkers();

    try {
        const locationResponse = await fetch('/api/my-location');
        const locationData = await locationResponse.json();

        if (!locationData.success) {
            showError('Impossible to get your location');
            return;
        }

        const { latitude, longitude } = locationData;

        const posMarker = L.marker([latitude, longitude])
            .addTo(map)
            .bindPopup('<b>Votre position</b>');
        markers.push(posMarker);

        const stationResponse = await fetch('/api/nearest-station', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lat: latitude, lon: longitude })
        });
        const stationData = await stationResponse.json();

        if (stationData.success) {
            const station = stationData.station;

            const stationMarker = L.marker([station.lat, station.lon], { icon: stationIcon })
                .addTo(map)
                .bindPopup(`<b>${station.name}</b><br>Distance: ${station.distance} km`)
                .openPopup();
            markers.push(stationMarker);

            L.polyline([
                [latitude, longitude],
                [station.lat, station.lon]
            ], {
                color: '#e74c3c',
                weight: 3,
                opacity: 0.7,
                dashArray: '10, 10'
            }).addTo(map);

            document.getElementById('station-info').style.display = 'block';
            document.getElementById('station-info').innerHTML = `
                <h3><i class="fas fa-map-marker-alt"></i> Station la plus proche</h3>
                <p><strong>Nom:</strong> ${station.name}</p>
                <p><strong>Distance:</strong> ${station.distance} km</p>
            `;

            const bounds = L.latLngBounds([
                [latitude, longitude],
                [station.lat, station.lon]
            ]);
            map.fitBounds(bounds, { padding: [100, 100] });
        } else {
            showError('No station found');
        }
    } catch (error) {
        showError('Error : ' + error.message);
    } finally {
        hideLoading();
    }
}

async function showAllWeather() {
    showLoading();
    clearMarkers();

    try {
        const response = await fetch('/api/weather');
        const data = await response.json();
        if (data.success) {
            const { precipitation, temperature, wind_speed } = data.weather;
            document.getElementById('weather-info').style.display = 'block';
            document.getElementById('weather-info').innerHTML = `
                <h3><i class="fas fa-cloud-sun"></i> Actual Meteo </h3>
                <p><strong>🌡️ Temperature :</strong> ${temperature} °C</p>
                <p><strong>💧 Precipitation :</strong> ${precipitation} mm</p>
                <p><strong>💨 Wind Speed :</strong> ${wind_speed} km/h</p>
                `;
        }
    } catch (error) {
        showError('Error : ' + error.message);
    } finally {
        hideLoading();
    }
}

// ============================================
// EVENT LISTENERS FOR ENTER KEY
// ============================================

document.getElementById('search-address').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') searchAddress();
});

document.getElementById('start-address').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') document.getElementById('end-address').focus();
});

document.getElementById('end-address').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') calculateRoute();
});

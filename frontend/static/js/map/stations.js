import { map, stationIcon } from './init.js';
import { showLoading, hideLoading, showError } from './ui.js';
import { clearMarkers, addMarker } from './markers.js';

let stationsData = null;

export async function showAllStations() {
    showLoading();
    clearMarkers();

    try {
        const response = await fetch('/api/stations');
        const data = await response.json();

        if (data.success) {
            stationsData = data.stations;

            data.stations.forEach(station => {
                addMarker(station.lat, station.lon, stationIcon, `<b>${station.name}</b>`);
            });

            document.getElementById('station-info').style.display = 'block';
            document.getElementById('station-info').innerHTML = `
                <h3><i class="fas fa-bicycle"></i> Stations Bubi</h3>
                <p><strong>Number of station : </strong> ${data.stations.length}</p>
            `;

            const bounds = L.latLngBounds(data.stations.map(s => [s.lat, s.lon]));
            map.fitBounds(bounds, { padding: [50, 50] });
        } else {
            showError('Unable to load stations');
        }
    } catch (error) {
        showError('Error : ' + error.message);
    } finally {
        hideLoading();
    }
}

export async function findNearestStation() {
    showLoading();
    clearMarkers();

    try {
        const locationResponse = await fetch('/api/my-location');
        const locationData = await locationResponse.json();

        if (!locationData.success) {
            showError('Unable to get your location');
            return;
        }

        const { latitude, longitude } = locationData;

        const posMarker = addMarker(latitude, longitude, null, '<b>Your position</b>');

        const stationResponse = await fetch('/api/nearest-station', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lat: latitude, lon: longitude })
        });

        const stationData = await stationResponse.json();

        if (stationData.success) {
            const station = stationData.station;

            const stationMarker = addMarker(station.lat, station.lon, stationIcon,
                `<b>${station.name}</b><br>Distance: ${station.distance} km`);
            stationMarker.openPopup();

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
                <h3><i class="fas fa-map-marker-alt"></i> Nearest station</h3>
                <p><strong>Name : </strong> ${station.name}</p>
                <p><strong>Distance : </strong> ${station.distance} km</p>
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

export { stationsData };
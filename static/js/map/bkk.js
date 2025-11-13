import { stationIcon } from './init.js';
import { addMarker } from './markers.js';

export async function findNearestBkkStop() {
    const resBox = document.getElementById('bkk-nearest-result');
    const textEl = document.getElementById('bkk-nearest-text');

    resBox.style.display = 'block';
    textEl.textContent = 'Recherche…';

    try {
        const res = await fetch('/api/bkk/nearest-stop', {
            headers: { 'Accept': 'application/json' }
        });
        const data = await res.json();


        const { stop_name, stop_id, stop_lat, stop_lon, distance_km } = data;

        const stationMarker = addMarker(stop_lat, stop_lon, stationIcon,
            `<b>${stop_name}</b><br>Distance: ${distance_km} km`);
        stationMarker.openPopup();

        textEl.textContent = `Nom: ${stop_name} | ID: ${stop_id} | Lat: ${stop_lat} | Lon: ${stop_lon} | distance: ${distance_km}`;
    } catch (e) {
        textEl.textContent = "Erreur lors de la récupération de l'arrêt.";
    }
}
import { showSearchNotification } from './ui.js';
import { clearMarkers, clearRoute } from './markers.js';

window.currentWeather = null;

export async function showAllWeather() {
    try {
        const response = await fetch('/api/weather');
        const data = await response.json();

        if (data.success) {
            const { precipitation, temperature, wind_speed } = data.weather;

            document.getElementById('temp').textContent = `${temperature}°C`;
            document.getElementById('wind').textContent = `${wind_speed} km/h`;
            document.getElementById('precipitation').textContent = `${precipitation}%`;

            window.currentWeather = { precipitation, temperature, wind_speed };
        }
    } catch (error) {
        console.error('Erreur météo:', error);
        document.getElementById('temp').textContent = 'N/A';
        document.getElementById('wind').textContent = 'N/A';
        document.getElementById('precipitation').textContent = 'N/A';
    }
}

export function checkRainAndShowAlert() {
    if (window.currentWeather && window.currentWeather.precipitation > 30) {
        showRainAlert();
    }
}

function showRainAlert() {
    const overlay = document.getElementById('rain-alert-overlay');
    const alert = document.getElementById('rain-alert');

    if (window.currentWeather) {
        document.getElementById('rain-precipitation').textContent =
            `${window.currentWeather.precipitation}%`;
        document.getElementById('rain-temperature').textContent =
            `${window.currentWeather.temperature}°C`;
        document.getElementById('rain-wind').textContent =
            `${window.currentWeather.wind_speed} km/h`;
    }

    overlay.classList.add('show');
    alert.classList.add('show');
}

export function closeRainAlert() {
    const overlay = document.getElementById('rain-alert-overlay');
    const alert = document.getElementById('rain-alert');

    overlay.classList.remove('show');
    alert.classList.remove('show');
}

export function switchToBKK() {
    closeRainAlert();

    document.querySelectorAll('.tab-btn-locomotion').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.includes('BKK') || btn.onclick.toString().includes('bkk')) {
            btn.classList.add('active');
        }
    });

    document.querySelectorAll('.tab-content-locomotion').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById('tab-bkk').classList.add('active');

    clearMarkers();
    clearRoute();

    showSearchNotification('Switched to public transport (BKK)', 'success');
}

export function initWeather() {
    showAllWeather();
    setInterval(showAllWeather, 600000);
}
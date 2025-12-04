import { showSearchNotification } from './ui.js';
import { clearMarkers, clearRoute } from './markers.js';

window.currentWeather = null;

export async function fetchAndSaveWeather() {
    try {
        const response = await fetch('/api/weather/current');
        const data = await response.json();

        if (data.success) {
            const { temperature, precipitation, wind_speed } = data.weather;

            document.getElementById('temp').textContent = `${temperature}°C`;
            document.getElementById('wind').textContent = `${wind_speed} km/h`;
            document.getElementById('precipitation').textContent = `${precipitation}%`;

            window.currentWeather = { precipitation, temperature, wind_speed };
        }
    } catch (error) {
        console.error('Weather fetch error:', error);
        // Fallback to latest weather from database
        showLatestWeather();
    }
}

export async function showLatestWeather() {
    try {
        const response = await fetch('/api/weather/latest');
        const data = await response.json();

        if (data.success) {
            const { precipitation, temperature, windSpeed } = data.weather;

            document.getElementById('temp').textContent = `${temperature}°C`;
            document.getElementById('wind').textContent = `${windSpeed} km/h`;
            document.getElementById('precipitation').textContent = `${precipitation}%`;

            window.currentWeather = { precipitation, temperature, wind_speed: windSpeed };
        }
    } catch (error) {
        console.error('Weather error:', error);
        document.getElementById('temp').textContent = 'N/A';
        document.getElementById('wind').textContent = 'N/A';
        document.getElementById('precipitation').textContent = 'N/A';
    }
}

export async function showAllWeather() {
    // First try to fetch and save new weather
    await fetchAndSaveWeather();
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
    // Refresh weather every 30 minutes (1800000 milliseconds)
    setInterval(showAllWeather, 1800000);
}
import { showSearchNotification } from './ui.js';
import { clearMarkers, clearRoute } from './markers.js';

window.currentWeather = null;

// Store the rain alert resolve function at module level
let rainAlertResolveCallback = null;

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
    return new Promise((resolve) => {
        if (window.currentWeather && window.currentWeather.precipitation > 30) {
            showRainAlert(resolve);
        } else {
            resolve(true); // No rain, proceed
        }
    });
}

function showRainAlert(resolve) {
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
    
    // Store resolve function at module level
    rainAlertResolveCallback = resolve;
}

export function closeRainAlert() {
    const overlay = document.getElementById('rain-alert-overlay');
    const alert = document.getElementById('rain-alert');

    overlay.classList.remove('show');
    alert.classList.remove('show');
    
    // Resolve with true (continue anyway)
    if (rainAlertResolveCallback) {
        rainAlertResolveCallback(true);
        rainAlertResolveCallback = null;
    }
}

export function switchToBKK() {
    closeRainAlert();
    
    // Switch transport mode to BKK
    const transportMode = document.getElementById('transport-mode');
    if (transportMode) {
        transportMode.value = 'transport';
    }

    clearMarkers();
    clearRoute();

    showSearchNotification('Switched to public transport (BKK)', 'success');
    
    // Resolve with false (don't continue with bike/bubi)
    if (rainAlertResolveCallback) {
        rainAlertResolveCallback(false);
        rainAlertResolveCallback = null;
    }
}

export function initWeather() {
    showAllWeather();
    // Refresh weather every 30 minutes (1800000 milliseconds)
    setInterval(showAllWeather, 1800000);
}
import { initializeUserPosition } from './map/init.js';
import { searchAddress, getMyLocation, setMyLocation } from './map/search.js';
import { calculateRoute } from './map/routes.js';
import { showAllStations, findNearestStation } from './map/stations.js';
import { findNearestBkkStop } from './map/bkk.js';
import { initWeather, closeRainAlert, switchToBKK } from './map/weather.js';
import { initAuth, openLogin, openSignup, toggleUserDropdown, handleLogout } from './map/auth.js';
import { switchTab, switchTabLocomotion } from './map/ui.js';
import { clearMarkers, clearRoute } from './map/markers.js';

// Initialisation
initializeUserPosition();
initWeather();
initAuth();

// Expose functions globally for HTML onclick handlers
window.searchAddress = searchAddress;
window.getMyLocation = getMyLocation;
window.setMyLocation = setMyLocation;
window.calculateRoute = calculateRoute;
window.showAllStations = showAllStations;
window.findNearestStation = findNearestStation;
window.findNearestBkkStop = findNearestBkkStop;
window.switchTab = switchTab;
window.switchTabLocomotion = switchTabLocomotion;
window.closeRainAlert = closeRainAlert;
window.switchToBKK = switchToBKK;
window.openLogin = openLogin;
window.openSignup = openSignup;
window.toggleUserDropdown = toggleUserDropdown;
window.handleLogout = handleLogout;

// Event listeners
document.getElementById('quick-search-input')?.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') searchAddress();
});

document.getElementById('start-address')?.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') document.getElementById('end-address').focus();
});

document.getElementById('end-address')?.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') calculateRoute();
});

document.getElementById('bkk-nearest-btn')?.addEventListener('click', findNearestBkkStop);
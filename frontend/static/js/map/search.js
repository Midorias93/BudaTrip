import { map } from './init.js';
import { showLoading, hideLoading, showError } from './ui.js';
import { clearMarkers, addMarker } from './markers.js';

export async function searchAddress() {
    const address = document.getElementById('quick-search-input').value;
    if (!address) {
        showError('Please enter an address');
        return;
    }

    showLoading();
    clearMarkers();

    try {
        const response = await fetch('/api/geocode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address })
        });

        const data = await response.json();

        if (data.success) {
            const { latitude, longitude, address: fullAddress } = data;
            map.setView([latitude, longitude], 16);

            const marker = addMarker(latitude, longitude, null, `<b>${fullAddress}</b>`);
            marker.openPopup();
        } else {
            showError(data.error || 'Adress not found');
        }
    } catch (error) {
        showError('Error while searching ' + error.message);
    } finally {
        hideLoading();
    }
}

export async function getMyLocation() {
    showLoading();
    clearMarkers();

    try {
        const response = await fetch('/api/my-location');
        const data = await response.json();

        if (data.success) {
            const { latitude, longitude } = data;
            map.setView([latitude, longitude], 16);

            const marker = addMarker(latitude, longitude, null, '<b>Your Position</b>');
            marker.openPopup();
        } else {
            showError('Unable to get your location');
        }
    } catch (error) {
        showError('Error : ' + error.message);
    } finally {
        hideLoading();
    }
}

export async function setMyLocation() {
    showLoading();

    try {
        const response = await fetch('/api/my-location');
        const data = await response.json();

        if (data.success) {
            const startInput = document.getElementById('start-address');
            startInput.value = data.latitude + ', ' + data.longitude;
            startInput.style.fontWeight = '500';
            hideLoading();
        }
    } catch (error) {
        showError('Error : ' + error.message);
    }
}
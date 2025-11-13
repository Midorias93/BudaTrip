import { map } from './init.js';

let markers = [];
let routeLayer = null;
let startMarker = null;
let endMarker = null;

export function clearMarkers() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
}

export function clearRoute() {
    if (routeLayer) {
        map.removeLayer(routeLayer);
        routeLayer = null;
    }
}

export function addMarker(lat, lon, icon, popupText) {
    const marker = L.marker([lat, lon], icon ? { icon } : {})
        .addTo(map)
        .bindPopup(popupText);
    markers.push(marker);
    return marker;
}

export function setStartMarker(marker) {
    startMarker = marker;
}

export function setEndMarker(marker) {
    endMarker = marker;
}

export function setRouteLayer(layer) {
    routeLayer = layer;
}

export { markers, routeLayer, startMarker, endMarker };
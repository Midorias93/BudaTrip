import folium
import os
import webbrowser

def display_map(coordinates):

    latitude, longitude = coordinates

    m = folium.Map(location=[latitude, longitude], zoom_start=16, tiles='OpenStreetMap')

    folium.Marker(
        [latitude, longitude],
        popup="Point central",
        tooltip=f"{longitude, latitude}"
    ).add_to(m)

    folium.Circle(
        radius=300,
        location=[latitude, longitude],
        color="blue",
        fill=True,
        fill_opacity=0.2
    ).add_to(m)

    save_and_open_map(m, "quartier.html")

def display_route(start_coords, end_coords, route_data=None, stations=None):
    """
    Affiche un itinéraire sur une carte

    Args:
        start_coords: tuple (lat, lon) du départ
        end_coords: tuple (lat, lon) de l'arrivée
        route_data: données de l'itinéraire (optionnel)
        stations: dict des stations Bubi à afficher (optionnel)
    """
    # Créer la carte centrée entre les deux points
    center_lat = (start_coords[0] + end_coords[0]) / 2
    center_lon = (start_coords[1] + end_coords[1]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles='OpenStreetMap')

    # Marqueur de départ
    folium.Marker(
        start_coords,
        popup="Départ",
        tooltip="Point de départ",
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)

    # Marqueur d'arrivée
    folium.Marker(
        end_coords,
        popup="Arrivée",
        tooltip="Point d'arrivée",
        icon=folium.Icon(color='red', icon='stop')
    ).add_to(m)

    # Afficher l'itinéraire si disponible
    if route_data and 'coordinates' in route_data:
        # Convertir les coordonnées [lon, lat] en [lat, lon] pour folium
        route_coords = [(coord[1], coord[0]) for coord in route_data['coordinates']]

        folium.PolyLine(
            route_coords,
            color='blue',
            weight=5,
            opacity=0.7,
            popup=f"Distance: {route_data['distance'] / 1000:.2f} km<br>Durée: {route_data['duration'] / 60:.0f} min"
        ).add_to(m)

        # Ajouter les informations de l'itinéraire
        info_html = f"""
        <div style="position: fixed; 
                    top: 10px; right: 10px; 
                    background-color: white; 
                    padding: 10px; 
                    border: 2px solid grey; 
                    border-radius: 5px;
                    z-index: 9999;
                    font-size: 14px;">
            <b>Informations de l'itinéraire</b><br>
            📏 Distance: {route_data['distance'] / 1000:.2f} km<br>
            ⏱️ Durée estimée: {route_data['duration'] / 60:.0f} minutes<br>
            🚴 Mode: Vélo
        </div>
        """
        m.get_root().html.add_child(folium.Element(info_html))
    else:
        # Si pas d'itinéraire, tracer une ligne droite
        folium.PolyLine(
            [start_coords, end_coords],
            color='gray',
            weight=3,
            opacity=0.5,
            dash_array='10'
        ).add_to(m)

    # Afficher les stations Bubi si fournies
    if stations:
        for name, coords in stations.items():
            folium.Marker(
                coords,
                popup=name,
                tooltip=name,
                icon=folium.Icon(color='orange', icon='bicycle', prefix='fa')
            ).add_to(m)

    save_and_open_map(m, "itineraire.html")


def display_multiple_stations(stations, center_coords=None):
    """
    Affiche plusieurs stations Bubi sur une carte

    Args:
        stations: dict des stations {nom: (lat, lon)}
        center_coords: coordonnées du centre (optionnel)
    """
    if center_coords:
        center_lat, center_lon = center_coords
    else:
        # Calculer le centre à partir des stations
        lats = [coord[0] for coord in stations.values()]
        lons = [coord[1] for coord in stations.values()]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles='OpenStreetMap')

    for name, coords in stations.items():
        folium.Marker(
            coords,
            popup=f"<b>{name}</b>",
            tooltip=name,
            icon=folium.Icon(color='blue', icon='bicycle', prefix='fa')
        ).add_to(m)

    save_and_open_map(m, "stations.html")


def save_and_open_map(map_obj, filename):
    """Sauvegarde et ouvre une carte dans le navigateur"""
    if not os.path.exists("maps"):
        os.makedirs("maps")

    filepath = f"maps/{filename}"
    map_obj.save(filepath)
    webbrowser.open('file://' + os.path.realpath(filepath))


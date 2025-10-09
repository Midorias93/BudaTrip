import Location
import Display
import Itinerary


def main():
    print("=== Application d'itinéraire vélo ===\n")

    # 1. Obtenir la position actuelle
    print("📍 Récupération de votre position...")
    my_coords = Location.get_my_coordinatess()
    print(f"Position: {my_coords}\n")

    # 2. Récupérer les stations Bubi
    print("🚲 Chargement des stations Bubi...")
    stations = Location.bubi_location()
    print(f"Nombre de stations: {len(stations)}\n")

    # 3. Trouver la station la plus proche
    print("🔍 Recherche de la station la plus proche...")
    nearest = Location.find_nearest_station(my_coords, stations)
    if nearest:
        station_name, station_coords, distance = nearest
        print(f"Station la plus proche: {station_name}")
        print(f"Distance: {distance:.2f} km\n")

    # 4. Exemple d'itinéraire entre deux stations
    print("🗺️ Création d'un itinéraire...")

    # Station de départ
    start_station = "Barázda utca"
    if start_station in stations:
        start_coords = stations[start_station]

        # Station d'arrivée (exemple)
        end_station = list(stations.keys())[10]  # Prendre une autre station
        end_coords = stations[end_station]

        print(f"Départ: {start_station}")
        print(f"Arrivée: {end_station}")

        # Obtenir l'itinéraire
        route = Itinerary.get_route(start_coords, end_coords, mode='bike')

        if route:
            print(f"\n✅ Itinéraire trouvé!")
            print(f"Distance: {route['distance'] / 1000:.2f} km")
            print(f"Durée: {route['duration'] / 60:.0f} minutes")

            # Afficher l'itinéraire sur la carte
            Display.display_route(start_coords, end_coords, route)
        else:
            print("❌ Impossible de calculer l'itinéraire")
            Display.display_route(start_coords, end_coords)

    # 5. Afficher toutes les stations
    # Display.display_multiple_stations(stations, my_coords)


def custom_route():
    """Créer un itinéraire personnalisé"""
    print("\n=== Itinéraire personnalisé ===")

    # Coordonnées de Budapest (exemple)
    start = (47.4979, 19.0402)  # Déli pályaudvar
    end = (47.5636, 19.0947)  # Örs vezér tere

    print(f"Départ: {start}")
    print(f"Arrivée: {end}")

    route = Itinerary.get_route(start, end, mode='bike')

    if route:
        Display.display_route(start, end, route)
    else:
        Display.display_route(start, end)


if __name__ == "__main__":
    print(Location.get_coordinates("Szondi u 47 1063, Budapest"))
    print(Location.get_location("Magyar Tudósok Körútja 2 1117, Budapest"))
    #main()
    #custom_route()  # Décommenter pour tester un itinéraire personnalisé



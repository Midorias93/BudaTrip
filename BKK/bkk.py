# bkk_api.py
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any


class BKKApi:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://futar.bkk.hu/api/query/v1/ws"
        self.dialect = "otp"  # Dialecte standard pour BKK

    def _get_headers(self) -> Dict[str, str]:
        """Retourne les headers par défaut"""
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def _add_api_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ajoute la clé API aux paramètres"""
        params['key'] = self.api_key
        return params

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Effectue une requête avec gestion d'erreur"""
        params = self._add_api_key(params)

        try:
            response = requests.get(endpoint, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur API: {e}")
            if hasattr(response, 'text'):
                print(f"Réponse: {response.text}")
            return None

    # ===== ALERTS =====
    def search_alerts(self,
                      query: Optional[str] = None,
                      start: Optional[int] = None,
                      end: Optional[int] = None,
                      min_result: int = 5,
                      app_version: str = "1.0",
                      version: int = 2,
                      include_references: bool = True) -> Optional[Dict]:
        """
        Recherche des alertes/perturbations

        Args:
            query: Terme de recherche (ID, titre ou description)
            start: Début de l'intervalle (timestamp epoch en secondes)
            end: Fin de l'intervalle (timestamp epoch en secondes)
            min_result: Nombre minimum de résultats
            app_version: Version de l'application cliente
            version: Version de l'API (2 ou 3)
            include_references: Inclure les références
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/alert-search"

        params = {
            'minResult': min_result,
            'appVersion': app_version,
            'version': version,
            'includeReferences': str(include_references).lower()
        }

        if query:
            params['query'] = query
        if start:
            params['start'] = start
        if end:
            params['end'] = end

        return self._make_request(endpoint, params)

    # ===== STOPS =====
    def get_stops_for_location(self,
                               lat: float,
                               lon: float,
                               radius: int = 500,
                               lat_span: Optional[float] = None,
                               lon_span: Optional[float] = None,
                               app_version: str = "1.0",
                               version: int = 2,
                               include_references: bool = True) -> Optional[Dict]:
        """
        Trouve les arrêts à proximité d'une localisation

        Args:
            lat: Latitude du centre
            lon: Longitude du centre
            radius: Rayon de recherche en mètres
            lat_span: Étendue latitudinale (optionnel)
            lon_span: Étendue longitudinale (optionnel)
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/stops-for-location"

        params = {
            'lat': lat,
            'lon': lon,
            'radius': radius,
            'appVersion': app_version,
            'version': version,
            'includeReferences': str(include_references).lower()
        }

        if lat_span:
            params['latSpan'] = lat_span
        if lon_span:
            params['lonSpan'] = lon_span

        return self._make_request(endpoint, params)

    # ===== ARRIVALS & DEPARTURES =====
    def get_arrivals_and_departures(self,
                                    stop_id: str,
                                    minutes_after: int = 30,
                                    minutes_before: int = 0,
                                    only_departures: bool = False,
                                    app_version: str = "1.0",
                                    version: int = 2,
                                    include_references: bool = True) -> Optional[Dict]:
        """
        Récupère les prochains départs/arrivées pour un arrêt

        Args:
            stop_id: ID de l'arrêt (ex: "BKK_F01029")
            minutes_after: Minutes après maintenant
            minutes_before: Minutes avant maintenant
            only_departures: Uniquement les départs
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/arrivals-and-departures-for-stop"

        params = {
            'stopId': stop_id,
            'minutesAfter': minutes_after,
            'minutesBefore': minutes_before,
            'onlyDepartures': str(only_departures).lower(),
            'appVersion': app_version,
            'version': version,
            'includeReferences': str(include_references).lower()
        }

        return self._make_request(endpoint, params)

    # ===== TRIP PLANNING =====
    def plan_trip(self,
                  from_place: str,
                  to_place: str,
                  mode: str = "TRANSIT,WALK",
                  date: Optional[str] = None,
                  time: Optional[str] = None,
                  arrive_by: bool = False,
                  max_walk_distance: int = 1000,
                  wheelchair: bool = False,
                  optimize: str = "QUICK",
                  app_version: str = "1.0",
                  version: int = 2,
                  include_references: bool = True) -> Optional[Dict]:
        """
        Planifie un itinéraire

        Args:
            from_place: Point de départ (format: "Nom::lat,lon" ou "Nom::vertex_id")
            to_place: Point d'arrivée (format: "Nom::lat,lon" ou "Nom::vertex_id")
            mode: Modes de transport séparés par virgule (TRANSIT, WALK, BICYCLE, etc.)
            date: Date au format YYYY-MM-DD
            time: Heure au format HH:MM
            arrive_by: True pour arriver à l'heure spécifiée
            max_walk_distance: Distance maximale de marche en mètres
            wheelchair: Accessible en fauteuil roulant
            optimize: Type d'optimisation (QUICK, SAFE, FLAT, TRIANGLE)
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/plan-trip"

        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        if not time:
            time = datetime.now().strftime("%H:%M")

        params = {
            'fromPlace': from_place,
            'toPlace': to_place,
            'mode': mode,
            'date': date,
            'time': time,
            'arriveBy': str(arrive_by).lower(),
            'maxWalkDistance': max_walk_distance,
            'wheelchair': str(wheelchair).lower(),
            'appVersion': app_version,
            'version': version,
            'includeReferences': str(include_references).lower()
        }

        # Paramètres spécifiques pour le vélo
        if 'BICYCLE' in mode.upper():
            params['optimize'] = optimize
            if optimize == 'TRIANGLE':
                # Valeurs par défaut pour le triangle (peuvent être personnalisées)
                params['triangleSafetyFactor'] = 0.33
                params['triangleSlopeFactor'] = 0.33
                params['triangleTimeFactor'] = 0.34

        return self._make_request(endpoint, params)

    # ===== ROUTES =====
    def get_route_details(self,
                          route_id: str,
                          related: bool = False,
                          app_version: str = "1.0",
                          version: int = 2,
                          include_references: bool = True) -> Optional[Dict]:
        """
        Récupère les détails d'une ligne

        Args:
            route_id: ID de la ligne (ex: "BKK_0650")
            related: Inclure les lignes associées
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/route-details"

        params = {
            'routeId': route_id,
            'related': str(related).lower(),
            'appVersion': app_version,
            'version': version,
            'includeReferences': str(include_references).lower()
        }

        return self._make_request(endpoint, params)

    def get_routes_for_location(self,
                                lat: float,
                                lon: float,
                                radius: int = 500,
                                query: Optional[str] = None,
                                app_version: str = "1.0",
                                version: int = 2,
                                include_references: bool = True) -> Optional[Dict]:
        """
        Trouve les lignes à proximité d'une localisation

        Args:
            lat: Latitude
            lon: Longitude
            radius: Rayon de recherche en mètres
            query: Filtre de recherche
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/routes-for-location"

        params = {
            'lat': lat,
            'lon': lon,
            'radius': radius,
            'appVersion': app_version,
            'version': version,
            'includeReferences': str(include_references).lower()
        }

        if query:
            params['query'] = query

        return self._make_request(endpoint, params)

    # ===== TRIPS =====
    def get_trip_details(self,
                         trip_id: Optional[str] = None,
                         vehicle_id: Optional[str] = None,
                         date: Optional[str] = None,
                         app_version: str = "1.0",
                         version: int = 2,
                         include_references: bool = True) -> Optional[Dict]:
        """
        Récupère les détails d'un trajet

        Args:
            trip_id: ID du trajet
            vehicle_id: ID du véhicule (alternatif)
            date: Date au format YYYYMMDD
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/trip-details"

        params = {
            'appVersion': app_version,
            'version': version,
            'includeReferences': str(include_references).lower()
        }

        if trip_id:
            params['tripId'] = trip_id
        if vehicle_id:
            params['vehicleId'] = vehicle_id
        if date:
            params['date'] = date

        return self._make_request(endpoint, params)

    # ===== VEHICLES =====
    def get_vehicles_for_location(self,
                                  lat: float,
                                  lon: float,
                                  radius: int = 500,
                                  query: Optional[str] = None,
                                  lat_span: Optional[float] = None,
                                  lon_span: Optional[float] = None,
                                  app_version: str = "1.0",
                                  version: int = 2,
                                  include_references: bool = True) -> Optional[Dict]:
        """
        Trouve les véhicules à proximité d'une localisation

        Args:
            lat: Latitude
            lon: Longitude
            radius: Rayon de recherche en mètres
            query: Filtre de recherche (ID, numéro ou type)
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/vehicles-for-location"

        params = {
            'lat': lat,
            'lon': lon,
            'radius': radius,
            'appVersion': app_version,
            'version': version,
            'includeReferences': str(include_references).lower()
        }

        if query:
            params['query'] = query
        if lat_span:
            params['latSpan'] = lat_span
        if lon_span:
            params['lonSpan'] = lon_span

        return self._make_request(endpoint, params)

    def get_vehicle_for_trip(self,
                             trip_ids: List[str],
                             app_version: str = "1.0",
                             version: int = 2,
                             include_references: bool = True) -> Optional[Dict]:
        """
        Récupère les véhicules pour des trajets spécifiques

        Args:
            trip_ids: Liste des IDs de trajets
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/vehicle-for-trip"

        params = {
            'tripId': ','.join(trip_ids),
            'appVersion': app_version,
            'version': version,
            'includeReferences': str(include_references).lower()
        }

        return self._make_request(endpoint, params)

    # ===== SEARCH =====
    def search(self,
               query: str,
               app_version: str = "1.0",
               version: int = 2,
               include_references: bool = True) -> Optional[Dict]:
        """
        Recherche globale (arrêts, lignes, alertes)

        Args:
            query: Terme de recherche
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/search"

        params = {
            'query': query,
            'appVersion': app_version,
            'version': version,
            'includeReferences': str(include_references).lower()
        }

        return self._make_request(endpoint, params)

    # ===== BOOKING =====
    def get_booking_redirect(self,
                             route_id: str,
                             direction_id: str,
                             trip_id: str,
                             service_date: str,
                             board_stop_id: str,
                             alight_stop_id: str,
                             app_version: str = "1.0",
                             version: int = 2) -> Optional[Dict]:
        """
        Obtient l'URL de redirection pour la réservation

        Args:
            route_id: ID de la ligne
            direction_id: Direction (0 ou 1)
            trip_id: ID du trajet
            service_date: Date au format YYYYMMDD
            board_stop_id: ID de l'arrêt de montée
            alight_stop_id: ID de l'arrêt de descente
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/booking-redirect"

        params = {
            'routeId': route_id,
            'directionId': direction_id,
            'tripId': trip_id,
            'serviceDate': service_date,
            'boardStopId': board_stop_id,
            'alightStopId': alight_stop_id,
            'appVersion': app_version,
            'version': version
        }

        return self._make_request(endpoint, params)

    # ===== TICKETING =====
    def get_ticketing(self,
                      if_modified_since: Optional[int] = None,
                      app_version: str = "1.0",
                      version: int = 2,
                      include_references: bool = True) -> Optional[Dict]:
        """
        Récupère les informations de billetterie

        Args:
            if_modified_since: Timestamp en millisecondes
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/ticketing"

        params = {
            'appVersion': app_version,
            'version': version,
            'includeReferences': str(include_references).lower()
        }

        if if_modified_since:
            params['ifModifiedSince'] = if_modified_since

        return self._make_request(endpoint, params)

    # ===== STATISTICS =====
    def get_statistics(self,
                       app_version: str = "1.0",
                       version: int = 2) -> Optional[Dict]:
        """
        Récupère les statistiques du serveur (pour debug)
        """
        endpoint = f"{self.base_url}/{self.dialect}/api/where/statistics"

        params = {
            'appVersion': app_version,
            'version': version
        }

        return self._make_request(endpoint, params)


# examples.py
from config import BKK_API_KEY
import time

# Initialiser l'API
bkk = BKKApi(api_key=BKK_API_KEY)

# ===== EXEMPLE 1: Rechercher des alertes =====
print("=== ALERTES ===")
alerts = bkk.search_alerts(
    query="metro",
    min_result=5
)
if alerts and alerts.get('data'):
    print(f"Nombre d'alertes trouvées: {len(alerts['data'].get('list', []))}")

# ===== EXEMPLE 2: Trouver des arrêts proches =====
print("\n=== ARRÊTS PROCHES ===")
stops = bkk.get_stops_for_location(
    lat=47.5000,
    lon=19.0833,
    radius=500
)
if stops and stops.get('data'):
    stop_list = stops['data'].get('list', [])
    print(f"Nombre d'arrêts trouvés: {len(stop_list)}")
    if stop_list:
        print(f"Premier arrêt: {stop_list[0].get('name')}")

# ===== EXEMPLE 3: Horaires d'un arrêt =====
print("\n=== HORAIRES D'UN ARRÊT ===")
# Utilisez un vrai stop_id de votre recherche précédente
departures = bkk.get_arrivals_and_departures(
    stop_id="BKK_F01029",
    minutes_after=60
)
if departures and departures.get('data'):
    entry = departures['data'].get('entry', {})
    stop_times = entry.get('stopTimes', [])
    print(f"Nombre de départs: {len(stop_times)}")

# ===== EXEMPLE 4: Planifier un itinéraire (SANS BICYCLE) =====
print("\n=== PLANIFICATION D'ITINÉRAIRE (TRANSPORT + MARCHE) ===")
trip = bkk.plan_trip(
    from_place="Départ::47.5000,19.0833",
    to_place="Arrivée::47.5058,19.0375",
    mode="TRANSIT,WALK"
)
if trip and trip.get('data'):
    plan = trip['data'].get('entry', {}).get('plan', {})
    itineraries = plan.get('itineraries', [])
    print(f"Nombre d'itinéraires trouvés: {len(itineraries)}")
    if itineraries:
        first_itinerary = itineraries[0]
        print(f"Durée: {first_itinerary.get('duration', 0) / 60:.1f} minutes")
        print(f"Nombre de correspondances: {first_itinerary.get('transfers', 0)}")

# ===== EXEMPLE 5: Planifier avec vélo =====
print("\n=== PLANIFICATION AVEC VÉLO ===")
bike_trip = bkk.plan_trip(
    from_place="Départ::47.5000,19.0833",
    to_place="Arrivée::47.5058,19.0375",
    mode="BICYCLE,TRANSIT,WALK",
    optimize="QUICK"  # ou "SAFE", "FLAT"
)
if bike_trip and bike_trip.get('data'):
    plan = bike_trip['data'].get('entry', {}).get('plan', {})
    print(f"Statut: {bike_trip.get('status')}")
else:
    print(f"Erreur: {bike_trip}")

# ===== EXEMPLE 6: Détails d'une ligne =====
print("\n=== DÉTAILS D'UNE LIGNE ===")
route = bkk.get_route_details(route_id="BKK_0650")
if route and route.get('data'):
    entry = route['data'].get('entry', {})
    print(f"Nom de la ligne: {entry.get('shortName')} - {entry.get('longName')}")

# ===== EXEMPLE 7: Véhicules à proximité =====
print("\n=== VÉHICULES PROCHES ===")
vehicles = bkk.get_vehicles_for_location(
    lat=47.5000,
    lon=19.0833,
    radius=1000
)
if vehicles and vehicles.get('data'):
    vehicle_list = vehicles['data'].get('list', [])
    print(f"Nombre de véhicules: {len(vehicle_list)}")

# ===== EXEMPLE 8: Recherche globale =====
print("\n=== RECHERCHE GLOBALE ===")
search_result = bkk.search(query="Deák")
if search_result and search_result.get('data'):
    entry = search_result['data'].get('entry', {})
    print(f"Arrêts trouvés: {len(entry.get('stopIds', []))}")
    print(f"Lignes trouvées: {len(entry.get('routeIds', []))}")

# ===== EXEMPLE 9: Statistiques du serveur =====
print("\n=== STATISTIQUES ===")
stats = bkk.get_statistics()
if stats and stats.get('data'):
    entry = stats['data'].get('entry', {})
    print(f"Version serveur: {entry.get('serverInfo')}")
    print(f"Données valides du: {entry.get('validityStart')} au {entry.get('validityEnd')}")

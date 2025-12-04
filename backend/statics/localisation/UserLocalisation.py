import geocoder


def get_location():
    """
    Get the current user location based on IP address.
    Returns a dictionary with latitude, longitude, city, and country.
    """
    g = geocoder.ip('me')
    return {
        'latitude': g.latlng[0] if g.latlng else None,
        'longitude': g.latlng[1] if g.latlng else None,
        'city': g.city,
        'country': g.country
    }


def get_my_coordinates():
    """
    Get the current user coordinates (latitude, longitude) as a tuple.
    """
    location = get_location()
    return (location["latitude"], location["longitude"])

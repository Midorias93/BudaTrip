import requests
import folium
import webbrowser
import os
import Location

print(Location.get_location())

data = Location.budy_location()

print(data["data"]["list"][0])
latitude_bubi = data["data"]["list"][1]['lat']
longitude_bubi = data["data"]["list"][1]['lon']

latitude = Location.get_location()["latitude"]
longitude = Location.get_location()["longitude"]

m = folium.Map(location=[latitude, longitude], zoom_start=16, tiles='OpenStreetMap')

folium.Marker(
    [latitude, longitude],
    popup="Point central",
    tooltip="48.9356, 2.3539"
).add_to(m)

"""folium.Circle(
    radius=300,
    location=[latitude, longitude],
    color="blue",
    fill=True,
    fill_opacity=0.2
).add_to(m)"""

if not os.path.exists("maps"):
    os.makedirs("maps")
    m.save("maps/quartier.html")
else:
    m.save("maps/quartier.html")

webbrowser.open('file://' + os.path.realpath("maps/quartier.html"))


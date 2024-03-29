import airsim
import math

def distance_between_gps_points(gps1, gps2, alt = True):
    # Constants for scaling lat/lon differences to meters
    lat_scale = 111319.488  # meters per degree latitude (approximation)
    lon_scale = 111319.488 * math.cos(math.radians((gps1[0] + gps2[0]) / 2))  # average latitude for scaling longitude

    # Calculate differences
    dLat = (gps2[0] - gps1[0]) * lat_scale
    dLon = (gps2[1] - gps1[1]) * lon_scale
    dAlt = gps2[2] - gps1[2]

    # Euclidean distance
    if alt:
        distance = math.sqrt(dLat**2 + dLon**2 + dAlt**2)
    else:
        distance = math.sqrt(dLat**2 + dLon**2)
    #print(drone_name, distance)
    return distance

def create_geo_point(lat, lon, alt):
    geo_point = airsim.GeoPoint()
    geo_point.latitude = lat
    geo_point.longitude = lon
    geo_point.altitude = alt
    return geo_point

# Function to read GPS data based on point name
def getNedDataByName(point_name, filename="NED_data.txt"):
    with open(filename, "r") as file:
        for line in file:
            if line.startswith(point_name + ":"):
                _, coords = line.strip().split(": ")
                x, y, z = map(float, coords.split(","))
                return x, y, z
    print(f"No NED data found for point '{point_name}'")
    return None, None, None


def getgpsDataByName(point_name, filename="gps_data.txt"):
    with open(filename, "r") as file:
        for line in file:
            if line.startswith(point_name + ":"):
                _, coords = line.strip().split(": ")
                latitude, longitude, altitude = map(float, coords.split(", "))
                return [latitude, longitude, altitude]
    print(f"No GPS data found for point '{point_name}'")
    return None, None, None
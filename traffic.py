import requests

def get_live_travel_time(start_coords, end_coords):
    """
    Fetches dynamic travel time from the OSRM API between two coordinates.
    
    :param start_coords: Tuple (lat, lon) for the start location.
    :param end_coords: Tuple (lat, lon) for the destination location.
    :return: Estimated travel time in minutes or None if the API call fails.
    """
    # OSRM API endpoint expects coordinates in lon,lat order.
    base_url = "http://router.project-osrm.org/route/v1/driving/{},{};{},{}?overview=false"
    url = base_url.format(start_coords[1], start_coords[0], end_coords[1], end_coords[0])
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Check that we got a valid response
            if data.get("code") == "Ok" and data.get("routes"):
                duration_seconds = data["routes"][0]["duration"]
                # Convert seconds to minutes and return
                return duration_seconds / 60.0
        else:
            print("OSRM API request failed with status code:", response.status_code)
    except Exception as e:
        print("Error fetching OSRM data:", e)
    return None

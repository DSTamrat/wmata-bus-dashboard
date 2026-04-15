import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


np.random.seed(42)


# ---------------------------------------------------------
# REALISTIC DC ROUTE SHAPES (Simplified Polylines)
# ---------------------------------------------------------
ROUTE_SHAPES = {
    "S2": [
        (38.9935, -77.0310),  # Silver Spring
        (38.9800, -77.0320),
        (38.9650, -77.0340),
        (38.9500, -77.0360),
        (38.9350, -77.0380),
        (38.9200, -77.0400),  # Columbia Heights
        (38.9100, -77.0360),
        (38.9000, -77.0330),  # McPherson Sq
    ],
    "70": [
        (38.9935, -77.0230),  # Silver Spring
        (38.9800, -77.0235),
        (38.9650, -77.0238),
        (38.9500, -77.0240),
        (38.9350, -77.0235),
        (38.9200, -77.0220),  # Howard U
        (38.9050, -77.0210),
        (38.8950, -77.0200),  # Archives
    ],
    "X2": [
        (38.9000, -77.0330),  # Lafayette Sq
        (38.9000, -77.0200),
        (38.9000, -77.0100),
        (38.9000, -77.0000),
        (38.9000, -76.9900),
        (38.9000, -76.9800),
        (38.9000, -76.9700),
        (38.9000, -76.9600),  # Minnesota Ave
    ],
}


# ---------------------------------------------------------
# GENERATE STOPS ALONG EACH POLYLINE
# ---------------------------------------------------------
def interpolate_points(points, n_stops=20):
    """Generate evenly spaced stops along a polyline."""
    lat_list = []
    lon_list = []

    for i in range(len(points) - 1):
        lat1, lon1 = points[i]
        lat2, lon2 = points[i + 1]

        for t in np.linspace(0, 1, n_stops // (len(points) - 1)):
            lat_list.append(lat1 + (lat2 - lat1) * t)
            lon_list.append(lon1 + (lon2 - lon1) * t)

    return lat_list, lon_list


# ---------------------------------------------------------
# GENERATE TRIPS + STOP TIMES
# ---------------------------------------------------------
def generate_route_data(route_id, shape_points, trips_per_day=40):
    stops_lat, stops_lon = interpolate_points(shape_points, n_stops=20)

    records = []
    vehicle_positions = []

    for trip in range(trips_per_day):
        start_time = datetime(2024, 1, 1, 5, 0) + timedelta(minutes=trip * 15)

        for stop_idx in range(len(stops_lat)):
            sched_arr = start_time + timedelta(minutes=stop_idx * 2)

            delay = np.random.normal(1.5, 2.0)
            dwell = max(5, np.random.normal(15, 5))
            load = max(0, int(np.random.normal(20 + stop_idx * 2, 8)))

            actual_arr = sched_arr + timedelta(minutes=delay)

            records.append({
                "route_id": route_id,
                "trip_id": f"{route_id}_T{trip:03d}",
                "stop_sequence": stop_idx + 1,
                "scheduled_arrival": sched_arr,
                "actual_arrival": actual_arr,
                "delay_min": delay,
                "dwell_time_sec": dwell,
                "passenger_load": load,
                "latitude": stops_lat[stop_idx],
                "longitude": stops_lon[stop_idx],
            })

        # ---------------------------------------------------------
        # GENERATE VEHICLE POSITIONS FOR ANIMATION
        # ---------------------------------------------------------
        for t in range(0, len(stops_lat) * 120, 20):  # every 20 seconds
            progress = t / (len(stops_lat) * 120)
            progress = min(progress, 1)

            lat = stops_lat[0] + (stops_lat[-1] - stops_lat[0]) * progress
            lon = stops_lon[0] + (stops_lon[-1] - stops_lon[0]) * progress

            vehicle_positions.append({
                "route_id": route_id,
                "trip_id": f"{route_id}_T{trip:03d}",
                "timestamp": start_time + timedelta(seconds=t),
                "latitude": lat,
                "longitude": lon,
                "progress": progress,
            })

    return records, vehicle_positions


# ---------------------------------------------------------
# MAIN GENERATOR
# ---------------------------------------------------------
def main():
    all_stops = []
    all_positions = []

    for route_id, shape in ROUTE_SHAPES.items():
        stops, positions = generate_route_data(route_id, shape)
        all_stops.extend(stops)
        all_positions.extend(positions)

    df_stops = pd.DataFrame(all_stops)
    df_positions = pd.DataFrame(all_positions)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    df_stops.to_csv(os.path.join(root, "data", "bus_stops.csv"), index=False)
    df_positions.to_csv(os.path.join(root, "data", "vehicle_positions.csv"), index=False)

    print("Generated:")
    print(" - data/bus_stops.csv")
    print(" - data/vehicle_positions.csv")


if __name__ == "__main__":
    main()

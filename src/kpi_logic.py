import pandas as pd
import numpy as np

def compute_service_kpis(df):
    """
    Compute route-level KPIs using the new realistic DC dataset.
    """

    # Ensure datetime
    df["scheduled_arrival"] = pd.to_datetime(df["scheduled_arrival"])
    df["actual_arrival"] = pd.to_datetime(df["actual_arrival"])

    # Compute headway (minutes between scheduled arrivals)
    df = df.sort_values(["route_id", "trip_id", "stop_sequence"])
    df["scheduled_headway"] = (
        df.groupby(["route_id", "stop_sequence"])["scheduled_arrival"]
        .diff()
        .dt.total_seconds()
        .div(60)
    )

    # OTP: On-time if delay <= 5 minutes
    df["on_time"] = df["delay_min"].abs() <= 5

    # Load factor (scaled passenger load)
    df["load_factor"] = df["passenger_load"] / df["passenger_load"].max()

    # Route-level aggregation
    route_kpis = df.groupby("route_id").agg(
        avg_delay_min=("delay_min", "mean"),
        otp=("on_time", "mean"),
        avg_load_factor=("load_factor", "mean"),
        peak_load_factor=("load_factor", "max"),
        trips=("trip_id", "nunique"),
        stops=("stop_sequence", "nunique"),
    ).reset_index()

    # Reliability score (lower delay + higher OTP)
    route_kpis["reliability_score"] = (
        (1 - (route_kpis["avg_delay_min"] / route_kpis["avg_delay_min"].max())) * 0.5
        + (route_kpis["otp"]) * 0.5
    )

    # Crowding score (higher load = worse)
    route_kpis["crowding_score"] = (
        route_kpis["avg_load_factor"] * 0.7
        + route_kpis["peak_load_factor"] * 0.3
    )

    # Final route score (lower is better)
    route_kpis["route_score"] = (
        route_kpis["reliability_score"] * 0.6
        + (1 - route_kpis["crowding_score"]) * 0.4
    )

    # Recommendations
    def make_recommendation(row):
        if row["avg_delay_min"] > 8:
            return "High delays — consider adding recovery time or adjusting schedule."
        if row["peak_load_factor"] > 0.85:
            return "Overcrowding — consider increasing frequency."
        if row["otp"] < 0.75:
            return "Low OTP — investigate bunching or traffic hotspots."
        return "Route performing within acceptable range."

    route_kpis["recommendation"] = route_kpis.apply(make_recommendation, axis=1)

    return route_kpis

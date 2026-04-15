import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from kpi_logic import compute_service_kpis


# =========================================================
# DATA LOADERS
# =========================================================
@st.cache_data
def load_stops():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "data", "bus_stops.csv")
    df = pd.read_csv(path)

    df["scheduled_arrival"] = pd.to_datetime(df["scheduled_arrival"])
    df["actual_arrival"] = pd.to_datetime(df["actual_arrival"])

    df["time_bucket"] = pd.cut(
        df["scheduled_arrival"].dt.hour,
        bins=[0, 6, 10, 16, 20, 24],
        labels=["Night", "AM Peak", "Midday", "PM Peak", "Evening"],
        right=False,
        include_lowest=True,
    )

    return df


@st.cache_data
def load_positions():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "data", "vehicle_positions.csv")
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


@st.cache_data
def load_colors():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "assets", "wmata_colors.json")
    with open(path, "r") as f:
        return json.load(f)


# =========================================================
# WMATA CSS THEME + CENTERING + BLURRED HEADER IMAGE
# =========================================================
def inject_css(colors):
    st.markdown(
        f"""
        <style>

        /* Center the entire dashboard content */
        .main .block-container {{
            max-width: 1100px;
            margin-left: auto;
            margin-right: auto;
        }}

        /* Hide Streamlit default header/footer */
        .stApp > header, .stApp > footer {{
            visibility: hidden;
        }}

        .stApp {{
            background: linear-gradient(135deg, {colors['primary_blue']} 0%, #0A3D62 40%, #0C2E4E 100%);
            color: white !important;
        }}

        section[data-testid="stSidebar"] {{
            background-color: {colors['dark_gray']} !important;
            border-right: 2px solid {colors['secondary_gold']};
        }}

        /* WMATA header with blurred background image and glass strip */
        .wmata-header {{
            position: relative;
            padding: 18px 28px;
            border-left: 6px solid {colors['secondary_gold']};
            border-bottom: 2px solid {colors['secondary_gold']};
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.35);
            overflow: hidden;
        }}

        .wmata-header::before {{
            content: "";
            position: absolute;
            inset: 0;
            background-image: url('https://copilot.microsoft.com/th/id/BCO.45e200bf-bf2c-499d-818e-cacdec9a251a.png');
            background-size: cover;
            background-position: center;
            filter: blur(10px) brightness(0.55);
            transform: scale(1.05);
            z-index: 0;
        }}

        .wmata-header-inner {{
            position: relative;
            z-index: 1;
            background: rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(6px);
            border-radius: 10px;
            padding: 10px 20px;
            text-align: center;
        }}

        .wmata-header-inner h1 {{
            color: white;
            font-size: 30px;
            margin: 0;
            font-weight: 700;
        }}

        .glass-card {{
            background: rgba(255,255,255,0.12);
            padding: 20px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            margin-bottom: 20px;
        }}

        div[data-testid="metric-container"] {{
            background: rgba(255,255,255,0.15);
            padding: 12px;
            border-radius: 10px;
            backdrop-filter: blur(6px);
        }}

        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(255,255,255,0.1);
            border-radius: 10px;
        }}

        .stTabs [data-baseweb="tab"] {{
            color: white !important;
            font-weight: 600;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# ROUTE SHAPES + ANIMATION ENGINE
# =========================================================
def load_route_shapes():
    return {
        "S2": [
            (38.9935, -77.0310),
            (38.9800, -77.0320),
            (38.9650, -77.0340),
            (38.9500, -77.0360),
            (38.9350, -77.0380),
            (38.9200, -77.0400),
            (38.9100, -77.0360),
            (38.9000, -77.0330),
        ],
        "70": [
            (38.9935, -77.0230),
            (38.9800, -77.0235),
            (38.9650, -77.0238),
            (38.9500, -77.0240),
            (38.9350, -77.0235),
            (38.9200, -77.0220),
            (38.9050, -77.0210),
            (38.8950, -77.0200),
        ],
        "X2": [
            (38.9000, -77.0330),
            (38.9000, -77.0200),
            (38.9000, -77.0100),
            (38.9000, -77.0000),
            (38.9000, -76.9900),
            (38.9000, -76.9800),
            (38.9000, -76.9700),
            (38.9000, -76.9600),
        ],
    }


def build_route_polyline_traces(route_shapes, colors, selected_route=None):
    traces = []
    for route_id, pts in route_shapes.items():
        lats = [p[0] for p in pts]
        lons = [p[1] for p in pts]

        color = colors["primary_blue"]
        width = 3

        if selected_route == route_id:
            color = colors["secondary_gold"]
            width = 5

        traces.append(
            go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode="lines",
                line=dict(width=width, color=color),
                name=f"{route_id} Route",
                hoverinfo="none",
            )
        )
    return traces


def build_animation_frames(df_positions, colors):
    frames = []
    timestamps = sorted(df_positions["timestamp"].unique())

    for ts in timestamps:
        df_t = df_positions[df_positions["timestamp"] == ts]

        frames.append(
            go.Frame(
                data=[
                    go.Scattermapbox(
                        lat=df_t["latitude"],
                        lon=df_t["longitude"],
                        mode="markers",
                        marker=dict(size=11, color=colors["secondary_gold"], opacity=0.9),
                        text=df_t["route_id"],
                        hovertemplate="<b>%{text}</b><br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>",
                    )
                ],
                name=str(ts),
            )
        )

    return frames, timestamps


def build_animation_figure(route_traces, frames, colors):
    fig = go.Figure()

    for t in route_traces:
        fig.add_trace(t)

    if frames:
        fig.add_trace(frames[0].data[0])

    fig.frames = frames

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=11,
            center=dict(lat=38.92, lon=-77.02),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        updatemenus=[
            {
                "type": "buttons",
                "showactive": False,
                "buttons": [
                    {
                        "label": "▶ Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": 120, "redraw": True},
                                "fromcurrent": True,
                                "transition": {"duration": 0},
                                "mode": "immediate",
                                "loop": True,
                            },
                        ],
                    }
                ],
            }
        ],
    )

    return fig


# =========================================================
# MAIN DASHBOARD
# =========================================================
def main():
    st.set_page_config(page_title="WMATA Bus Route Performance Dashboard", layout="wide")

    colors = load_colors()
    inject_css(colors)

    st.markdown(
        """
        <div class="wmata-header">
            <div class="wmata-header-inner">
                <h1>WMATA Bus Route Performance Dashboard</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_stops = load_stops()
    df_positions = load_positions()
    route_kpis = compute_service_kpis(df_stops)

    routes = sorted(df_stops["route_id"].unique())

    selected_routes = st.sidebar.multiselect("Select Routes", routes, default=routes)

    time_buckets = sorted(df_stops["time_bucket"].dropna().unique())
    selected_buckets = st.sidebar.multiselect("Time of Day", time_buckets, default=time_buckets)

    df_f = df_stops[
        (df_stops["route_id"].isin(selected_routes)) &
        (df_stops["time_bucket"].isin(selected_buckets))
    ]

    kpis_f = route_kpis[route_kpis["route_id"].isin(selected_routes)]

    # KPI ROW
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Delay (min)", f"{kpis_f['avg_delay_min'].mean():.1f}")
    col2.metric("OTP (%)", f"{kpis_f['otp'].mean() * 100:.1f}")
    col3.metric("Avg Load Factor", f"{kpis_f['avg_load_factor'].mean():.2f}")
    col4.metric("Avg Route Score", f"{kpis_f['route_score'].mean():.1f}")

    st.markdown("")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "System Overview",
            "Route Performance",
            "Stop Analysis",
            "Recommendations",
            "Map View",
            "Real‑Time Simulation",
        ]
    )

    # TAB 1 — SYSTEM OVERVIEW
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("System Overview")

        fig = px.scatter(
            kpis_f,
            x="avg_delay_min",
            y="avg_load_factor",
            size="trips",
            color="route_id",
            color_discrete_sequence=[
                colors["secondary_gold"],
                colors["primary_blue"],
                colors["danger_red"],
            ],
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # TAB 2 — ROUTE PERFORMANCE
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Route Performance Scorecard")

        st.dataframe(
            kpis_f[
                [
                    "route_id",
                    "avg_delay_min",
                    "otp",
                    "avg_load_factor",
                    "peak_load_factor",
                    "reliability_score",
                    "crowding_score",
                    "route_score",
                    "recommendation",
                ]
            ].sort_values("route_score", ascending=False),
            use_container_width=True,
        )

        st.markdown('</div>', unsafe_allow_html=True)

    # TAB 3 — STOP ANALYSIS
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Stop-Level Delay and Crowding")

        route_sel = st.selectbox("Select Route", routes)
        df_r = df_f[df_f["route_id"] == route_sel]

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**Delay by Stop Sequence**")
            fig3 = px.box(
                df_r,
                x="stop_sequence",
                y="delay_min",
                color_discrete_sequence=[colors["secondary_gold"]],
            )
            st.plotly_chart(fig3, use_container_width=True)

        with c2:
            st.markdown("**Passenger Load by Stop**")
            load_by_stop = (
                df_r.groupby("stop_sequence")["passenger_load"]
                .mean()
                .reset_index()
            )
            fig4 = px.line(
                load_by_stop,
                x="stop_sequence",
                y="passenger_load",
                color_discrete_sequence=[colors["primary_blue"]],
            )
            st.plotly_chart(fig4, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # TAB 4 — RECOMMENDATIONS
    with tab4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Route Recommendations")

        st.dataframe(
            kpis_f[
                [
                    "route_id",
                    "route_score",
                    "reliability_score",
                    "crowding_score",
                    "recommendation",
                ]
            ].sort_values("route_score"),
            use_container_width=True,
        )

        st.markdown('</div>', unsafe_allow_html=True)

    # TAB 5 — MAP VIEW
    with tab5:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("WMATA-Style Map View")

        stop_delay = (
            df_f.groupby(["route_id", "latitude", "longitude"])["delay_min"]
            .mean()
            .reset_index()
        )

        fig_map = px.scatter_mapbox(
            stop_delay,
            lat="latitude",
            lon="longitude",
            color="delay_min",
            color_continuous_scale=["#0072CE", "#FDB913", "#C8102E"],
            zoom=11,
            height=650,
            hover_name="route_id",
            hover_data={"delay_min": True},
        )

        fig_map.update_traces(
            cluster=dict(enabled=True),
            marker=dict(size=7),
        )

        fig_map.update_layout(
            mapbox_style="carto-positron",
            margin=dict(l=0, r=0, t=0, b=0),
        )

        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # TAB 6 — REAL‑TIME SIMULATION
    with tab6:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Real‑Time Bus Simulation (Auto‑Play)")

        sim_route = st.selectbox("Select Route for Simulation", routes)

        df_pos_r = df_positions[df_positions["route_id"] == sim_route]

        if df_pos_r.empty:
            st.warning("No vehicle position data for this route.")
        else:
            route_shapes = load_route_shapes()
            route_traces = build_route_polyline_traces(route_shapes, colors, selected_route=sim_route)
            frames, timestamps = build_animation_frames(df_pos_r, colors)
            fig_sim = build_animation_figure(route_traces, frames, colors)
            st.plotly_chart(fig_sim, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

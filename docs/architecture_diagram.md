flowchart TD

    %% Data Sources
    subgraph Data Sources
        S1[Route Definitions]
        S2[Stop Locations]
        S3[Vehicle Position Logs]
    end

    %% Data Generation
    subgraph Synthetic Data Engine
        G1[Schedule Generator]
        G2[Delay Model]
        G3[Passenger Load Model]
    end

    S1 --> G1
    S2 --> G1
    G1 --> G2
    G2 --> G3

    G3 --> R1[Raw Data Files<br/>bus_stops.csv<br/>vehicle_positions.csv]

    %% Processing
    subgraph Processing & Analytics
        P1[ETL Pipeline]
        P2[KPI Computation<br/>Delay, OTP, Load Factor]
        P3[Route Score Engine]
        P4[Simulation Frame Builder]
    end

    R1 --> P1
    P1 --> P2
    P2 --> P3
    P3 --> P4

    %% Dashboard
    subgraph Streamlit Dashboard
        D1[System Overview]
        D2[Route Performance]
        D3[Stop Analysis]
        D4[Map View]
        D5[Real‑Time Simulation]
    end

    P2 --> D1
    P3 --> D2
    P2 --> D3
    P2 --> D4
    P4 --> D5

    %% Assets
    subgraph Assets
        A1[WMATA Colors JSON]
        A2[WMATA Header Image]
        A3[WMATA Hero Banner]
    end

    Assets --> Streamlit Dashboard

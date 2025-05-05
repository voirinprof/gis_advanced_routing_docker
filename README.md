# Optimized Routing with Multiple Vehicles and Leaflet

This repository contains a web application using Flask, Nginx, and SQLite to manage waypoints (clients) with delivery demands, calculate optimized routes for multiple delivery vehicles with capacity constraints, using NetworkX, OSMnx, and OR-Tools. The results are displayed on a Leaflet map.

## Prerequisites
- Docker
- Docker Compose

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/voirinprof/gis_advanced_routing_docker.git
   cd gis_advanced_routing_docker
   ```
2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
3. Access the application at `http://localhost`.

## Usage
- Click on the map to add waypoints (clients), specifying a delivery demand via the "Delivery Demand" field.
- Configure the number of vehicles and their capacity in the respective fields.
- Click "Optimize Route" to calculate and display the optimized routes for each vehicle.
- Routes are displayed on the map with different colors for each vehicle.

## Structure
- `app/` : Contains the Flask application, HTML templates, and static files (CSS, JS).
- `nginx/` : Nginx configuration to serve the application.
- `docker-compose.yml` : Service orchestration.

## Features
- Add waypoints with specific delivery demands.
- Calculate optimized routes for multiple vehicles with capacity constraints.
- Display routes on a Leaflet map with distinct colors for each vehicle.

## OR-Tools and Approach

### Overview of OR-Tools
OR-Tools is an open-source software suite by Google for combinatorial optimization, particularly suited for solving complex routing problems like the Vehicle Routing Problem (VRP). In this project, OR-Tools is used to compute optimized routes for multiple delivery vehicles, considering capacity constraints and delivery demands at each client location.

### Approach to Solving the VRP
The application implements a Capacitated Vehicle Routing Problem (CVRP) with the following approach:

1. **Problem Definition**:
   - **Waypoints**: Each waypoint represents a client with a specific delivery demand (except the first waypoint, which is the depot with zero demand).
   - **Vehicles**: Multiple vehicles are available, each with a defined capacity limit.
   - **Objective**: Minimize the total distance traveled by all vehicles while ensuring each client's demand is met without exceeding vehicle capacities.

2. **Data Preparation**:
   - **Graph Creation**: OSMnx retrieves a road network graph centered around the depot, providing real-world road distances.
   - **Distance Matrix**: NetworkX computes shortest path lengths between waypoints to create a distance matrix.
   - **Demands**: Delivery demands are stored in the SQLite database and retrieved for each waypoint.
   - **Depot**: The first waypoint is designated as the depot, where all vehicles start and end.

3. **OR-Tools Configuration**:
   - **Routing Model**: A routing model is created with the number of vehicles and a depot node.
   - **Distance Callback**: A callback function provides the distance between nodes based on the distance matrix.
   - **Capacity Dimension**: A dimension is added to track the cumulative load of each vehicle, with vehicle-specific capacity constraints.
   - **Search Parameters**: The solver uses the `PATH_CHEAPEST_ARC` first-solution strategy and `GUIDED_LOCAL_SEARCH` metaheuristic to find an optimized solution within a 30-second time limit.

4. **Solution Extraction**:
   - The solver returns a set of routes, one per vehicle, which are converted back to geographic coordinates (latitude, longitude) for display on the Leaflet map.
   - Routes are visualized with distinct colors to differentiate vehicles.

### Best Practices
- **Ensure Feasible Inputs**: The total demand of all clients should not exceed the combined capacity of all vehicles, or the solver may fail to find a solution.
- **Optimize Graph Size**: Limit the graph size (e.g., 5km radius) to balance accuracy and computation speed.
- **Tune Solver Parameters**: Adjust the time limit or metaheuristic strategy based on problem complexity for better solutions.
- **Validate Waypoints**: Ensure waypoints are within the road network area to avoid routing errors.

This approach leverages OR-Tools' robust optimization capabilities to provide practical and efficient delivery routes, integrated with real-world road data from OSMnx.
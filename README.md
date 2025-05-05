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
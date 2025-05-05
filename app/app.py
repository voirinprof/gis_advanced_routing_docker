from flask import Flask, render_template, request, jsonify
import osmnx as ox
import networkx as nx
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import sqlite3
import os

app = Flask(__name__)

# Chemin de la base de données
DB_PATH = '/root/db/waypoints.db'

# Connexion à SQLite
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS waypoints 
                 (id INTEGER PRIMARY KEY, lat REAL, lon REAL, demand INTEGER)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_waypoint', methods=['POST'])
def add_waypoint():
    data = request.json
    lat, lon, demand = data['lat'], data['lon'], data['demand']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO waypoints (lat, lon, demand) VALUES (?, ?, ?)", (lat, lon, demand))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/get_waypoints', methods=['GET'])
def get_waypoints():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT lat, lon, demand FROM waypoints")
    waypoints = [{"lat": row[0], "lon": row[1], "demand": row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(waypoints)

@app.route('/optimize_route', methods=['POST'])
def optimize_route():
    data = request.json
    num_vehicles = data.get('num_vehicles', 1)
    vehicle_capacity = data.get('vehicle_capacity', 100)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT lat, lon, demand FROM waypoints")
    waypoints = [(row[0], row[1], row[2]) for row in c.fetchall()]
    conn.close()

    if len(waypoints) < 2:
        return jsonify({"error": "At least 2 waypoints required"})

    # Le premier waypoint est le dépôt (demande = 0)
    demands = [0] + [wp[2] for wp in waypoints[1:]]
    waypoints = [(wp[0], wp[1]) for wp in waypoints]

    # Télécharger le graphe routier avec OSMnx
    G = ox.graph_from_point(waypoints[0], dist=5000, network_type='drive')
    nodes = list(G.nodes(data=True))

    # Trouver les nœuds les plus proches pour chaque waypoint
    waypoint_nodes = []
    for lat, lon in waypoints:
        node = ox.distance.nearest_nodes(G, lon, lat)
        waypoint_nodes.append(node)

    # Créer une matrice de distances
    distance_matrix = []
    for i in waypoint_nodes:
        row = []
        for j in waypoint_nodes:
            if i == j:
                row.append(0)
            else:
                try:
                    length = nx.shortest_path_length(G, i, j, weight='length')
                    row.append(int(length))
                except:
                    row.append(999999)  # Distance infinie si pas de chemin
        distance_matrix.append(row)

    # Configurer OR-Tools pour le VRP avec capacités
    manager = pywrapcp.RoutingIndexManager(len(waypoint_nodes), num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    # Callback pour les distances
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Callback pour les demandes
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # Pas de slack
        [vehicle_capacity] * num_vehicles,  # Capacité des véhicules
        True,  # Commencer à zéro
        "Capacity"
    )

    # Paramètres de recherche
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 30

    # Résoudre le problème
    solution = routing.SolveWithParameters(search_parameters)
    if not solution:
        return jsonify({"error": "No solution found"})

    # Construire les itinéraires par véhicule
    routes = []
    for vehicle_id in range(num_vehicles):
        route = []
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route.append(waypoint_nodes[node_index])
            index = solution.Value(routing.NextVar(index))
        if len(route) > 1:  # Inclure uniquement les routes non vides
            routes.append(route)

    # Convertir les nœuds en coordonnées
    optimized_routes = []
    for route in routes:
        route_coords = []
        for node in route:
            node_data = nodes[[n[0] for n in nodes].index(node)][1]
            route_coords.append({"lat": node_data['y'], "lon": node_data['x']})
        optimized_routes.append(route_coords)

    return jsonify({"routes": optimized_routes})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
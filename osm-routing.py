import osmnx as ox
import networkx as nx
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/route")
def get_route():
    # Define start and end lat/lon
    start_latlon = (51.448538, -0.355183)  # Example: London
    end_latlon = (51.445235, -0.325506)  # Example: Another London location

    # Compute bounding box
    north = max(start_latlon[0], end_latlon[0])  # Maximum latitude
    south = min(start_latlon[0], end_latlon[0])  # Minimum latitude
    east = max(start_latlon[1], end_latlon[1])   # Maximum longitude
    west = min(start_latlon[1], end_latlon[1])   # Minimum longitude

    bbox = [west, south, east, north]

    # # Get drivable roads
    G = ox.graph.graph_from_bbox(bbox, network_type="all_public", simplify=True)

    features = ox.features_from_bbox(bbox, { "leisure": "park" })

    print(features)

    # Find the nearest nodes
    orig = ox.distance.nearest_nodes(G, start_latlon[1], start_latlon[0])
    dest = ox.distance.nearest_nodes(G, end_latlon[1], end_latlon[0])

    # # Find the shortest path
    # weight : None, string or function, optional (default = None)
    # If None, every edge has weight/distance/cost 1.
    # If a string, use this edge attribute as the edge weight.
    # Any edge attribute not present defaults to 1.
    # If this is a function, the weight of an edge is the value
    # returned by the function. The function must accept exactly
    # three positional arguments: the two endpoints of an edge and
    # the dictionary of edge attributes for that edge.
    # The function must return a number.
    route = ox.shortest_path(G, orig, dest, weight="length")

    # Convert node IDs to coordinates
    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]

    # Convert tuples to nested lists
    route_coords_list = [[lat, lon] for lat, lon in route_coords]

    return { "route": route_coords_list }
import osmnx as ox
import networkx as nx
from fastapi import FastAPI
from pydantic import BaseModel, Json
from shapely.strtree import STRtree

app = FastAPI()

class GeoDirection(BaseModel):
    orig: tuple[float, float]
    dest: tuple[float, float]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/route")
def get_route(route: GeoDirection):
    # Define start and end lat/lon
    start_latlon = route.orig
    end_latlon = route.dest

    padding = 0.02

    north = max(start_latlon[0], end_latlon[0]) + padding  # Maximum latitude
    south = min(start_latlon[0], end_latlon[0]) - padding  # Minimum latitude
    east = max(start_latlon[1], end_latlon[1]) + padding  # Maximum longitude
    west = min(start_latlon[1], end_latlon[1]) - padding   # Minimum longitude

    bbox = [west, south, east, north]

    # # Get drivable roads
    G = ox.graph.graph_from_bbox(bbox, network_type="all")

    # Find the nearest nodes
    orig = ox.distance.nearest_nodes(G, start_latlon[1], start_latlon[0])
    dest = ox.distance.nearest_nodes(G, end_latlon[1], end_latlon[0])

    def make_custom_weight_func(park_gdf):
        parks = list(park_gdf.geometry)
        park_tree = STRtree(parks)

        def custom_weight(u, v, data):
            weights = []

            for edge in data.values():
                w = edge.get("length", 1.0)
                geom = edge.get("geometry")

                if geom is not None:
                    centroid = geom.centroid
                    nearby_parks = park_tree.query(centroid) if centroid is not None else []

                    for park in nearby_parks:
                        w *= 0.3  # reward park segment
                        break

                weights.append(w)

            return min(weights) if weights else 1.0

        return custom_weight


    parks_tag_dict = {
        'leisure': ['park', 'garden', 'common', 'recreation_ground', 'nature_reserve'],
        'landuse': ['forest', 'grass', 'meadow', 'recreation_ground', 'village_green'],
        'natural': ['wood', 'heath', 'scrub', 'grassland', 'wetland', 'water'],
        'boundary': ['national_park']
    }

    gdf_parks = ox.features_from_bbox(bbox, tags=parks_tag_dict)

    custom_weight = make_custom_weight_func(gdf_parks)

    route = ox.shortest_path(G, orig, dest, weight=custom_weight)

    # Convert node IDs to coordinates
    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]

    # Convert tuples to nested lists
    route_coords_list = [[lat, lon] for lat, lon in route_coords]

    return { "route": route_coords_list }
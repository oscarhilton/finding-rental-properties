import osmnx as ox
import matplotlib.pyplot as plt
from shapely.strtree import STRtree

start_latlon = [51.450931,-0.357921]
end_latlon = [51.461013,-0.301767]

padding = 0.002

north = max(start_latlon[0], end_latlon[0]) + padding  # Maximum latitude
south = min(start_latlon[0], end_latlon[0]) - padding  # Minimum latitude
east = max(start_latlon[1], end_latlon[1]) + padding  # Maximum longitude
west = min(start_latlon[1], end_latlon[1]) - padding   # Minimum longitude

bbox_ = [west, south, east, north]

# Get walking network for an area in London
G = ox.graph_from_bbox(bbox_, network_type='all')

fig, ax = ox.plot_graph(G, show=False, close=False)

# Define origin and destination by coordinates
orig = ox.distance.nearest_nodes(G, start_latlon[1], start_latlon[0])  # near Primrose Hill
dest = ox.distance.nearest_nodes(G, end_latlon[1], end_latlon[0])  # near British Museum

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
    'natural': ['wood', 'heath', 'scrub', 'grassland', 'wetland'],
    'boundary': ['national_park']
}

gdf_parks = ox.features_from_bbox(bbox_, tags=parks_tag_dict)

custom_weight = make_custom_weight_func(gdf_parks)

# Get scenic path
route = ox.shortest_path(G, orig, dest, weight=custom_weight)

ox.plot_graph_route(G, route, ax=ax, route_color='red', route_linewidth=3, show=False, close=False)

# Plot a custom point (like origin/destination)

x, y = G.nodes[orig]['x'], G.nodes[orig]['y']
ax.scatter(x, y, c='green', s=100, label='Start')

x2, y2 = G.nodes[dest]['x'], G.nodes[dest]['y']
ax.scatter(x2, y2, c='blue', s=100, label='End')

gdf_parks.plot(ax=ax, color='green', alpha=0.4)

gdf_parks = ox.features_from_bbox(bbox_, tags={'natural':'water'})
gdf_parks.plot(ax=ax, color='blue', alpha=0.4)

plt.show()
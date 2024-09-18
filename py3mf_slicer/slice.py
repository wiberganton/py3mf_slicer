import lib3mf
import pyvista as pv
from get_items import get_pyvista_mesh
from ctypes import c_float, c_uint32
import numpy as np
import networkx as nx
import math

def to_lib3mf_position2D(positions):
    lib3mf_positions = []
    for row in positions:
        position = lib3mf.Position2D((c_float * 2)(row[0], row[1]))
        lib3mf_positions.append(position)
    return lib3mf_positions

def identify_pv_polygons(arr):
    from collections import defaultdict, deque
    # Create a graph from the array
    graph = defaultdict(list)
    for edge in arr:
        graph[edge[0]].append(edge[1])
        graph[edge[1]].append(edge[0])
    def bfs(start, visited):
        queue = deque([start])
        circle = []
        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                circle.append(node)
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        queue.append(neighbor)
        circle.append(start)  # Add the start node at the end to complete the circle
        return circle
    visited = set()
    circles = []
    for node in graph:
        if node not in visited:
            circle = bfs(node, visited)
            if len(circle) > 2:  # Ensure it's a circle
                circles.append(circle)
    return circles

def identify_pv_polygons2(connections):
    # Create a graph from the connections
    G = nx.Graph()
    G.add_edges_from(connections)
    
    # Find all connected components in the graph
    connected_components = list(nx.connected_components(G))
    
    sorted_entities = []
    
    for component in connected_components:
        # Create a subgraph for each component
        subgraph = G.subgraph(component)
        
        # Find a path that visits all nodes in the subgraph
        path = list(nx.dfs_preorder_nodes(subgraph))
        
        # Append the sorted path to the result
        sorted_entities.append(path)
    
    return sorted_entities
    
def slice_pv_mesh(mesh, layer_height):
    z_min, z_max = mesh.bounds[4], mesh.bounds[5]
    # Create a MultiBlock to store all slices
    slices = pv.MultiBlock()
    # Slice the mesh at each z-coordinate
    z_floor = math.floor(z_min/layer_height)*layer_height
    z_floor = max(z_floor, 0)
    z = z_floor+layer_height
    while z < z_max:
        slice = mesh.slice(normal=[0, 0, 1], origin=[0, 0, z])
        slices.append(slice)
        z = z + layer_height

    return slices

def slice_model(model, layer_height):
    model_sliced = model #copy.deepcopy(model)
    pv_meshes = get_pyvista_mesh(model_sliced)
    for mesh in pv_meshes:
        slices = slice_pv_mesh(mesh, layer_height)

        z_min = slices[0].points[0][2]
        z_max = slices[-1].points[0][2]

        slicestack = model_sliced.AddSliceStack(z_min-layer_height)
        for pv_slice in slices:
            slice = slicestack.AddSlice(pv_slice.points[0][2])
            vertices = pv_slice.points[:, :2]
            positions = to_lib3mf_position2D(vertices)
            slice.SetVertices(positions)
            pv_lines = pv_slice.lines.reshape(-1, 3)[:, 1:]
            #sorted_lines = identify_pv_polygons(pv_lines)
            sorted_lines = identify_pv_polygons2(pv_lines)

            for sorted_line in sorted_lines:
                sorted_line = np.array(sorted_line)
                lines = (c_uint32 * sorted_line.size)(*sorted_line.flatten())
                slice.AddPolygon(lines)
    return model_sliced


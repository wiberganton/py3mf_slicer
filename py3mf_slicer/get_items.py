
from __future__ import annotations

import lib3mf
import numpy as np
import pyvista as pv
from ctypes import c_float, c_uint32
import shapely
from typing import Iterable, List, Tuple, Optional, Callable, Union, Dict
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

def to_lib3mf_position2D(positions):
    lib3mf_positions = []
    for row in positions:
        position = lib3mf.Position2D((c_float * 2)(row[0], row[1]))
        lib3mf_positions.append(position)
    return lib3mf_positions

def get_vertexs(model):
    matrix = []
    mesh_iterator = model.GetMeshObjects()
    
    while mesh_iterator.MoveNext():
        vertex_matrix = []
        mesh_object = mesh_iterator.GetCurrentMeshObject()
        vertices = mesh_object.GetVertices()
        
        for vertex in vertices:
            coordinates = vertex.Coordinates
            vertex_matrix.append([coordinates[0], coordinates[1], coordinates[2]])
        matrix.append(vertex_matrix)
    return matrix

def get_bounding_boxes(model):
    matrices = get_vertexs(model)
    boundries = []
    for matrix in matrices:
        m = np.array(matrix)
        min_values = np.min(m, axis=0)
        max_values = np.max(m, axis=0)
        boundries.append([max_values.tolist(), min_values.tolist()])
    return boundries

def get_layer_height(model):
    slice_stack_iterator = model.GetSliceStacks()
    while slice_stack_iterator.MoveNext():
        slicestack = slice_stack_iterator.GetCurrentSliceStack()
        slice_count = slicestack.GetSliceCount()
        z_min = slicestack.GetSlice(0).GetZTop()
        z_max = slicestack.GetSlice(slice_count-1).GetZTop()
        if slice_count > 1:
            layer_height = (z_max-z_min)/(slice_count-1)
        else:
            layer_height = z_min
        return layer_height
    return 0

def get_layer_z_height(model, layer_nmb):
    slice_stack_iterator = model.GetSliceStacks()
    while slice_stack_iterator.MoveNext():
        slicestack = slice_stack_iterator.GetCurrentSliceStack()
        slice_count = slicestack.GetSliceCount()
        if layer_nmb < slice_count:
            z_height = slicestack.GetSlice(layer_nmb).GetZTop()
            return z_height
    return 0

def get_pyvista_meshes(model):
    pv_meshes = []
    mesh_iterator = model.GetMeshObjects()
    while mesh_iterator.MoveNext():
        mesh_object = mesh_iterator.GetCurrentMeshObject()
        # Extract vertices
        vertices = mesh_object.GetVertices()
        points = [(vertex.Coordinates[0], vertex.Coordinates[1], vertex.Coordinates[2]) for vertex in vertices]
        # Extract faces
        triangles = mesh_object.GetTriangleIndices()
        faces = []
        for triangle in triangles:
            faces.append([3, triangle.Indices[0], triangle.Indices[1], triangle.Indices[2]])
        # Create pyvista mesh
        pv_meshes.append(pv.PolyData(points, faces))
    return pv_meshes

def get_pyvista_slices(model):
    slice_stack_iterator = model.GetSliceStacks()
    slices = []
    while slice_stack_iterator.MoveNext():
        slicestack = slice_stack_iterator.GetCurrentSliceStack()
        multiblock = pv.MultiBlock()

        for i in range(slicestack.GetSliceCount()):
            slice = slicestack.GetSlice(i)
            vertices = []
            vertices_list = slice.GetVertices()
            z_top = slicestack.GetSlice(i).GetZTop()
            vertices = [[vertex.Coordinates[0], vertex.Coordinates[1], z_top] for vertex in vertices_list]
            
            polygons = []
            for k in range(slice.GetPolygonCount()):
                polygon = slice.GetPolygonIndices(k)
                newlst = []
                for i in range(len(polygon)-1):
                    newlst.append(2)
                    newlst.append(polygon[i])
                    newlst.append(polygon[i+1])
                newlst.append(2)
                newlst.append(polygon[-1])
                newlst.append(polygon[0])
                polydata = pv.PolyData(vertices, lines=np.array(newlst))
                multiblock.append(polydata)
            
        slices.append(multiblock)
    return slices

def get_py3mf_from_pyvista(pyvista_meshes):
    wrapper = lib3mf.get_wrapper()
    model = wrapper.CreateModel()

    for mesh in pyvista_meshes:
        mesh = mesh.triangulate()  # 🔹 Ensure all faces are triangles
        mesh_object = model.AddMeshObject()
        vertices = mesh.points
        faces = mesh.faces
        
        # Add vertices to the lib3mf mesh object
        for vertex in vertices:
            mesh_object.AddVertex(lib3mf.Position((c_float * 3)(vertex[0], vertex[1], vertex[2])))

        # Add triangles to the lib3mf mesh object
        i = 0
        while i < len(faces):
            n = faces[i]  # Number of vertices in the face
            if n == 3:  # Triangle (expected now that we triangulated)
                v1, v2, v3 = faces[i+1], faces[i+2], faces[i+3]
                if v1 != v2 and v2 != v3 and v1 != v3:  # Avoid degenerate triangles
                    mesh_object.AddTriangle(lib3mf.Triangle((c_uint32 * 3)(v1, v2, v3)))
            else:
                raise ValueError(f"Unexpected face with {n} vertices (should be 3 after triangulation)")
            i += n + 1  # Move to the next face
        
        # Apply identity transformation
        transform = lib3mf.Transform()
        transform.m_Fields = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 0.0]
        ]
        model.AddBuildItem(mesh_object, transform)

    return model

def get_slices(model):
    pv_model_slices = get_pyvista_slices(model)
    levels = []
    max_z = 0
    for pv_model in pv_model_slices:
        level =[]
        for slice in pv_model:
            level.append(slice.GetBounds()[4])
        np_level = np.array(level)
        levels.append(np_level)
        max_z = max(max_z, np.max(np_level))

    layer_height = get_layer_height(model)
    z = layer_height
    slices = []

    while z <= max_z:
        slice = []
        for i in range(len(pv_model_slices)):
            positions = np.where(levels[i] == z)[0]
            s = []
            for pos in positions:
                block = pv_model_slices[i][pos.item()] #[pos]
                s.append(block)
            slice.append(s)
        slices.append(slice)
        z += layer_height
    return slices
      
def get_shapely_slice(model, layer, *, eps=1e-6):
    """
    Build a per-slicestack shapely geometry (Polygon/MultiPolygon) at the given layer index.
    Returns a list aligned with slicestacks; entries are None when out of bounds.
    """

    def create_hierarchy(polygons):
        # Sort big -> small so outers come before inners
        polygons = [p for p in polygons if p.is_valid and p.area > 0.0]
        if not polygons:
            return None
        polygons.sort(key=lambda p: p.area, reverse=True)

        top_level = [polygons[0]]
        second_level = [[]]  # holes candidates per top poly

        for i in range(1, len(polygons)):
            p = polygons[i]
            added = False
            for ii, outer in enumerate(top_level):
                # Use 'covers' instead of 'contains' to tolerate touching boundaries
                if outer.buffer(eps).covers(p):
                    # only add as a hole if it isn't inside an existing hole
                    add_to_second_level = True
                    for hole_poly in second_level[ii]:
                        if hole_poly.buffer(eps).covers(p):
                            add_to_second_level = False
                            break
                    if add_to_second_level:
                        second_level[ii].append(p)
                        added = True
                        break
            if not added:
                top_level.append(p)
                second_level.append([])

        out = []
        for outer, holes in zip(top_level, second_level):
            if holes:
                interiors = [h.exterior for h in holes]
                out.append(Polygon(outer.exterior, interiors))
            else:
                out.append(outer)
        if len(out) == 1:
            return out[0]
        return MultiPolygon(out)

    # ---- geometry + layer bookkeeping ---------------------------------------
    # Bounding boxes: assumed [(min_xyz, max_xyz), ...]
    bounding_box = get_bounding_boxes(model)
    # z_bound[i] = (zmin, zmax)
    z_bound = np.array([(bb[0][2], bb[1][2]) for bb in bounding_box], dtype=float)

    # layer height & target absolute height of this layer
    layer_height = float(get_layer_height(model))
    if layer_height <= 0:
        raise ValueError("get_layer_height(model) must be > 0")
    height = layer * layer_height

    # Collect slicestacks safely
    slice_stack_iterator = model.GetSliceStacks()
    slicestacks = []
    while slice_stack_iterator.MoveNext():
        try:
            slicestacks.append(slice_stack_iterator.GetCurrentSliceStack())
        except Exception as e:
            print(f"Error accessing slice stack: {e}")

    shapely_slice = []

    for index, slicestack in enumerate(slicestacks):
        zmin, zmax = z_bound[index]
        # Normalize ordering (just in case)
        if zmin > zmax:
            zmin, zmax = zmax, zmin

        # Is this height within this stack's vertical extent?
        if (zmin - eps) <= height <= (zmax + eps):
            # Compute the integer layer index inside this stack
            raw = (height - zmin) / layer_height
            stack_layer = int(round(raw))

            # Clamp to valid slice index range
            try:
                slice_count = int(slicestack.GetSliceCount())
            except Exception:
                # If API doesn't provide it, we’ll try/except per access below
                slice_count = None

            if slice_count is not None:
                if stack_layer < 0 or stack_layer >= slice_count:
                    shapely_slice.append(None)
                    continue

            try:
                slc = slicestack.GetSlice(stack_layer)
            except Exception:
                shapely_slice.append(None)
                continue

            vertices_list = slc.GetVertices()
            if not vertices_list:
                shapely_slice.append(None)
                continue

            # Build numpy of (x, y); we’re slicing a horizontal plane
            np_vertices = np.array(
                [[v.Coordinates[0], v.Coordinates[1]] for v in vertices_list],
                dtype=float
            )

            # Construct polygons; filter degenerate rings
            polys = []
            poly_count = slc.GetPolygonCount()
            for k in range(poly_count):
                idx = slc.GetPolygonIndices(k)
                if idx is None or len(idx) < 3:
                    continue
                ring = np_vertices[np.asarray(idx, dtype=int)]
                # Remove consecutive duplicates
                if len(ring) >= 2 and np.allclose(ring[0], ring[-1]):
                    # Shapely doesn't require explicit closure; ok either way
                    pass
                # Skip degenerate polygons (zero area / tiny)
                poly = Polygon(ring)
                if not poly.is_valid or poly.area <= eps:
                    continue
                polys.append(poly)

            if not polys:
                shapely_slice.append(None)
                continue

            # If multiple polygons, build hierarchy (holes) if needed
            geom = polys[0] if len(polys) == 1 else create_hierarchy(polys)
            shapely_slice.append(geom)
        else:
            shapely_slice.append(None)

    return shapely_slice

def get_number_of_mesh_objects(model):
    mesh_iterator = model.GetMeshObjects()
    nmb_of_meshes = 0
    while mesh_iterator.MoveNext():
        nmb_of_meshes = nmb_of_meshes + 1
    return nmb_of_meshes

def get_number_of_slice_stacks(model):
    slice_stack_iterator = model.GetSliceStacks()
    nmb_of_slice_stacks = 0
    while slice_stack_iterator.MoveNext():
        nmb_of_slice_stacks = nmb_of_slice_stacks + 1
    return nmb_of_slice_stacks

def get_number_layers(model):
    number_of_slices = []
    slice_stack_iterator = model.GetSliceStacks()
    while slice_stack_iterator.MoveNext():
        slicestack = slice_stack_iterator.GetCurrentSliceStack()
        slice_count = slicestack.GetSliceCount()
        number_of_slices.append(slice_count)
    return number_of_slices
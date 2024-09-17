import lib3mf
import numpy as np
import pyvista as pv
from ctypes import c_float, c_uint32

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
            for j in range(slice.GetVertexCount()):
                vertex = slice.GetVertices()[j]
                vertices.append([vertex.Coordinates[0], vertex.Coordinates[1], slicestack.GetSlice(i).GetZTop()])
            vertices = np.array(vertices)
            
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
        mesh_object = model.AddMeshObject()
        vertices = mesh.points
        faces = mesh.faces
        # Add vertices to the lib3mf mesh object
        for vertex in vertices:
            mesh_object.AddVertex(lib3mf.Position((c_float * 3)(vertex[0], vertex[1], vertex[2])))
        # Add triangles to the lib3mf mesh object
        for i in range(0,len(faces),4):
            mesh_object.AddTriangle(lib3mf.Triangle((c_uint32 * 3)(faces[i+1], faces[i+2], faces[i+3])))
        transform = lib3mf.Transform()
        transform.m_Fields = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 0.0]
        ]
        model.AddBuildItem(mesh_object, transform)
    return model
from lib3mf import get_wrapper
import lib3mf
import os

def load_file(path):
    file_extension = os.path.splitext(path)[1].lower()
    if file_extension[1:] == 'stl' or file_extension[1:] == 'obj'or file_extension[1:] == '3mf':
        wrapper = get_wrapper()
        model = wrapper.CreateModel()
        reader = model.QueryReader(file_extension[1:])
        reader.ReadFromFile(path)
        return model
    else:
        print("Import file format not supported")
    return None

def load_files(paths):
    def add_mesh_objects(source_model, target_model):
        mesh_iterator = source_model.GetMeshObjects()
        while mesh_iterator.MoveNext():
            mesh_object = mesh_iterator.GetCurrentMeshObject()
            new_mesh_object = target_model.AddMeshObject()
            
            # Copy vertices and triangles
            vertices = mesh_object.GetVertices()
            triangles = mesh_object.GetTriangleIndices()
            new_mesh_object.SetGeometry(vertices, triangles)
            
            # Add the new mesh object to the build
            transform = lib3mf.Transform()
            transform.m_Fields = [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.0, 0.0, 0.0]
            ]
            target_model.AddBuildItem(new_mesh_object, transform)
            
    wrapper = lib3mf.get_wrapper()
    merged_model = wrapper.CreateModel()
    for path in paths:
        add_mesh_objects(load_file(path), merged_model)
    return merged_model
    

import py3mf_slicer.get_items as get_items

def transform_model(model, item, movement = (0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
    meshes = get_items.get_pyvista_meshes(model)
    mesh = meshes[item]
    transformed_mesh = mesh.translate([movement[0], movement[1], movement[2]])
    transformed_mesh = transformed_mesh.rotate_x(rotation[0]).rotate_y(rotation[1]).rotate_z(rotation[2])
    transformed_mesh = transformed_mesh.scale([scale[0], scale[1], scale[2]])

    meshes[item] = transformed_mesh
    import pyvista as pv
    plotter = pv.Plotter()
    for slice in meshes:
        plotter.add_mesh(slice, color='green')
    plotter.show()
    transformed_model = get_items.get_py3mf_from_pyvista(meshes)

    return transformed_model

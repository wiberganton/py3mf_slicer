import lib3mf

def write_file(model, path):
    writer = model.QueryWriter("3mf")
    writer.WriteToFile(path)
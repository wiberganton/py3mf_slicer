import py3mf_slicer
import py3mf_slicer.load
import py3mf_slicer.slice
import py3mf_slicer.get_items
import py3mf_slicer.visualize
geometry1 = r"tests\geometries\test_geometry1.stl"
geometry2 = r"tests\geometries\test_geometry2.stl"
geometry3 = r"tests\geometries\test_geometry3.stl"

model = py3mf_slicer.load.load_files([geometry1, geometry2, geometry3])
        
sliced_model = py3mf_slicer.slice.slice_model(model, 1)

import time
start_time = time.time()  # Record start time
slices1 = py3mf_slicer.get_items.get_shapely_slice(sliced_model, 0)
end_time = time.time()    # Record end time

execution_time = end_time - start_time
print(f"Execution time1: {execution_time:.4f} seconds")

start_time = time.time()  # Record start time
slices2 = py3mf_slicer.get_items.get_shapely_slice2(sliced_model, 0)
end_time = time.time()    # Record end time

execution_time = end_time - start_time
print(f"Execution time2: {execution_time:.4f} seconds")

print(slices2)
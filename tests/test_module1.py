import unittest
import py3mf_slicer
import py3mf_slicer.load
import py3mf_slicer.slice
import py3mf_slicer.get_items
import py3mf_slicer.visualize

class TestPy3MF(unittest.TestCase):

    def setUp(self):
        # Paths to the files used in the test
        self.geometry1 = r"tests\geometries\test_geometry1.stl"
        self.geometry2 = r"tests\geometries\test_geometry2.stl"
        self.geometry3 = r"tests\geometries\test_geometry3.stl"

    def test_load_and_slice_model(self):
        # Step 1: Load the model
        model = py3mf_slicer.load.load_files([self.geometry1, self.geometry2, self.geometry3])
        
        # Assert that the model is not None
        self.assertIsNotNone(model, "Model failed to load")
        
        # Step 2: Slice the model
        sliced_model = py3mf_slicer.slice.slice_model(model, 1)
        
        # Assert that slicing produced a valid object
        self.assertIsNotNone(sliced_model, "Slicing the model failed")
        
        # Step 3: Get slices
        slices = py3mf_slicer.get_items.get_slices(sliced_model)

        # Assert that slices were extracted
        self.assertGreater(len(slices), 0, "No slices were extracted from the model")

        # Step 4: Get shapely slices
        slices = py3mf_slicer.get_items.get_shapely_slice(sliced_model, 0)

        # Assert that slices were extracted
        self.assertGreater(len(slices), 0, "No shapely slices were extracted from the model")
        
        # Step 5: Test if correct number of slice stacks and mesh objects are returned
        number_of_mesh_objects = py3mf_slicer.get_items.get_number_of_mesh_objects(sliced_model)
        number_of_slice_stacks = py3mf_slicer.get_items.get_number_of_slice_stacks(sliced_model)
        self.assertEqual(number_of_mesh_objects, 3, "Not correct number of mesh objects")
        self.assertEqual(number_of_slice_stacks, 3, "Not correct number of slice stacks")

        # Vizulise slice
        #py3mf_slicer.visualize.visualize_layer(slices[5])


        
if __name__ == '__main__':
    unittest.main()
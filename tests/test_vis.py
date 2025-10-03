import unittest
import py3mf_slicer
import py3mf_slicer.load
import py3mf_slicer.slice
import py3mf_slicer.get_items
import py3mf_slicer.visualize

import pyvista as pv

class TestPy3MF(unittest.TestCase):

    def setUp(self):
        self.geometry1 = r"tests\geometries\overhang.stl"
        self.mesh1 = pv.read(self.geometry1)

    def test_load_and_slice_model(self):
        z_step = 0.05
        model = py3mf_slicer.get_items.get_py3mf_from_pyvista([self.mesh1])
        sliced_model = py3mf_slicer.slice.slice_model(model, z_step)
        py3mf_slicer.visualize.visualize_slices(sliced_model)
        
if __name__ == '__main__':
    unittest.main()
import unittest
import py3mf_slicer
import py3mf_slicer.load
import py3mf_slicer.slice
import py3mf_slicer.get_items
import py3mf_slicer.visualize

import pyvista as pv
from shapely.geometry.base import BaseGeometry
from shapely.geometry import Polygon, MultiPolygon
from typing import List
import matplotlib.pyplot as plt
import numpy as np


def plot_geometries(geoms: List[BaseGeometry], ax=None, facecolor="lightblue", edgecolor="black", alpha=0.5):
    """
    Plot a list of shapely geometries with matplotlib.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 7))
    else:
        fig = ax.figure

    for geom in geoms:
        if geom.is_empty:
            continue
        
        if isinstance(geom, (Polygon, MultiPolygon)):
            polys = [geom] if isinstance(geom, Polygon) else geom.geoms
            for poly in polys:
                # Exterior ring
                x, y = poly.exterior.xy
                ax.fill(x, y, facecolor=facecolor, edgecolor=edgecolor, alpha=alpha)
                
                # Holes (interiors)
                for interior in poly.interiors:
                    ix, iy = interior.xy
                    ax.fill(ix, iy, facecolor="white", edgecolor=edgecolor, alpha=1.0)
        else:
            # Fallback for LineString / Point / others
            x, y = geom.xy
            ax.plot(x, y, color=edgecolor)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.show()

import pyvista as pv
import numpy as np
from shapely.geometry import Polygon, MultiPolygon

def polygons_to_outline_polydata(polys, z):
    """Return a PolyData made of polyline edges at Z=z for a list of shapely polygons."""
    pts = []
    lines = []
    idx = 0

    def add_ring(coords):
        nonlocal idx
        if len(coords) < 2:
            return
        # ring is closed in shapely; we’ll add open line (viewer can render closed visually)
        for x, y in coords:
            pts.append((x, y, z))
        n = len(coords)
        # VTK polyline cell format: [n, id0, id1, ..., id(n-1)]
        lines.extend([n] + list(range(idx, idx + n)))
        idx += n

    for poly in polys:
        if isinstance(poly, MultiPolygon):
            for g in poly.geoms:
                add_ring(list(g.exterior.coords))
                for hole in g.interiors:
                    add_ring(list(hole.coords))
        else:  # Polygon
            add_ring(list(poly.exterior.coords))
            for hole in poly.interiors:
                add_ring(list(hole.coords))

    if not pts:
        return pv.PolyData()
    pts = np.asarray(pts, dtype=float)
    lines = np.asarray(lines, dtype=np.int64)
    return pv.PolyData(pts, lines=lines)

def plot_layers_outlines(layers):
    plotter = pv.Plotter()
    for i, (z, polys) in enumerate(layers):
        pd = polygons_to_outline_polydata(polys, z)
        if pd.n_points == 0:
            continue
        plotter.add_mesh(pd, color=None, line_width=2, render_lines_as_tubes=True)
    plotter.show()


class TestPy3MF(unittest.TestCase):

    def setUp(self):
        # Paths to the files used in the test
        #self.geometry1 = r"tests\geometries\overhang.stl"
        #self.geometry1 = r"C:\Users\antwi87\Documents\git\py3mf_slicer\tests\geometries\overhang.stl"
        self.geometry1 = r"tests\geometries\overhang.stl"
        self.mesh1 = pv.read(self.geometry1)
        #remeshed = remesh(self.mesh1, target = 0.1)
        #pv.plot([self.mesh1], show_edges=True)
        #pv.plot([remeshed], show_edges=True)
        #self.mesh1 = remeshed

    def test_load_and_slice_model(self):
        z_step = 0.1
        model = py3mf_slicer.get_items.get_py3mf_from_pyvista([self.mesh1])
        sliced_model = py3mf_slicer.slice.slice_model(model, z_step)
        pv_slices = py3mf_slicer.get_items.get_pyvista_slices(sliced_model)
        #print("pv slides ", pv_slices)
        #pv_slices[0].plot(show_edges=True)
        nmb_layers = py3mf_slicer.get_items.get_number_layers(sliced_model)[0]
        step = int(nmb_layers/1)
        #print(f"nmb_layers {nmb_layers}")
        #print(f"step {step}")
        slices = []
        for i in range(0,nmb_layers,1):
            slice = py3mf_slicer.get_items.get_shapely_slice(sliced_model, i)
            slices.append((z_step*i, slice))

        # layers = [(0.0, [poly1, poly2]), (0.5, [poly3]), (1.0, [poly4, poly5])]
        #plot_layers_outlines(slices)
        
if __name__ == '__main__':
    unittest.main()
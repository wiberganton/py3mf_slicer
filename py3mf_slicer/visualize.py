import pyvista as pv

import py3mf_slicer.get_items

def get_colors():
    colors = [
        'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown',
        'black', 'white', 'gray', 'cyan', 'magenta', 'lightblue', 'lightgreen',
        'lightgray', 'darkblue', 'darkgreen', 'darkgray', 'darkred', 'darkorange',
        'darkviolet', 'darkcyan', 'darkmagenta', 'skyblue', 'turquoise', 'lime',
        'olive', 'teal', 'navy', 'maroon', 'gold', 'khaki', 'orchid', 'plum',
        'salmon', 'sienna', 'indigo', 'chocolate', 'coral', 'crimson', 'lavender',
        'thistle', 'beige', 'hotpink', 'tan', 'forestgreen', 'seagreen',
        'royalblue', 'midnightblue', 'slateblue', 'deepskyblue', 'dodgerblue',
        'lightsalmon', 'lightcoral', 'peachpuff', 'palegreen', 'palevioletred',
        'springgreen', 'steelblue', 'tomato', 'wheat', 'azure', 'bisque',
        'blanchedalmond', 'cornflowerblue', 'gainsboro', 'honeydew', 'ivory',
        'lavenderblush', 'lemonchiffon', 'linen', 'mistyrose', 'oldlace',
        'papayawhip', 'peachpuff', 'seashell', 'snow', 'whitesmoke', 'aliceblue'
    ]
    return colors

## Excpects input on the form [[pv_PolyData, pv_PolyData], [pv_PolyData], [...]]
## will assign one color to each inner list
def visualize_layer(pv_layer):
    plotter = pv.Plotter()
    colors = get_colors()
    for i, polydata in enumerate(pv_layer):
        for polydatum in polydata:
            plotter.add_mesh(polydatum, color=colors[i], show_edges=True)
    plotter.show()



def visualize_slices(sliced_model, show_bounds=False):
    pv_elements = py3mf_slicer.get_items.get_pyvista_slices(sliced_model)

    mb = pv.MultiBlock()
    for m in pv_elements:
        if isinstance(m, pv.MultiBlock):
            # extend with its children
            for j in range(len(m)):
                b = m[j]
                if b is not None:
                    mb.append(b)
        else:
            mb.append(m)

    p = pv.Plotter()
    p.add_mesh(mb, multi_colors=True)  # distinct color per (sub)block
    if show_bounds:
        p.show_bounds(grid='front', location='outer', ticks='both', all_edges=True)
    p.enable_anti_aliasing()
    p.show()
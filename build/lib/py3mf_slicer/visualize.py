import pyvista as pv

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
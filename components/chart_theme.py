import holoviews as hv
from bokeh.themes import Theme

def apply_dark_theme():
    dark_json = {
        "attrs": {
            "Figure": {
                "background_fill_color": "#121212",
                "border_fill_color": "#121212",
                "outline_line_color": "#2A2A2A",
            },
            "Axis": {
                "major_label_text_color": "#E3EAF2",
                "axis_label_text_color": "#A0A7B4",
                "major_tick_line_color": "#A0A7B4",
                "minor_tick_line_color": "#6C7480",
                "axis_line_color": "#A0A7B4",
            },
            "Grid": {
                "grid_line_color": "#2A2A2A",
            },
            "Title": {
                "text_color": "#E3EAF2",
            },
            "Text": {
                "text_color": "#E3EAF2",
            },
            "Toolbar": {
                "logo": None,
                "autohide": False,
            },
        }
    }

    hv.renderer("bokeh").theme = Theme(json=dark_json)

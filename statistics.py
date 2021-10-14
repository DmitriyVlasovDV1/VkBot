# Bokeh
import random
from bokeh.models import (HoverTool, FactorRange, Plot, LinearAxis, Grid,
                          Range1d)
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh.resources import INLINE
from bokeh.io import curdoc

def initialize_plots():
    curdoc().theme = "dark_minimal"
    return

def create_line_plot(x_values, y_values, title='Title',
    x_label='x', y_label='y', graphic_lable='', line_width=3):

    plot = figure(title=title, x_axis_label=x_label, y_axis_label=y_label)
    plot.line(x_values, y_values, legend_label=graphic_lable, line_width=line_width, line_color="green")

    plot.background_fill_color = (34, 35, 36)
    plot.border_fill_color = (64, 65, 67)
    plot.outline_line_color = (196, 196, 196)
    plot.width_policy = "max"
    plot.height_policy = "max"

    return plot
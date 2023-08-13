from bokeh.io import show
from bokeh.plotting import gmap, output_file, save, figure, curdoc
from bokeh.models import GMapOptions, ColumnDataSource, HoverTool, ColorBar, Button
from bokeh.transform import linear_cmap
from bokeh.palettes import Plasma256 as palette, RdYlBu3
from bokeh.layouts import column
import pandas as pd
from dotenv import load_dotenv
import os
import urllib, json

load_dotenv()
GMAPS_API_KEY=os.environ['GMAPS_API_KEY']


def load_data():
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data

# create a plot and style its properties
def get_data():
    data = load_data()
    df = pd.DataFrame.from_records(data)
    df["radius"] = df["sbi"]*3.
    df["usage"] = df["bemp"]/df["tot"]
    return df

df = get_data()

def plot(lat, lng, zoom=13, map_type='roadmap'):
    gmap_options = GMapOptions(lat=lat, lng=lng, 
                               map_type=map_type, zoom=zoom,
                               scale_control=True)
    # the tools are defined below: 
    hover = HoverTool(
        tooltips = [
            # @price refers to the price column
            # in the ColumnDataSource. 
            ('parking spaces', '@tot'),
            ('available bikes', '@sbi'), 
        ]
    )
    p = gmap(GMAPS_API_KEY, gmap_options, title=f'Taipei YouBike2.0 Stations Updated: {df.iloc[0]["srcUpdateTime"]}', 
             width=1000, height=800, 
            tools=[hover, 'reset', 'wheel_zoom', 'pan'])
    source = ColumnDataSource(df)
    mapper = linear_cmap('usage', palette, 0., 1.)   
    color_bar = ColorBar(color_mapper=mapper['transform'], 
                         location=(0,0))
    p.add_layout(color_bar, 'right') 
    center = p.circle('lng', 'lat', radius="radius", alpha=0.6, 
                      color=mapper, source=source)
    show(p)
    save(p)
    return p


# plot
p = plot(df["lat"].mean(), df["lng"].mean(), map_type='satellite')

# add a button widget and configure with the call back
button = Button(label="LoadData")
button.on_click(get_data)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(button, p))

import io
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, Response
app = Flask(__name__)

df = pd.read_csv( "dataset/FARM001.csv", delimiter=",")
df = df.drop(df[df['LATITUDINE_P'] == '-'].index)
farmacie = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df['LONGITUDINE_P'], df['LATITUDINE_P']), crs = 'EPSG:4326')

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/farmacia', methods=['GET'])
def farmacia():
    return render_template('input1.html')

@app.route('/risultatofarmacia', methods=['GET'])
def risultatofarmacia():
    inFarmacia = request.args.get('inFarmacia')
    fig, ax = plt.subplots(figsize = (12,8))
    farmacieCTX = farmacie.to_crs(epsg=3857)
    farmacieCTX[farmacieCTX.FARMACIA.str.contains(inFarmacia)].plot(ax=ax)
    ctx.add_basemap(ax=ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=32245, debug=True)
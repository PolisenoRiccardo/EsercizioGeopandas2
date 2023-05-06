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

comuni = gpd.read_file('dataset/Com01012022_WGS84.zip')
farmacie32632 = farmacie.to_crs(32632)
comuniContenuti = comuni[comuni.intersects(farmacie32632.unary_union)]

@app.route('/confini', methods=['GET'])
def confini():
    fig, ax = plt.subplots(figsize = (12,8))  
    comuniContenuti.plot(ax=ax, facecolor='None')
    farmacie32632.plot(ax=ax, markersize=2)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

gioin = gpd.sjoin(comuniContenuti, farmacie32632, predicate='intersects', how = 'left')
elenco = gioin.groupby('COMUNE_left').count()['COD_RIP'].reset_index()

@app.route('/elenco', methods=['GET'])
def elencol(): 
    return render_template('tabella.html', table = elenco.to_html())

@app.route('/mappacomuni', methods=['GET'])
def mappacomuni():
    farmacieComuni = gioin.merge(elenco, on='COMUNE_left')
    fig, ax = plt.subplots(figsize = (12,8))  
    farmacie.to_crs(epsg=3857).plot(ax = ax, markersize=1, color='pink')
    farmacieComuni.to_crs(epsg=3857).plot(ax=ax , column='COD_RIP_x', cmap='YlGnBu_r', edgecolor='red', alpha=0.75)
    ctx.add_basemap(ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/torta', methods=['GET'])
def torta():
    elenco = gioin.groupby('COMUNE_left').count()['COD_RIP']
    labels = elenco.index
    dati = elenco
    fig, ax = plt.subplots()
    ax.pie(dati, labels=labels)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=32245, debug=True)
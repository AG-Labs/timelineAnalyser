from mpl_toolkits.basemap import Basemap
import matplotlib
matplotlib.use('qt5agg')
import matplotlib.pyplot as plt
import numpy as np
from shapely import geos
import timelineAnalysis


llcrnrlon = -10.5
llcrnrlat=48
urcrnrlon=4
urcrnrlat=59

myfigure = plt.figure(1)

m = Basemap(llcrnrlon=llcrnrlon,llcrnrlat=llcrnrlat,urcrnrlon=urcrnrlon,urcrnrlat=urcrnrlat,
             resolution='i', projection='cyl', lat_0 = 39.5, lon_0 = -3.25)

m.drawmapboundary(fill_color='azure')
m.fillcontinents(color='sandybrown',lake_color='azure')

parallels = np.arange(0.,81,10.)
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[True,False,False,True])
# plot blue dot on Boulder, colorado and label it as such.
lon, lat = -104.237, 40.125 # Location of Boulder
# convert to map projection coords.
# Note that lon,lat can be scalars, lists or numpy arrays.
xpt,ypt = m(lon,lat)
# convert back to lat/lon
lonpt, latpt = m(xpt,ypt,inverse=True)


stucturedData, heatmapData = timelineAnalysis.unpickleData()
reducedHeatmapData = timelineAnalysis.createHeatMap(stucturedData, 4)

uniquePoints = reducedHeatmapData.keys()

squareDataLon, squareDataLat = timelineAnalysis.getSquare(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat, uniquePoints)

points = m.plot(squareDataLon,squareDataLat, 'bo', latlon = True)


point, = m.plot(xpt,ypt,'bo')  # plot a blue dot there
# put some text next to the dot, offset a little bit
# (the offset is in map projection coordinates)
annotation = plt.annotate('(%5.1fW,%3.1fN)' % (lon, lat), xy=(xpt,ypt),
             xytext=(20,35), textcoords="offset points", 
             bbox={"facecolor":"w", "alpha":0.5}, 
             arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))

def onclick(event):
	print(event)
	ix, iy = event.xdata, event.ydata
	xpti, ypti = m(ix, iy,inverse=True)
	string = '(%5.1fW,%3.1fN)' % (xpti, ypti)
	print(string)
	annotation.xy = (ix, iy)
	point.set_data([ix], [iy])
	annotation.set_text(string)
	plt.gcf().canvas.draw_idle()


figg = plt.gcf()
cid = figg.canvas.mpl_connect("button_press_event", onclick)


plt.show()
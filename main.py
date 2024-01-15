#!/usr/bin/env python
import time
from opensign import OpenSign
from opensign.canvas import OpenSignCanvas
from PIL import Image
import fetchTimes
import datetime

def addIconInline(message, trainLine, continueLine=True, y_offset=0):
    """Add an image to the canvas.
    :param string file: The filename of the image. This should be the full path.
    """
    x, y = message._cursor
    file = '/home/subwayclock/subway/icons/icons_28x28/'+trainLine+'.png'
    new_image = Image.open(file).convert("RGBA")
    message._enlarge_canvas(new_image.width, new_image.height)
    message._image.alpha_composite(new_image, dest=(x, y+y_offset))
    if continueLine:
        message._cursor[0] += new_image.width

def createImg():
    if message:
        del message
    
    # initialize the fetch object
    mta =fetchTimes.subwayFetch()
    
    # initialize the scroller
    message = OpenSignCanvas()
   
    # add font
    message.add_font("piboto-Bold", "/usr/share/fonts/truetype/piboto/PibotoLtBold.ttf", 22)
    
    # force the canvas to the dimensions of the matrix
    message._enlarge_canvas(0,64)

    # station names to display - stored in a list 
    displayStations = ['W 4 St-Wash Sq','Christopher St-Sheridan Sq','Bleecker St']

    # top line -----
    for stationStop in displayStations:
        message.add_text(stationStop + 'uptown', color=(255, 255, 200))
        routes = [str(stop['routeId']) for stop in mta.stations if stop['name'] == stationStop]
        for route in routes:
            addIconInline(message=message, trainLine=route, continueLine=True)
            message.add_text(mta.getArrivalStr(stopName=stationStop, direction='uptown',route=route, arrivals=arrivals), color=(255, 255, 200))
    
    # bottom line -----
    # reset the cursor position
    message._cursor = [0,0]

    arrivals = mta.getAllArrivals()

    for stationStop in displayStations:
        message.add_text(stationStop + 'uptown', color=(255, 255, 200))
        routes = [str(stop['routeId']) for stop in mta.stations if stop['name'] == stationStop]
        for route in routes:
            addIconInline(message=message, trainLine=route, continueLine=True)
            message.add_text(mta.getArrivalStr(stopName=stationStop, direction='uptown',route=route, arrivals=arrivals), color=(255, 255, 200))

    message.add_text("downtown ", color=(255, 255, 200),y_offset=32)
    addIconInline(message=message, trainLine='1', continueLine=True, y_offset=32)
    message.add_text("  also super late ", color=(255, 255, 200),y_offset=32)
    
    print('message canvas width:', message.width)
    print('message canvas height:', message.height)
    

def main():

    # initialize the sign object
    sign = OpenSign(columns=64, 
                    rows=64,
                    chain=2,
                    brightness=70,
                    slowdown_gpio=4)
    
    matrixWidth = sign._matrix.width
    matrixHeight = sign._matrix.height
    
    print('matrix width:', sign._matrix.width)
    print('matrix height:', sign._matrix.height)
    
    
    
    # messageCenter_x, messageCenter_y = sign._get_centered_position(message)
    

    tock = datetime.datetime.now()
    tick = datetime.datetime.now()
    while tick-tock > 60:
        sign.scroll_from_to(message, duration=4, start_x=0-message.width, start_y=0, end_x=matrixWidth, end_y=0)
        tick = datetime.datetime.now()


# Main function
if __name__ == "__main__":
    main()

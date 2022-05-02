#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 20:44:55 2021

@author: supun
"""

def import_or_install(package,showPrint=False):
    import pip
    try:
        __import__(package)
        if(showPrint):
            print(package+" imported successfully")
    except ImportError:
        pip.main(['install','--user', package])
        __import__(package)
        if(showPrint):
            print(package+" installed successfully")
            
def import_libs(*arg):
    showPrint=False
    arg=list(arg)
    for i in arg:
        if(i=="show_prints"):
            showPrint=True
            arg.remove(i)
    for i in arg:
        if i not in dir():
            import_or_install(i,showPrint)  
            
def readFit(path, showPrint=False):
    if(showPrint):
        import_libs("astropy","matplotlib","numpy","datetime","time","glob","cv2","os","show_prints")
    else:
        import_libs("astropy","matplotlib","numpy","datetime","time","glob","cv2","os")
    from astropy.io import fits
    import os
    if(os.path.isfile(path)):
        hdu=fits.open(path)
        data = hdu[0].data
        freqs= hdu[1].data  ['Frequency'][0] # extract frequency axis
        timeax = hdu[1].data  ['Time'][0]      # extract time axis
        dT = hdu[0].header['CDELT1']     # extract time resolution
        datum      = hdu[0].header['DATE-OBS']   # take first file
        T0         = hdu[0].header['TIME-OBS']   # take first file
        instrument = hdu[0].header['INSTRUME']
        content    = hdu[0].header['CONTENT']
        T1         = hdu[0].header['TIME-END']  # take first file
        telescope    = hdu[0].header['TELESCOP']
        object    = hdu[0].header['OBJECT']
        #author    = hdu[0].header['AUTHOR']
        return {'isError':False,'data':data,'frequencyAxis':freqs,'timeAxis':timeax,'timeResolution':dT,'date-obs':datum,'time-obs':T0,'instrument':instrument,'content':content,'timeEnd':T1,'telescope':telescope,'object':object}
    else:
        return {'isError':True,'error':"Error: file not found in the directory !"}
    
    
def showPlot(path,showPrint=False, Tmin =  1, Tmax = 30, vmin = 0, vmax =14 ,bg='dark_background' , xlabel='Observation time [UTC]' ,ylabel='Plasma frequency [MHz]' ,colorbarlbl='dB above background', cmap="plasma"):
    from astropy.io import fits
    import matplotlib.pyplot as plt 
    from matplotlib import cm
    import numpy as np
    import matplotlib.dates as mdates
    import datetime as dt
    import time
    import glob
    import cv2
    import os
    from matplotlib.dates import DateFormatter
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    readfit=readFit(path,showPrint)
    if(readfit['isError']):
        print(readfit['error'])
    else:
        data = readfit['data'] 
        freqs= readfit['frequencyAxis'] # extract frequency axis
        timeax = readfit['timeAxis']     # extract time axis
        dT = readfit['timeResolution']     # extract time resolution
        datum      = readfit['date-obs']    # take first file
        T0         = readfit['time-obs']   # take first file
        instrument = readfit['instrument'] 
        content    = readfit['content'] 
        T1         = readfit['timeEnd']   # take first file
        Tmin =  Tmin # Start time for background averaging [sec]
        Tmax = Tmax # Stop time for background averaging [sec]
        dmean = np.mean(data[:,int(Tmin/dT):int(Tmax/dT)], axis=1,keepdims=True) # all frequencies, time range in pixels
        bgs = data - dmean # subtraction background
        meanspec = np.mean(bgs) # averafe spectrum
        vmin = vmin; # minimum cut for color table, need to play with
        vmax =vmax; # maximum cut for color label, need to play with
        YY = int(datum.split("/")[0])
        MM = int(datum.split("/")[1])
        DD = int(datum.split("/")[2])
        hh = int(T0.split(":")[0])
        mm = int(T0.split(":")[1])
        ss = int(0.5+float(T0.split(":")[2]))
        ss1=float(T0.split(":")[2])
        d0 = dt.datetime(YY,MM,DD,hh,mm,ss)
        unixtime0 = time.mktime(d0.timetuple())
        hh = int(T1.split(":")[0])
        mm = int(T1.split(":")[1])
        ss = int(0.5+float(T1.split(":")[2]))
        d1 = dt.datetime(YY,MM,DD,hh,mm,ss)
        unixtime1 = time.mktime(d1.timetuple())
        x_lims = list(map(dt.datetime.fromtimestamp, [unixtime0, unixtime1]))
        x_lims = mdates.date2num(x_lims)
        y_lims = [min(freqs),max(freqs)]
        plt.style.use(bg)
        fig,ax = plt.subplots(figsize=(14,8))
        im=ax.imshow(bgs, extent = [x_lims[0], x_lims[1],  y_lims[0], y_lims[1]],aspect='auto',cmap=cmap,norm=plt.Normalize(vmin, vmax))
        ax.xaxis_date()
        ax.set_xlabel(xlabel,fontsize=15)
        ax.set_ylabel(ylabel,fontsize=15)
        ax.set_title(content,fontsize=17)
        for tick in ax.get_xticklabels():
            tick.set_rotation(0) # 20° ... 45°
            tick.set_size(12)
        for tick in ax.get_yticklabels():
            tick.set_rotation(0) # 0° or 90°
            tick.set_size(12)
        ax.tick_params(axis='both', labelsize=14)
        fig.gca().xaxis.set_major_formatter( DateFormatter('%H:%M:%S') )
        start, end = ax.get_xlim()
        deltaT = (end-start)/12
        ax.xaxis.set_ticks(np.arange(start, end, deltaT))
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='3%', pad=0.08)
        xxc=fig.colorbar(im, cax=cax, orientation='vertical')
        xxc.set_label(label=colorbarlbl, size='14')
        xxc.ax.tick_params(labelsize='14')
        fig.tight_layout() # makes x-axis label visible
        plt.show()
    

    
def makePlot(path,showPrint=False, Tmin =  1, Tmax = 30, vmin = 0, vmax =14 ,bg='dark_background' , xlabel='Observation time [UTC]' ,ylabel='Plasma frequency [MHz]' ,colorbarlbl='dB above background', cmap="plasma"):
    from astropy.io import fits
    import matplotlib.pyplot as plt 
    from matplotlib import cm
    import numpy as np
    import matplotlib.dates as mdates
    import datetime as dt
    import time
    import glob
    import cv2
    import os
    from matplotlib.dates import DateFormatter
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    readfit=readFit(path,showPrint)
    if(readfit['isError']):
        print(readfit['error'])
    else:
        data = readfit['data'] 
        freqs= readfit['frequencyAxis'] # extract frequency axis
        timeax = readfit['timeAxis']     # extract time axis
        dT = readfit['timeResolution']     # extract time resolution
        datum      = readfit['date-obs']    # take first file
        T0         = readfit['time-obs']   # take first file
        instrument = readfit['instrument'] 
        content    = readfit['content'] 
        T1         = readfit['timeEnd']   # take first file
        Tmin =  Tmin # Start time for background averaging [sec]
        Tmax = Tmax # Stop time for background averaging [sec]
        dmean = np.mean(data[:,int(Tmin/dT):int(Tmax/dT)], axis=1,keepdims=True) # all frequencies, time range in pixels
        bgs = data - dmean # subtraction background
        meanspec = np.mean(bgs) # averafe spectrum
        vmin = vmin; # minimum cut for color table, need to play with
        vmax =vmax; # maximum cut for color label, need to play with
        YY = int(datum.split("/")[0])
        MM = int(datum.split("/")[1])
        DD = int(datum.split("/")[2])
        hh = int(T0.split(":")[0])
        mm = int(T0.split(":")[1])
        ss = int(0.5+float(T0.split(":")[2]))
        ss1=float(T0.split(":")[2])
        d0 = dt.datetime(YY,MM,DD,hh,mm,ss)
        unixtime0 = time.mktime(d0.timetuple())
        hh = int(T1.split(":")[0])
        mm = int(T1.split(":")[1])
        ss = int(0.5+float(T1.split(":")[2]))
        d1 = dt.datetime(YY,MM,DD,hh,mm,ss)
        unixtime1 = time.mktime(d1.timetuple())
        x_lims = list(map(dt.datetime.fromtimestamp, [unixtime0, unixtime1]))
        x_lims = mdates.date2num(x_lims)
        y_lims = [min(freqs),max(freqs)]
        fig,ax = plt.subplots(figsize=(14,8))
        im=ax.imshow(bgs, extent = [x_lims[0], x_lims[1],  y_lims[0], y_lims[1]],aspect='auto',cmap=cmap,norm=plt.Normalize(vmin, vmax))
        plt.close()
        return (fig,ax,im,content)


def displayPlot(path,showPrint=False, Tmin =  1, Tmax = 30, vmin = 0, vmax =14 ,bg='dark_background' , xlabel='Observation time [UTC]' ,ylabel='Plasma frequency [MHz]' ,colorbarlbl='dB above background', cmap="plasma"):
    import numpy as np
    import matplotlib.pyplot as plt 
    fig,ax,im,content=makePlot(path,showPrint=showPrint, Tmin = Tmin, Tmax = Tmax, vmin = vmin, vmax =vmax ,bg=bg , xlabel=xlabel ,ylabel=ylabel ,colorbarlbl=colorbarlbl, cmap=cmap)
    ax.xaxis_date()
    ax.set_xlabel('Observation time [UTC]',fontsize=15)
    ax.set_ylabel('Plasma frequency [MHz]',fontsize=15)
    ax.set_title(content,fontsize=17)

    for tick in ax.get_xticklabels():
        tick.set_rotation(0) # 20° ... 45°
        tick.set_size(12)
    for tick in ax.get_yticklabels():
        tick.set_rotation(0) # 0° or 90°
        tick.set_size(12)

    ax.tick_params(axis='both', labelsize=14)

    from matplotlib.dates import DateFormatter
    fig.gca().xaxis.set_major_formatter( DateFormatter('%H:%M:%S') )
    start, end = ax.get_xlim()
    deltaT = (end-start)/12
    ax.xaxis.set_ticks(np.arange(start, end, deltaT))
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='3%', pad=0.08)
    xxc=fig.colorbar(im, cax=cax, orientation='vertical')
    xxc.set_label(label='dB above background', size='14')
    xxc.ax.tick_params(labelsize='14')
    fig.tight_layout() # makes x-axis label visible
    dummy = plt.figure()
    new_manager = dummy.canvas.manager
    new_manager.canvas.figure = fig
    fig.set_canvas(new_manager.canvas)
    plt.show()


def getAreaofBursts(path,showPrint=False,max_area_count=3, Tmin =  1, Tmax = 30, vmin = 0, vmax =14 ,bg='dark_background' , xlabel='Observation time [UTC]' ,ylabel='Plasma frequency [MHz]' ,colorbarlbl='dB above background', cmap="plasma"):
    import numpy as np
    import matplotlib.pyplot as plt
    import cv2
    fig,ax,im,content=makePlot(path,showPrint=showPrint, Tmin = Tmin, Tmax = Tmax, vmin = vmin, vmax =vmax ,bg=bg , xlabel=xlabel ,ylabel=ylabel ,colorbarlbl=colorbarlbl, cmap=cmap)
    # redraw the canvas
    fig.canvas.draw()
    #convert canvas to image
    img = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8,sep='')
    img  = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    img = img[70:503, 128:906]
    
    # img is rgb, convert to opencv's default bgr
    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)

    # convert the image to grayscale format
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # apply binary thresholding
    ret, thresh = cv2.threshold(img_gray, 80, 255, cv2.THRESH_BINARY)

    # detect the contours on the binary image using cv2.CHAIN_APPROX_NONE
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    
    # function to display contour area
    def find_contour_areas(contours):
        areas=[]
        for cnt in contours:
            cont_area=cv2.contourArea(cnt)
            if(cont_area>0):
                areas.append(cont_area)
        return areas

    #sorting contours from larger area to smaller area
    sorted_contours_by_area=sorted(contours, key=cv2.contourArea, reverse=True)

    if(showPrint):
        #count of contours
        print("Number of contours detected = ", len(contours))
        #printing contours in order
        print('Contour areas in order', find_contour_areas(sorted_contours_by_area))
    
    return_list=[]
    if(max_area_count=='all'):
        return_list=find_contour_areas(sorted_contours_by_area)
    else:
        if(max_area_count<len(find_contour_areas(sorted_contours_by_area))):
            return_list=find_contour_areas(sorted_contours_by_area)[0:max_area_count]
        else:
            return_list=find_contour_areas(sorted_contours_by_area)
    
    return_dict={'total_area':sum(return_list),'area_list':return_list}
    return return_dict


def saveDisplayedPlot(path,savename="latest.png",showPrint=False, Tmin =  1, Tmax = 30, vmin = 0, vmax =14 ,bg='dark_background' , xlabel='Observation time [UTC]' ,ylabel='Plasma frequency [MHz]' ,colorbarlbl='dB above background', cmap="plasma"):
    import numpy as np
    import matplotlib.pyplot as plt 
    fig,ax,im,content=makePlot(path,showPrint=showPrint, Tmin = Tmin, Tmax = Tmax, vmin = vmin, vmax =vmax ,bg=bg , xlabel=xlabel ,ylabel=ylabel ,colorbarlbl=colorbarlbl, cmap=cmap)
    ax.xaxis_date()
    ax.set_xlabel('Observation time [UTC]',fontsize=15)
    ax.set_ylabel('Plasma frequency [MHz]',fontsize=15)
    ax.set_title(content,fontsize=17)

    for tick in ax.get_xticklabels():
        tick.set_rotation(0) # 20° ... 45°
        tick.set_size(12)
    for tick in ax.get_yticklabels():
        tick.set_rotation(0) # 0° or 90°
        tick.set_size(12)

    ax.tick_params(axis='both', labelsize=14)

    from matplotlib.dates import DateFormatter
    fig.gca().xaxis.set_major_formatter( DateFormatter('%H:%M:%S') )
    start, end = ax.get_xlim()
    deltaT = (end-start)/12
    ax.xaxis.set_ticks(np.arange(start, end, deltaT))
    # from mpl_toolkits.axes_grid1 import make_axes_locatable
    # divider = make_axes_locatable(ax)
    # cax = divider.append_axes('right', size='3%', pad=0.08)
    # xxc=fig.colorbar(im, cax=cax, orientation='vertical')
    # xxc.set_label(label='dB above background', size='14')
    # xxc.ax.tick_params(labelsize='14')
    fig.tight_layout() # makes x-axis label visible
    dummy = plt.figure()
    new_manager = dummy.canvas.manager
    new_manager.canvas.figure = fig
    fig.set_canvas(new_manager.canvas)
    fig.savefig(savename)


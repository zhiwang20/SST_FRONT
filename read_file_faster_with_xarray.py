import numpy as np
#from netCDF4 import Dataset
#import datetime
import cv2
import pandas as pd
from pymongo import MongoClient
import glob
import xarray as xr

client = MongoClient('mongodb://localhost:27017/')
db = client.capstone
collection = db['test3']
#files = glob.glob('dataset/test/*.nc')
files = glob.glob('dataset/20201201000000-STAR-L3C_GHRSST-SSTsubskin-ABI_G16-ACSPO_V2.80-v02.0-fv01.0.nc')
process_fail = 0
total_files = len(files)
for file in files:
    try: #extrude invalid file: 'sst_front_position' variable does not exist
        with xr.open_dataset(file) as data:
            #data = Dataset('dataset/url/c.nc','r')
            #data = Dataset(file,'r')
            print(file)
            ##since sst front postion variable consists of only 0s and 1s that has shape of (9000,18000); 0- front postion not present, 1-yes presented
            #so we can think this as an image: all 1s in this image are what we needed.
            #so connectedComponent feature will break all 1s into 211 curves, in this example
            #the goal is to store these curves into database with correspodning time,lat,lon,angle,magnitude,sst
            #sst_front_position = data.variables['sst_front_position'][:].data.reshape(9000,18000)
            sst_front_position = data.variables['sst_front_position'][0,:,:].astype('int8') #original float32; need int8 because cv2.connectedComponents(d) won't work otherwise
            d = np.where(sst_front_position == 1,sst_front_position,0)  #make all fill-on value 0
            num_labels, labels_im = cv2.connectedComponents(d) #default connectivity=8
            print(num_labels)
            if num_labels == 1:  #skip this file if sst_front_position are all 0s 
                continue
            
            lat = data.variables['lat'][:]
            lon = data.variables['lon'][:]
            print('test1')
            sst = data.variables['sea_surface_temperature'][0,:,:]
            #print(sst[4511][9400]) #print -- when it is a fill-on value; without using .data
            print('test2')
            satellite_zenith_angle = data.variables['satellite_zenith_angle'][0,:,:]
            print('test3')
            sst_gradient_magnitude = data.variables['sst_gradient_magnitude'][0,:,:]
            print('test4')
            sst_dtime = data.variables['sst_dtime'][0,:,:]
            print('test5')
            time = data.indexes['time'].to_datetimeindex() #convert cftime.DatetimeGregorian to DatetimeIndex
            print('start to store a file')
            begin_time = time[0] #ex:Timestamp('2020-12-01 00:00:00')
            #if not all positions presented, then there will be only one num_labels: 0; for loop won't run since num_labels starts at 1
            # if there are positions presented, let's say 212 labels, we want from 1 to 211 since 0 is where position not presented
            for label in range(1,num_labels):
                    x,y = np.where(labels_im == label)
                    list_lat = []
                    list_lon = []
                    list_sst = []
                    list_angle = []
                    list_magnitude = []
                    list_dtime = []

                    for i,j in zip(x,y):
                        #xarray only has lat[i].astype('float64').round(2) instead round(lat[i].astype('float64'),2)
                        #need .values other it will because lat[i] is a xarray.Variable which MongoDB won't work
                        list_lat.append(lat[i].values.astype('float64').round(2))  #lat and lon oringally are two decimals but float64 makes 13 decimals
                        list_lon.append(lon[j].values.astype('float64').round(2))  #need float62; Object of type 'float32' is not JSON serializable 
                        list_sst.append(sst[i][j].values.astype('float64').round(2))
                        list_angle.append(satellite_zenith_angle[i][j].values.astype('float64').round(2))      #float32 is 40.56  #float64: 40.559998, usally after 2nd deciamls all 9s
                        list_magnitude.append(sst_gradient_magnitude[i][j].values.astype('float64').round(3))  #float32 is 0.55 #float64: 0.055000003 usually after 3rd decimals all zeros
                        list_dtime.append(sst_dtime[i][j])  #has dtype='timedelta64[ns]'
                    TIME =str(begin_time + np.timedelta64((sum(list_dtime) / len(list_dtime)).values, 's')) #49583333333 ns == 49.58 seconds ~ 49 seconds
                    #not convert TIME to string also works
                    collection.insert({
                                     "time":TIME,
                                     "lat":list_lat,
                                     "lon":list_lon,
                                     "sst":list_sst,
                                     "satellite_zenith_angle":list_angle,
                                     "sst_gradient_magnitude": list_magnitude})
            print('finsh to store a file')
    except:
        print('fail to process '+file) #sometime old files didn't contain 'sst_front_position' and 'sst_gradient_magnitude' variable; but we focus on 'sst_front_position'
        process_fail+=1
print('failing to process '+str(process_fail/total_files*100)+'%')
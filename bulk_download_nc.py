from ftplib import FTP

url1 = 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/sst/acspo_data/viirs/n20/l3u/2020/' #about 130-144 files per folder; update very frequently
url2 = 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/sst/acspo_data/viirs/npp/l3u/2020/' #about 130-144 files per folder; update very frequently
url3 = 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/sst/acspo_data/modis/aqua/l3u/2020/'  #start to have positions:   217/	8/6/20, 8:11:00 PM
url4 = 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/sst/acspo_data/modis/terra/l3u/2020/'  #start to have positions:  317/		11/11/20, 7:12:00 PM
url5 = 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/sst/acspo_data/avhrr_frac/metopa/l3u/2020/'
url6 = 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/sst/acspo_data/avhrr_frac/metopb/l3u/2020/'
url7 = 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/sst/acspo_data/avhrr_frac/metopc/l3u/2020/'
url8 = 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/sst/acspo_data/abi/g16/l3c/2020/'  #174/		6/23/20, 9:20:00 AM #files before around 20MB after 25-28--later folder>50+
url9 = 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/sst/acspo_data/abi/g17/l3c/2020/'  #174/		6/23/20, 9:22:00 AM  #files before only around 30MB, but after 40MB
url10 = 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/sst/acspo_data/ahi/h08/l3c/2020/' #middle of 172/   6/23/20, 5:48:00 AM
url = [url1,url2,url3,url4,url5,url6,url7,url8,url9,url10]
'''
same folder has same day
 'dataset/20201111004000-STAR-L3U_GHRSST-SSTsubskin-VIIRS_N20-ACSPO_V2.80-v02.0-fv01.0.nc',
 'dataset/20201111225000-STAR-L3U_GHRSST-SSTsubskin-VIIRS_N20-ACSPO_V2.80-v02.0-fv01.0.nc',
 'dataset/20201111234000-STAR-L3U_GHRSST-SSTsubskin-VIIRS_N20-ACSPO_V2.80-v02.0-fv01.0.nc'
2020-11-11 00:40:01
2020-11-11 22:50:01
2020-11-11 23:40:00
'''
#url = 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/sst/acspo_data/viirs/n20/l3u/2020/{}/{}-STAR-L3U_GHRSST-SSTsubskin-VIIRS_N20-ACSPO_V2.80-v02.0-fv01.0.nc'

url = '{}-STAR-L3U_GHRSST-SSTsubskin-VIIRS_NPP-ACSPO_V2.80-v02.0-fv01.0.nc' #change when differnt platform
urls = []
dates = []
#from 20201126000000 to 20201126222000---->round 20201126222000 to 20201126220000
#from 20201126000000 to 20201126225000-----round 20201126225000 to 20201126230000
#trial: reduce files by get rid of for j in range(6)----->(20201107240000-20201107000000)/10000=24; not 24*6=144 files


for i in range(20201201100000,20201201220000,10000): #from 20201107000000 to 20201107235000
    for j in range(6): #0000 to 5000
        dates.append(i)
        i = i + 1000   
#print(dates[-1])
for date in dates:
    urls.append(url.format(date))
print(urls)   
ftp = FTP('ftp.star.nesdis.noaa.gov')
ftp.login() # Username: anonymous password: anonymous@
ftp.cwd('/pub/sod/sst/acspo_data/viirs/npp/l3u/2020/336/')
for url in urls:
    with open(url, 'wb') as fp:
        ftp.retrbinary('RETR ' + url, fp.write)
ftp.quit()
'''
ftp = FTP('ftp.star.nesdis.noaa.gov')
ftp.login() # Username: anonymous password: anonymous@
ftp.cwd('/pub/sod/sst/acspo_data/viirs/npp/l3u/2020/336/')
filenames = ftp.nlst() # get filenames within the directory
#print(filenames)
#print(len(filenames))
for url in filenames:
    with open(url, 'wb') as fp:   #go to that folder
        ftp.retrbinary('RETR ' + url, fp.write)
ftp.quit()
'''
# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: blair liu
# CreatDate: 2021/3/29 14:08
# Description: 
# import os
import time
from osgeo.scripts.gdal_pansharpen import gdal_pansharpen

if __name__ == '__main__':
    pan = 'D:\\temporary\\luolingcun\\gf2_temp\\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771-PAN1.tiff'
    # pan = 'GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771-PAN1.tiff'
    mss = 'D:\\temporary\\luolingcun\\gf2_temp\\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771-MSS1.tiff'
    # mss = 'GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771-MSS1.tiff'
    out = 'D:\\temporary\\luolingcun\\gf2_temp\\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\\test2.tif'
    # out = 'test.tif'
    start_time = time.time()
    gdal_pansharpen(['', '-b', '3', '-b', '2', '-b', '1', '-threads', 'ALL_CPUS', pan, mss, out])
    # gdal_pansharpen([pan, mss, out])
    print(time.time()- start_time)  # 42.39 -> 20.16
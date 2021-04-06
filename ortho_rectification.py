# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: blair liu
# CreatDate: 2021/4/2 19:13
# Description:
import math
import os

from lxml import etree
from osgeo import gdal, osr

"""
正射校正
"""


def ortho_rectification(raster_path, save_path, save_path2, demfile):
    raster_name = os.path.splitext(os.path.split(raster_path)[1])[0]

    # 分辨率
    xml_path = raster_path.replace('.tiff', '.xml')
    tree = etree.parse(xml_path)
    xRes = float(tree.xpath('//ImageGSD/text()')[0])
    yRes = float(tree.xpath('//ImageGSD/text()')[0])

    # 计算UTM区号
    lon = float(((raster_name.split('_'))[2])[1:])
    zone_ = int(math.ceil(lon / 6)) + 30
    zone = int("326" + str(zone_))
    print(zone)
    dstSRS = osr.SpatialReference()
    dstSRS.ImportFromEPSG(zone)

    origin_image = gdal.Open(raster_path)
    # warp_option = gdal.WarpOptions(dstSRS='EPSG:4326',
    #                                creationOptions=["TILED=YES", "COMPRESS=LZW", "COPY_SRC_OVERVIEWS=YES"],
    #                                format="Gtiff", xRes=xRes, yRes=yRes, rpc=True, transformerOptions=demfile)
    # gdal.Warp(save_path, origin_image, options=warp_option)
    gdal.Warp(save_path, origin_image, format="Gtiff", xRes=xRes, yRes=yRes, dstSRS=dstSRS, rpc=True,
              transformerOptions=demfile)
    print('----------------------------------------')
    image = gdal.Open(save_path)
    warp_option = gdal.WarpOptions(dstSRS='EPSG:4326',
                                   creationOptions=["TILED=YES", "COMPRESS=LZW", "COPY_SRC_OVERVIEWS=YES"])
    gdal.Warp(save_path2, image, options=warp_option)


if __name__ == '__main__':
    # 图像路径
    raster_path_ = r"E:\wanling_data\GF2\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771-MSS1.tiff"
    # 保存路径
    # save_path_ = raster_path_.replace('.tiff', '-ortho.tiff')
    save_path_ = r"E:\wanling_data\GF2\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\out\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771-MSS1-ortho.tiff"
    save_path2_ = r"E:\wanling_data\GF2\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\out\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771-MSS1-warp.tiff"
    # DEM
    demfile_ = r"D:\Program Files\Exelis\ENVI53\data\GMTED2010.jp2"
    # 正射校正
    ortho_rectification(raster_path_, save_path_, save_path2_, demfile_)

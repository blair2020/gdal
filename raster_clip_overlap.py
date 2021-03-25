# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: blair liu
# CreatDate: 2021/3/25 10:54
# Description: 
import os
from osgeo import gdal


def raster_pixel_corp_with_overlap(raster_path, crop_size, overlap, save_dir):
    # 读取一些基本信息
    image_name = os.path.splitext(os.path.split(raster_path))
    image = gdal.Open(raster_path)
    image_width = image.RasterXSize  # 宽
    image_height = image.RasterYSize  # 高
    channel = image.RasterCount  # 波段数
    print('image\'s image_width,image_height,channel:', image_width, image_height, channel)
    GT = image.GetGeoTransform()  # 图像的坐标和分辨率信息等
    img_proj = image.GetProjection()  # 图像的投影信息
    # datatype = image.GetRasterBand(1).DataType

    # 计算宽高各有多少块
    col_num = (image_width - crop_size[0]) // (crop_size[0] - overlap[0]) + 1  # 宽度可以分成几块
    row_num = (image_height - crop_size[1]) // (crop_size[1] - overlap[1]) + 1  # 高度可以分成几块
    total = col_num * row_num
    print("row_num:%d   col_num:%d   total:%d" % (row_num, col_num, total))

    for i in range(row_num):  # 高
        for j in range(col_num):  # 宽
            # 只读取小区域，否则会显存不够
            # ReadAsArray(x0, y0, width, height)
            sub_image = image.ReadAsArray(j * (crop_size[0] - overlap[0]), i * (crop_size[1] - overlap[1]), crop_size[0], crop_size[1])
            print('sub_image.shape:', sub_image.shape)

            # 根据反射变换参数计算新图的原点坐标
            top_left_x_new = GT[0] + j * (crop_size[0] - overlap[0]) * GT[1] + i * (crop_size[1] - overlap[1]) * GT[2]
            top_left_y_new = GT[3] + j * (crop_size[0] - overlap[0]) * GT[4] + i * (crop_size[1] - overlap[1]) * GT[5]
            GT_new = (top_left_x_new, GT[1], GT[2], top_left_y_new, GT[4], GT[5])

            # 判断数据类型
            if 'int8' in sub_image.dtype.name:
                datatype = gdal.GDT_Byte  # 1
            elif 'int16' in sub_image.dtype.name:
                datatype = gdal.GDT_UInt16  # 2
            else:
                datatype = gdal.GDT_Float32  # 6

            filename = save_dir + image_name + '_{0:0>4}_{1:0>4}.tif'.format(i, j)
            driver = gdal.GetDriverByName('GTiff')  # 获取指定格式的驱动
            # driver.Create(filename, img_width, img_height, img_bands, datatype)
            new_sub_image = driver.Create(filename, crop_size[0], crop_size[1], channel, datatype)
            new_sub_image.SetGeoTransform(GT_new)
            new_sub_image.SetProjection(img_proj)

            # 保存影像
            if channel == 1:
                new_sub_image.GetRasterBand(1).WriteArray(sub_image)
            else:
                for k in range(channel):
                    new_sub_image.GetRasterBand(k + 1).WriteArray(sub_image[k])
            del new_sub_image
    del image  # 删除变量,保留数据


if __name__ == '__main__':
    # 图像路径
    raster_path_ = ''
    # 裁剪后目标图像大小  x,y
    crop_size_ = [4096, 4096]
    # 重叠像素数 x,y
    overlap_ = [128, 128]
    # 保存路径
    crop_save_dir_ = ''
    raster_pixel_corp_with_overlap(raster_path_, crop_size_, overlap_, crop_save_dir_)


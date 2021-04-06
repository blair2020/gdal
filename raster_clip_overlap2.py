# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: blair liu
# CreatDate: 2021/4/1 11:15
# Description: 

"""
通用图像裁剪：
支持16位和8位
支持4通道3通道1通道
支持超大图像
支持矩形裁剪
支持overlap
"""

import os
import math
from osgeo import gdal
import numpy as np

gdal.UseExceptions()


def get_stretch_scale(array, black_edge=False):
    if not black_edge:
        """计算2%、98%的值"""
        per2 = np.percentile(array, 2)
        per98 = np.percentile(array, 98)
        # 最小值，最大值映射到0-255
        return per2, per98, (per98 - per2) / 255
    else:
        array = array.flatten()
        array = np.delete(array, np.where(array == 0))
        per2 = np.percentile(array, 2)
        per98 = np.percentile(array, 98)
        # 最小值，最大值映射到0-255
        return per2, per98, (per98 - per2) / 255


def count_per2_per98_from_histogram(histogram, black_edge=False):
    if black_edge:
        histogram[0] = 0
    cdf = histogram.cumsum() / histogram.sum()
    for index2, i in enumerate(cdf):
        if i >= 0.02:
            break
    per2 = index2
    for index98, i in enumerate(cdf[::-1]):
        if i <= 0.98:
            break
    per98 = len(cdf) - index98 - 1
    return per2, per98, (per98 - per2) / 255


def raster_pixel_corp_with_overlap(raster_path, crop_size, overlap, save_dir, available_memory=4):
    """
    遥感影像裁剪
    :param raster_path: 影像路径
    :param crop_size: 要裁剪的大小
    :param overlap: 重叠大小
    :param save_dir: 保存文件夹
    :param available_memory: 可用内存
    """
    # 读取一些基本信息
    image_name = os.path.splitext(os.path.split(raster_path)[0])[1]
    image = gdal.Open(raster_path)
    image_width = image.RasterXSize  # 宽
    image_height = image.RasterYSize  # 高
    channel = image.RasterCount  # 波段数
    GT = image.GetGeoTransform()  # 图像的坐标和分辨率信息等
    print(GT)
    img_proj = image.GetProjection()  # 图像的投影信息
    print(img_proj)
    if not img_proj:
        print('该影像没有投影信息')
    datatype = image.GetRasterBand(1).DataType
    print('image\'s image_width,image_height,channel,datatype:', image_width, image_height, channel, datatype)
    # 计算宽高各有多少块
    col_num = (image_width - crop_size[0]) // (crop_size[0] - overlap[0]) + 1  # 宽度可以分成几块
    row_num = (image_height - crop_size[1]) // (crop_size[1] - overlap[1]) + 1  # 高度可以分成几块
    total = col_num * row_num
    print("row_num:%d   col_num:%d   total:%d" % (row_num, col_num, total))

    # 若为16位影像，先计算per2, per98
    if datatype == 2:
        # 判断影像大小 单位G
        capacity = image_width * image_height * channel * 16 / 8589934592
        # 如果影像不大
        if capacity < available_memory:
            print('内存充足')
            array = image.ReadAsArray()
            if channel == 1:
                per2, per98, scale = get_stretch_scale(array, black_edge=True)
            else:
                per2 = []
                per98 = []
                scale = []
                for i in range(min(3, channel)):
                    per2_i, per98_i, scale_i = get_stretch_scale(array[i], black_edge=True)
                    per2 += [per2_i]
                    per98 += [per98_i]
                    scale += [scale_i]
        # 如果影像很大 试着一次读取available_memory图像
        else:
            print('内存不足,开启贫穷模式')
            # 给定内存切多少块
            available_size = int(11585 * math.sqrt(available_memory))
            print('available_size:', available_size)
            available_col_num = image_width // available_size  # 宽度可以分成几块
            available_row_num = image_height // available_size  # 高度可以分成几块
            available_total_num = available_col_num * available_row_num

            # 初始化histogram为全0
            if channel == 1:
                histogram = np.zeros(65536, dtype=np.int64)
            else:
                histogram = np.zeros((min(3, channel), 65536), dtype=np.int64)

            # 循环计算大图的各个小块的available_histogram，累加到histogram
            for i in range(available_col_num):  # 高
                for j in range(available_row_num):  # 宽
                    available_array = image.ReadAsArray(j * available_size, i * available_size, available_size,
                                                        available_size)
                    if channel == 1:
                        available_histogram, _ = np.histogram(available_array, bins=65536, range=(-0.5, 65535.5))
                        histogram += available_histogram
                    else:
                        for k in range(min(3, channel)):
                            available_histogram_k, _ = np.histogram(available_array[k], bins=65536,
                                                                    range=(-0.5, 65535.5))
                            histogram[k] += available_histogram_k

            # 由histogram计算per2, per98
            if channel == 1:
                per2, per98, scale = count_per2_per98_from_histogram(histogram, black_edge=True)
            else:
                per2 = []
                per98 = []
                scale = []
                for i in range(min(3, channel)):
                    per2_i, per98_i, scale_i = count_per2_per98_from_histogram(histogram[i], black_edge=True)
                    per2 += [per2_i]
                    per98 += [per98_i]
                    scale += [scale_i]
        print('per2, per98, scale:', per2, per98, scale)

    for i in range(row_num):  # 高
        for j in range(col_num):  # 宽
            # 只读取小区域，否则会显存不够
            # ReadAsArray(x0, y0, width, height)
            sub_image = image.ReadAsArray(j * (crop_size[0] - overlap[0]), i * (crop_size[1] - overlap[1]), crop_size[0], crop_size[1])
            # print('sub_image.shape:', sub_image.shape)
            if len(sub_image.shape) == 3:
                sub_image = sub_image[:min(3, channel)]

            # 根据反射变换参数计算新图的原点坐标
            top_left_x_new = GT[0] + j * (crop_size[0] - overlap[0]) * GT[1] + i * (crop_size[1] - overlap[1]) * GT[2]
            top_left_y_new = GT[3] + j * (crop_size[0] - overlap[0]) * GT[4] + i * (crop_size[1] - overlap[1]) * GT[5]
            GT_new = (top_left_x_new, GT[1], GT[2], top_left_y_new, GT[4], GT[5])

            # filename = save_dir + image_name + '_{0:0>4}_{1:0>4}.tif'.format(i, j)
            filename = os.path.join(save_dir, image_name + '_{0:0>4}_{1:0>4}.tif'.format(i, j))
            driver = gdal.GetDriverByName('GTiff')  # 获取指定格式的驱动
            # driver.Create(filename, img_width, img_height, img_bands, datatype)
            new_sub_image = driver.Create(filename, crop_size[0], crop_size[1], min(3, channel), 1)
            new_sub_image.SetGeoTransform(GT_new)
            new_sub_image.SetProjection(img_proj)

            # 如果16位就要16位转8位
            if datatype == 2:
                if channel == 1:
                    sub_image[sub_image < per2] = per2
                    sub_image[sub_image > per98] = per98
                    sub_image = (sub_image - per2) / scale
                else:
                    for k in range(min(3, channel)):
                        k_sub_image = sub_image[k]
                        k_sub_image[k_sub_image < per2[k]] = per2[k]
                        k_sub_image[k_sub_image > per98[k]] = per98[k]
                        sub_image[k] = (k_sub_image - per2[k]) / scale[k]
                    # 4通道BGR->RGB
                    if channel == 4:
                        sub_image = sub_image[::-1]
            # 保存影像
            if channel == 1:
                new_sub_image.GetRasterBand(1).WriteArray(sub_image)
            else:
                for k in range(min(3, channel)):
                    new_sub_image.GetRasterBand(k + 1).WriteArray(sub_image[k])
            del new_sub_image
    del image  # 删除变量,保留数据


if __name__ == '__main__':
    # 图像路径
    # raster_path_ = r"E:\wanling_data\GF2\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771-MSS1.tiff"
    # raster_path_ = r"E:\wanling_data\GF2\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\SV1-04_20200824_L2A0000960913_1012001921320002_01.tif"
    # raster_path_ = r"E:\wanling_data\111.tif"
    # raster_path_ = r"E:\wanling_data\GF2\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\SV1-04_20200825114705_L2A0000960913_1012001921320002_01_FUSION_ZQ-3-XJP102\SV1-04_20200824_L2A0000960913_1012001921320002_01.img"
    # raster_path_ = r"E:\wanling_data\GF2\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\JL1KF01A_20201012092659_200032303_102_001_L5_5m_PAN.tif"
    # raster_path_ = r"E:\wanling_data\GF2\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\JL101K_PMS06_20200311100859_200022947_101_0002_001_L1_MSS\JL101K_PMS06_20200311100859_200022947_101_0002_001_L1_MSS.tif"
    # raster_path_ = r"E:\wanling_data\GF2\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\JL1KF01A_PMS06_20200618084356_200026919_101_0003_001_L1_PAN\JL1KF01A_PMS06_20200618084356_200026919_101_0003_001_L1_PAN.tif"

    raster_path_ = "E:\wanling_data\GF2\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\JL1KF01A_PMS04_20200629005323_200027487_101_0005_001_L2D_PSH\JL1KF01A_PMS04_20200629005323_200027487_101_0005_001_L2D_PSH.tif"
    # 裁剪后目标图像大小  x,y
    crop_size_ = [4096, 4096]
    # 重叠像素数 x,y
    overlap_ = [0, 0]
    # 保存路径
    crop_save_dir_ = r"E:\wanling_data\GF2\GF2_PMS1_E2.0_N41.3_20160929_L1A0001854771\out"
    raster_pixel_corp_with_overlap(raster_path_, crop_size_, overlap_, crop_save_dir_)

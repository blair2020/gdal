# *_*coding: utf-8 *_*
# author --liming--

'''
此程序可处理多张遥感图像分幅问题
缺点：不能处理大图像，内存不足
可处理大图像的修改版见raster_clip2.py
但raster_clip2.py是处理单张程序
'''

import os
# import numpy as np
from osgeo import gdal


# 定义读取和保存图像的类
class GRID:

    def load_image(self, filename):  # 加载遥感影像
        image = gdal.Open(filename)

        img_width = image.RasterXSize  # 宽
        img_height = image.RasterYSize  # 高
        '''
        GetGeoTransform()
        返回：六个参数
        GeoTransform[0],GeoTransform[3]  左上角位置
        GeoTransform[1]是像元宽度
        GeoTransform[5]是像元高度
        如果影像是指北的,GeoTransform[2]和GeoTransform[4]这两个参数的值为0
        如果图像不含地理坐标信息，默认返回值是：(0,1,0,0,0,1)
        Xgeo = GT(0) + Xpixel*GT(1) + Yline*GT(2)
        Ygeo = GT(3) + Xpixel*GT(4) + Yline*GT(5)
        '''
        img_geotrans = image.GetGeoTransform()  # 图像的坐标和分辨率信息等
        img_proj = image.GetProjection()  # 图像的投影信息
        img_data = image.ReadAsArray(0, 0, img_width, img_height)

        del image

        return img_proj, img_geotrans, img_data

    def write_image(self, filename, img_proj, img_geotrans, img_data):  # 保存遥感影像
        # 判断栅格数据类型
        if 'int8' in img_data.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in img_data.dtype.name:
            datatype = gdal.GDT_UInt16
        else:
            datatype = gdal.GDT_Float32

        # 判断数组维度
        if len(img_data.shape) == 3:
            img_bands, img_height, img_width = img_data.shape
        else:
            img_bands, (img_height, img_width) = 1, img_data.shape

        # 创建文件
        '''
        GetDriverByName('xxx') 
        获取指定格式的驱动
        'GTiff':tif图像
        'HFA':Erdas的img格式
        'ENVI':ENVI的hdr文件
        '''
        driver = gdal.GetDriverByName('GTiff')  # 获取指定格式的驱动
        image = driver.Create(filename, img_width, img_height, img_bands, datatype)

        image.SetGeoTransform(img_geotrans)
        image.SetProjection(img_proj)

        # 保存影像
        if img_bands == 1:
            image.GetRasterBand(1).WriteArray(img_data)
        else:
            for i in range(img_bands):
                image.GetRasterBand(i + 1).WriteArray(img_data[i])

        del image  # 删除变量,保留数据


if __name__ == '__main__':
    import time
    import argparse

    parser = argparse.ArgumentParser(description='load remote sensing image and split to patch')
    # 待处理图像路径
    parser.add_argument('--image_path',
                        default='/media/lm/1E7FBDC6EEE168BC/RS_Dataset/test_image/',
                        help='remote sensing image path')
    # 分块大小
    parser.add_argument('--patch_size',
                        default=1000,
                        help='patch size')
    # 分块图像保存路径
    parser.add_argument('--patch_save',
                        default='/media/lm/1E7FBDC6EEE168BC/RS_Dataset/patch_save/',
                        help='save path of patch image')
    args = parser.parse_args()
    print('待处理图像路径为:{}'.format(args.image_path))
    print('分块大小为:{}'.format(args.patch_size))
    print('分块图像保存路径:{}'.format(args.patch_save))

    image_path = args.image_path
    # 待处理图像列表
    image_list = os.listdir(image_path)
    # image_list.sort(key=lambda x: int(x[:-4])) # 对文件夹中的图像进行排序
    # 待处理图像数目
    image_num = len(image_list)

    # 开始时间
    t_start = time.time()
    for k in range(image_num):
        # 第k张图像开始处理时间
        time_start = time.time()
        img_name = image_path + image_list[k]
        proj, geotrans, data = GRID().load_image(img_name)

        # 图像分块
        patch_size = args.patch_size
        patch_save = args.patch_save
        channel, width, height = data.shape

        num = 0
        for i in range(width // patch_size):  # 宽
            for j in range(height // patch_size):  # 高
                num += 1
                sub_image = data[:, i * patch_size:(i + 1) * patch_size, j * patch_size:(j + 1) * patch_size]
                GRID().write_image(patch_save + '{}.tif'.format(num), proj, geotrans, sub_image)

        # 第k张图像结束处理时间
        time_end = time.time()
        print('第{}张图像分块完毕, 耗时:{}秒'.format(k + 1, round((time_end - time_start), 4)))

    # 结束时间
    t_end = time.time()
    print('所有图像处理完毕,耗时:{}秒'.format(round((t_end - t_start), 4)))

# *_*coding: utf-8 *_*
# author --blair--

'''
本程序可处理单张大图像的分幅问题
支持单波段和多波段
缺点：分幅过程中不足size的部分舍去
如想保留加判断min（size，width- size * （i + 1））
'''

import time
from osgeo import gdal

# 开始时间
t_start = time.time()
# 待处理图像
# image_path = 'E:/陆良县/陆良县图层/陆良县图层/Extract_tif11.tif'
image_path = 'E:/陆良县/DLTB矢量转栅格/DLTB_PolygonToRaster51.tif'
image = gdal.Open(image_path)
print(image)
img_width = image.RasterXSize  # 宽
img_height = image.RasterYSize  # 高
channel = image.RasterCount  # 波段数
print('image\'s img_width,img_height,channel:', img_width, img_height, channel)
GT = image.GetGeoTransform()  # 图像的坐标和分辨率信息等
print('GT:', GT)
img_proj = image.GetProjection()  # 图像的投影信息
print('img_proj:\n', img_proj)
datatype = image.GetRasterBand(1).DataType
print('datatype:', datatype)
# print(gdal.GDT_Byte, gdal.GDT_UInt16, gdal.GDT_Float32)

del image  # 删除变量,保留数据

# 定义切图的大小（矩形框）
size = 1024
col_num = img_width // size  # 宽度可以分成几块
row_num = img_height // size  # 高度可以分成几块
total = col_num * row_num
print("row_num:%d   col_num:%d   total:%d" % (row_num, col_num, total))

# 保存路径
# save_path = 'G:/sat/'
# save_path = 'G:/label2/'
# save_path = 'E:/luliangxian_dataset/clip_1024_version_OG/sat/'
save_path = 'E:/luliangxian_dataset/clip_1024_version_OG/label/'
for i in range(row_num):  # 高
    for j in range(col_num):  # 宽
        # print('i_j:', i, j)
        image = gdal.Open(image_path)
        # 只读取小区域，否则会显存不够
        # ReadAsArray(x0, y0, width, height)
        sub_image = image.ReadAsArray(j * size, i * size, size, size)
        print('sub_image.shape:', sub_image.shape)

        # 根据反射变换参数计算新图的原点坐标
        top_left_x_new = GT[0] + j * size * GT[1] + i * size * GT[2]
        top_left_y_new = GT[3] + j * size * GT[4] + i * size * GT[5]
        GT_new = (top_left_x_new, GT[1], GT[2], top_left_y_new, GT[4], GT[5])

        # if 'int8' in image.dtype.name:
        #     datatype = gdal.GDT_Byte  # 1
        # elif 'int16' in sub_image.dtype.name:
        #     datatype = gdal.GDT_UInt16  # 2
        # else:
        #     datatype = gdal.GDT_Float32  # 6

        filename = save_path + '{0:0>3}_{1:0>3}.tif'.format(i, j)
        driver = gdal.GetDriverByName('GTiff')  # 获取指定格式的驱动
        # driver.Create(filename, img_width, img_height, img_bands, datatype)
        image = driver.Create(filename, size, size, channel, datatype)

        image.SetGeoTransform(GT_new)
        image.SetProjection(img_proj)

        # 保存影像
        if channel == 1:
            image.GetRasterBand(1).WriteArray(sub_image)
        else:
            for k in range(channel):
                image.GetRasterBand(k + 1).WriteArray(sub_image[k])

        del image  # 删除变量,保留数据

        t_used = int(time.time() - t_start)
        t_pre = int(t_used * (total - (i * col_num + j + 1)) / (i * col_num + j + 1))
        t_pre_m, t_pre_s = divmod(t_pre, 60)
        t_pre_h, t_pre_m = divmod(t_pre_m, 60)
        t_pre = str(t_pre_h) + 'h:' + str(t_pre_m) + 'm:' + str(t_pre_s) + 's'

        print('{}_{}处理完成,进度:{}/{},已耗时：{}s, 预计剩余时间：'.format(i, j, i * col_num + j + 1, total, t_used), t_pre)
    print('=' * 40)
# 结束时间
t_end = time.time()
print('图像处理完毕,耗时:{}秒'.format(round((t_end - t_start), 4)))

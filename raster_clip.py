# *_*coding: utf-8 *_*
# author --liumingliang--


import time
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
        
        GeoTransform[0] /* top left x 左上角x坐标*/
        GeoTransform[1] /* w--e pixel resolution 东西方向上的像素分辨率*/
        GeoTransform[2] /* rotation, 0 if image is "north up" 如果北边朝上，地图的旋转角度*/
        GeoTransform[3] /* top left y 左上角y坐标*/
        GeoTransform[4] /* rotation, 0 if image is "north up" 如果北边朝上，地图的旋转角度*/
        GeoTransform[5] /* n-s pixel resolution 南北方向上的像素分辨率*/
        
        Xgeo = GT(0) + Xpixel*GT(1) + Yline*GT(2)
        Ygeo = GT(3) + Xpixel*GT(4) + Yline*GT(5)
        '''
        img_geotrans = image.GetGeoTransform()  # 图像的坐标和分辨率信息等
        img_proj = image.GetProjection()  # 图像的投影信息
        # ReadAsArray(j, i, nCols, nRows)
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

    image_path = ''  # 待处理图像
    patch_size = 512  # 分块大小
    patch_save = './'  # 分块图像保存路径
    print('待处理图像为:{}'.format(image_path))
    print('分块大小为:{}'.format(patch_size))
    print('分块图像保存路径:{}'.format(patch_save))

    # 开始时间
    t_start = time.time()
    proj, geotrans, data = GRID().load_image(image_path)

    print('遥感影像的shape：', data.shape)
    if len(data.shape) == 3:
        # channel, width, height = data.shape
        channel, height, width = data.shape
    else:
        # channel, (width, height) = 1, data.shape
        channel, (height, width) = 1, data.shape

    num = 0
    # for i in range(width // patch_size):  # 宽
    for i in range(height // patch_size):  # 高
        # for j in range(height // patch_size):  # 高
        for j in range(width // patch_size):  # 宽
            num += 1
            sub_image = data[:, i * patch_size:(i + 1) * patch_size, j * patch_size:(j + 1) * patch_size]
            GRID().write_image(patch_save + '{}.tif'.format(num), proj, geotrans, sub_image)

    # 结束时间
    t_end = time.time()
    print('图像处理完毕,耗时:{}秒'.format(round((t_end - t_start), 4)))

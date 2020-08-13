from osgeo import gdal

image_path = 'G:/陆良县/陆良县图层/陆良县图层/Extract_tif11.tif'
image = gdal.Open(image_path)
print('image:', image)
img_width = image.RasterXSize  # 宽
img_height = image.RasterYSize  # 高
channel = image.RasterCount  # 波段数
print('img_width,img_height.channel:', img_width, img_height, channel)
img_geotrans = image.GetGeoTransform()  # 图像的坐标和分辨率信息等
print('img_geotrans:', img_geotrans)
img_proj = image.GetProjection()  # 图像的投影信息
print('img_proj:', img_proj)
img_data = image.ReadAsArray(0, 0, img_width, img_height)
print('遥感影像的shape：', img_data.shape)

# 问题
# MemoryError: Unable to allocate 44.6 GiB for an array with shape (3, 125940, 126756) and data type uint8

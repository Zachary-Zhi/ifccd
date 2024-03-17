#from applications.algorithms.GPS_georeference.osgeo import gdal
from osgeo import gdal


def copy_geoCoordSys(img_pos_path, img_none_path):
    '''
    获取img_pos坐标，并赋值给img_none
    :param img_pos_path: 带有坐标的图像
    :param img_none_path: 不带坐标的图像
    :return:
    '''

    def def_geoCoordSys(read_path, img_transf, img_proj):
        array_dataset = gdal.Open(read_path)
        img_array = array_dataset.ReadAsArray(0, 0, array_dataset.RasterXSize, array_dataset.RasterYSize)
        if 'int8' in img_array.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in img_array.dtype.name:
            datatype = gdal.GDT_UInt16
        else:
            datatype = gdal.GDT_Float32

        if len(img_array.shape) == 3:
            img_bands, im_height, im_width = img_array.shape
        else:
            img_bands, (im_height, im_width) = 1, img_array.shape

        filename = read_path[:-4] + '1' + read_path[-4:]
        driver = gdal.GetDriverByName("GTiff")  # 创建文件驱动
        dataset = driver.Create(filename, im_width, im_height, img_bands, datatype)
        dataset.SetGeoTransform(img_transf)  # 写入仿射变换参数
        dataset.SetProjection(img_proj)  # 写入投影

        # 写入影像数据
        if img_bands == 1:
            dataset.GetRasterBand(1).WriteArray(img_array)
        else:
            for i in range(img_bands):
                dataset.GetRasterBand(i + 1).WriteArray(img_array[i])
        print(read_path, 'geoCoordSys get!')

    dataset = gdal.Open(img_pos_path)  # 打开文件
    img_pos_transf = dataset.GetGeoTransform()  # 仿射矩阵
    img_pos_proj = dataset.GetProjection()  # 地图投影信息
    def_geoCoordSys(img_none_path, img_pos_transf, img_pos_proj)


#copy_geoCoordSys("G:\\python_work\\ifccd0411\\applications\\algorithms\\IR\\IR1_1.tif", "G:\\python_work\\ifccd0411\\applications\\algorithms\\IR\\IR1_2.tif")



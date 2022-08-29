#Functions to reproject and merge predicted chips

from osgeo import gdal
import cv2
import os
import glob
import numpy as np
import shutil



def proj_pred(img_path, predicted_array, tmp_pred_path,multi=False):

    #Write the masked image file and convert array to boolean 0 to 1
    flist = sorted(glob.glob(img_path+"/*.tif"))       
    
    for i in range(len(flist)):
        
        #setup filenames
        fn = os.path.basename(flist[i][:-4])
        out_fn = fn+".tif"
        
        #create temp tif folder
        out_dir = os.path.join(tmp_pred_path,out_fn)
        os.makedirs(tmp_pred_path,exist_ok=True)
        
        #Get pred arrays
        if multi == True:
            arr_pred = np.argmax(predicted_array[i], axis=2)[:,:,np.newaxis]
            cv2.imwrite(out_dir,arr_pred)
            #Image.fromarray(arr_pred.astype('uint8')).save(out_dir)
        else:
            arr_pred = (predicted_array[i]>.3)*255
            arr_pred = np.squeeze(arr_pred,axis=2)
            Image.fromarray(arr_pred.astype('uint8')).save(out_dir) #fix for speed
        #print("Created " +str(out_fn) + " to ../pred folder")

        #Get geoinfo of original image chip
        dataset = gdal.Open(flist[i])
        projection   = dataset.GetProjection()
        geotransform = dataset.GetGeoTransform()
        dataset = None

        #Copy geoinfo to water mask
        dataset2 = gdal.Open(out_dir,gdal.GA_Update)
        dataset2.SetGeoTransform(geotransform)
        dataset2.SetProjection(projection)
        dataset2.GetProjection()
        dataset2 = None
        
        
def merge_masks(mask_path,out_path,img_path):
    #setup paths
    os.makedirs(out_path,exist_ok=True)

    mask_list = glob.glob(mask_path+"/*.tif") 
    img = os.path.basename(img_path)
    out_fn = os.path.join(out_path,img+"_mask.tif")


    # build virtual raster mosaic and create geotiff
    vrt = gdal.BuildVRT(f"{mask_path}/merged.vrt", mask_list)
    options_str = '-ot Byte -of GTiff' 
    gdal.Warp(out_fn, vrt, options=options_str)
    print('Created',img+'_mask in ../outputs folder')
    vrt = None

    #delete vrt and temporary masks folder
    #os.remove(f"{mask_path}/merged.vrt")
    shutil.rmtree(mask_path) 
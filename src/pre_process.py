import os
import pandas as pd
import open3d as o3d
import numpy as np
from tqdm import tqdm

def crop_filter(cloud, min_x: int, max_x: int, min_y: int, max_y: int, min_z: int, max_z: int):
    """
    Set X and Y ranges of cropping box 
    :param cloud: input point clouds
    :param min_x: minimal X 
    :param max_x: maximum X 
    :param min_y: minimal Y 
    :param max_y: Maximum Y 
    :param min_z: Minimal Z
    :param max_z: Maximum Z
    :return: in_box_cloud <--> point clouds inside the cropping box, out_box_cloud <--> point clouds outside the cropping box
    """
    points = np.asarray(cloud.points)

    ind = np.where((points[:, 0] >= min_x) & (points[:, 0] <= max_x) &
                   (points[:, 1] >= min_y) & (points[:, 1] <= max_y) &
                   (points[:, 2] >= min_z) & (points[:, 2] <= max_z))[0]

    inlier_cloud = cloud.select_by_index(ind)
    outlier_cloud = cloud.select_by_index(ind, invert=True)
    return inlier_cloud, outlier_cloud

if __name__ == '__main__':
    # read als and tls data
    pwd = '/Volumes/T7/'
    tls_path = os.path.join(pwd, 'Data', 'Sepilok', 'Ground_truth', 'details','TLS', 'ITs')
    als_path = os.path.join(pwd, 'Data', 'Sepilok', 'Ground_truth', 'ALS2020_xyzid.csv')
    outpath = os.path.join(pwd, 'Data', 'Sepilok', 'Ground_truth', 'details', 'tls_als(900_10_1.4)_check_ITs')
    tls_filelist = os.listdir(tls_path)
    for tls_file in tqdm(tls_filelist):
        if '._' in tls_file:
            continue
        print('filename is: ' + tls_file)
        tls_data = pd.read_csv(os.path.join(tls_path, tls_file))
        als_data = pd.read_csv(als_path)
        als_data_arr = np.array(als_data[['X','Y','Z']])
        tls_data_arr = np.array(tls_data[['X','Y','Z']])
        # define o3d point clouds 
        # The RGB ranges from 0 to 1
        als_pcd = o3d.geometry.PointCloud()
        als_pcd.points = o3d.utility.Vector3dVector(als_data_arr)
        als_pcd.paint_uniform_color(np.asarray([0.75, 0.75, 0.75])) # als灰色 
        print("als point clouds:", als_pcd)
        tls_pcd = o3d.geometry.PointCloud()
        tls_pcd.points = o3d.utility.Vector3dVector(tls_data_arr)
        tls_pcd.paint_uniform_color(np.asarray([61/256,145/256,64/256])) # 绿色
        print("tls point clouds:", tls_pcd)
        '''
        o3d.visualization.draw_geometries([als_pcd, tls_pcd],
                                        window_name="原始点云",
                                        width=800, height=600)
        '''
        # get corner point by get_max_bound
        max_tls_pts, min_tls_pts = tls_pcd.get_max_bound(), tls_pcd.get_min_bound()
        max_als_pts, min_als_pts = als_pcd.get_max_bound(), als_pcd.get_min_bound()

        # extract Z from als
        z_min, z_max = max_als_pts[2], min_als_pts[2]
        # cropping area
        min_crop = [i - 10 for i in min_tls_pts] # [0:2]
        max_crop = [i + 10 for i in max_tls_pts] # [0:2]


        in_box_cloud, out_box_cloud = crop_filter(als_pcd,
                                                min_x=min_crop[0], max_x=max_crop[0],  
                                                min_y=min_crop[1], max_y=max_crop[1],
                                                min_z=min_crop[2], max_z=max_crop[2])

        in_box_cloud.paint_uniform_color(np.asarray([1, 0, 0]))
        out_box_cloud.paint_uniform_color(np.asarray([0.75, 0.75, 0.75]))
        print("in cropping point clouds:", in_box_cloud)
        #o3d.visualization.draw_geometries([tls_pcd, in_box_cloud, out_box_cloud],
        #                                window_name='裁剪出的点云',
        #                                width=800, height=600)
        outpts = pd.DataFrame(in_box_cloud.points, columns=['X','Y','Z'])
        outname = tls_file
        outpts.to_csv(os.path.join(outpath, outname))
        # o3d.io.write_point_cloud("ALS2020_cropped.ply", in_box_cloud)
        print('ok')
print('Complete....')

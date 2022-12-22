from copyreg import pickle
from curses import raw
import open3d as o3d
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from label_rgb_mapping import color_mapping
import pickle

class ALS_Label:
    def __init__(self, pwd) -> None:
        self.pwd = pwd #'/home/yc547/Wytham/'
        # these variables are used before labelling
        self.als_xyz_df = None
        self.tls_xyzid_df =None
        # the variable is used to store object
        self.c_m_obj = None
        # these variables are used to store labelled als data
        self.als_rgb_df_afterLabel = None
        self.als_xyz_df_afterLabel = None
        # key parameters
        self.nn = 300 # the number of neighbours
        self.max_radius = float(3)  # searching raidus
        self.max_pts_diff = 5 # stopping criteria: the number of newly labelled points 
        
    def unifyFormat(self, raw_als_path, raw_tls_path):
        if raw_tls_path:
            # reformating TLS data
            raw_tls = pd.read_csv(raw_tls_path, sep=' ', header=None)
            tls_xyzid_df = pd.DataFrame()
            tls_xyzid_df[['X','Y','Z']] = raw_tls[[0,1,2]]
            tls_xyzid_df['ID'] = raw_tls[4]
            # global shift to unify coordinate system
            tls_xyzid_df['X'] = tls_xyzid_df['X'] + 445900
            tls_xyzid_df['Y'] = tls_xyzid_df['Y'] + 209000
            print('unify TLS format complete...')
        if raw_als_path:
            # reformating ALS data
            raw_als = pd.read_csv(raw_als_path, sep=' ')
            als_xyzid_df = raw_als[['X','Y','Z']]
            als_xyzid_df['ID'] = [0] * len(als_xyzid_df)
            self.als_xyz_df = als_xyzid_df
            self.tls_xyzid_df = tls_xyzid_df
            print('unify ALS format complete...')

    def alsLabel(self):
        tls_arr = np.array(self.tls_xyzid_df[['X','Y','Z','ID']])
        tls_arr_xyz = tls_arr[:, 0:3]
        tls_label = tls_arr[:,3]
        # the labels for als data shold be [0] as there is no label for raw als data
        als_arr = np.array(self.als_xyz_df[['X','Y','Z','ID']])
        als_arr_xyz = als_arr[:, 0:3]
        als_label = als_arr[:, 3]
        # combine ALS and TLS
        als_tls_xyz = np.vstack((als_arr_xyz, tls_arr_xyz))
        als_tls_label = np.hstack((als_label, tls_label))
        # create random rgb from label
        c_m = color_mapping()
        self.c_m_obj = c_m
        als_tls_rgb_arr = c_m.label_rgb_mapping(als_tls_label)
        # np.array -> o3d.pointcloud
        tls_pcd = o3d.geometry.PointCloud()
        tls_pcd.points = o3d.utility.Vector3dVector(tls_arr_xyz)
        als_pcd = o3d.geometry.PointCloud()
        als_pcd.points = o3d.utility.Vector3dVector(als_arr_xyz)
        als_tls_pcd = o3d.geometry.PointCloud()
        als_tls_pcd.points = o3d.utility.Vector3dVector(als_tls_xyz)
        als_tls_pcd.colors = o3d.utility.Vector3dVector(als_tls_rgb_arr)
        als_len = len(als_arr_xyz)
        new_als_len = 0
        out_als_xyz_arr = np.empty((0, 3))
        out_als_rgb_arr = np.empty((0, 3))
        out_zero_xyz_arr = np.empty((0, 3))
        out_zero_rgb_arr = np.empty((0, 3))
        while True:
            zero_rgb_tuples_index_arr = []
            # Build KDTree
            print("Starting a New Loop...")
            print("Building kdtree...")
            pcd_tree = o3d.geometry.KDTreeFlann(als_tls_pcd)
            for i in tqdm(range(0, als_len)):
                compare_dic = {}
                [k, idx, _] = pcd_tree.search_hybrid_vector_3d(als_tls_pcd.points[i], 
                                                            radius=self.max_radius,
                                                            max_nn=self.nn)
                n_thres = self.nn/5
                if (k-1) < 2:
                    als_tls_pcd.colors[i] = (0,0,0)
                for idx_i in idx:
                    # recording the frequency of rgb cooridinate
                    nn_rgb = als_tls_pcd.colors[idx_i]
                    nn_rgb = tuple(nn_rgb)
                    if nn_rgb not in compare_dic:
                        compare_dic[nn_rgb] = 1
                    else:
                        compare_dic[nn_rgb] += 1
                [max_freq, target_rgb] = max(zip(compare_dic.values(), compare_dic.keys()))
                # 最终这里要把多数点集的rgb重新赋值给中心点
                target_rgb_arr = np.array(list(target_rgb))
                als_tls_pcd.colors[i] = target_rgb_arr
            # 以下思路为：区分已经标记和未标记的所有ALS点,并重构pcd，下次建树只针对未标记点来操作
            tmp_tls_rgb_arr = np.asarray(als_tls_pcd.colors)[als_len::] 
            tmp_als_pcd = o3d.geometry.PointCloud()
            tmp_als_xyz_arr = np.asarray(als_tls_pcd.points)[0:als_len]
            tmp_als_rgb_arr = np.asarray(als_tls_pcd.colors)[0:als_len]
            tmp_als_pcd.points = o3d.utility.Vector3dVector(tmp_als_xyz_arr)
            tmp_als_pcd.colors = o3d.utility.Vector3dVector(tmp_als_rgb_arr)
            # print('Visualize the point clouds....')
            # o3d.visualization.draw_geometries([tmp_als_pcd])
            # Select indice positions with rgb equals (0,0,0)
            zero_tuples_index, non_zero_tuples_index = [], []
            for i in tqdm(range(len(tmp_als_rgb_arr))):
                if tmp_als_rgb_arr[i].all() == 0:
                    zero_tuples_index.append(i)
                else:
                    non_zero_tuples_index.append(i)
            zero_rgb_arr = tmp_als_rgb_arr[zero_tuples_index,]
            zero_xyz_arr = tmp_als_xyz_arr[zero_tuples_index,]
            nonzero_rgb_arr = tmp_als_rgb_arr[non_zero_tuples_index,]
            nonzero_xyz_arr = tmp_als_xyz_arr[non_zero_tuples_index,]
            print('ok')
            # Export successfully labelled ALS point clouds and their label values
            out_als_xyz_arr = np.vstack((out_als_xyz_arr, nonzero_xyz_arr))
            out_als_rgb_arr = np.vstack((out_als_rgb_arr, nonzero_rgb_arr))
            # Stopping criterion: the number of newly labelled points is greater than threshold or not
            diff = len(nonzero_xyz_arr)
            if diff < self.max_pts_diff:
                out_zero_xyz_arr = zero_xyz_arr
                out_zero_rgb_arr = zero_rgb_arr
                print('The difference is: ' + str(diff) + ' ,smaller than ' + str(self.max_pts_diff) + ' ,loop breaks...')
                break
            else:
                print('The difference is: ' + str(diff) + ' ,greater than ' + str(self.max_pts_diff) + ' ,loop continues...')
                # Reconstruct data with unlabelled ALS point clouds and TLS point clouds
                als_tls_pcd = o3d.geometry.PointCloud()
                loop_als_tls_xyz_arr = np.vstack((zero_xyz_arr, tls_arr_xyz))
                loop_als_tls_rgb_arr = np.vstack((zero_rgb_arr, tmp_tls_rgb_arr))
                als_tls_pcd.points = o3d.utility.Vector3dVector(loop_als_tls_xyz_arr)
                als_tls_pcd.colors = o3d.utility.Vector3dVector(loop_als_tls_rgb_arr)
                als_len = len(zero_xyz_arr)
        print('Re-colorization finished.') 
        final_als_xyz_arr = np.vstack((out_als_xyz_arr, out_zero_xyz_arr))
        final_als_rgb_arr = np.vstack((out_als_rgb_arr, out_zero_rgb_arr))
        final_als_xyz_df = pd.DataFrame(final_als_xyz_arr, columns=['X','Y','Z'])
        final_als_rgb_df = pd.DataFrame(final_als_rgb_arr, columns=['R','G','B'])
        self.als_xyz_df_afterLabel = final_als_xyz_df
        self.als_rgb_df_afterLabel = final_als_rgb_df
        print('Visualize final results...')
        final_als_pcd = o3d.geometry.PointCloud()
        final_als_pcd.points = o3d.utility.Vector3dVector(final_als_xyz_arr)
        final_als_pcd.colors = o3d.utility.Vector3dVector(final_als_rgb_arr)
        figname = 'als_refinement_nn=' + str(self.nn) + ' & radius=' + str(self.max_radius)
        o3d.visualization.draw_geometries([final_als_pcd], window_name = figname)
        print('Labelling Process finished...')

    def postProcess(self):
        rgb_arr = np.array(self.als_rgb_df_afterLabel[['R','G','B']])
        re_assgin_label = self.c_m_obj.rgb_label_mapping(re_assign_rgb=rgb_arr, dic_map=self.c_m_obj.label_rgb_mapdic)
        self.als_xyz_df_afterLabel['ID'] = re_assgin_label[0:len(self.als_xyz_df)]
        filename = 'wytham_als_' + str(self.nn) + '_' + str(self.max_radius) + '.csv'
        outpath = os.path.join(self.pwd, 'ALS_labelling_process', filename)
        self.als_xyz_df_afterLabel.to_csv(outpath)
        print('RGB-label vals mapping Finished...')


import random
from tqdm import tqdm
import numpy as np


class color_mapping(object):
    # color_mapping class aims to realize mapping from label to (r,g,b) and (r,g,b) to label
    # input: np.array of label like np.array([1,2,3,4,5])
    # output: (n, 3) np.array RGB value with a range from 0 to 1m like ([0,0,1],[0,1,0],...)
    
    def __init__(self):
        self.label_rgb_mapdic= {}
        self.rgb_label_mapdic = {}
        self.rgb_arr = None
        self.re_assign_rgb_arr = None
        self.label_uni = None
        
    def label_rgb_mapping(self, label_arr):
        print('start mapping point label to RGB value')
        self.label_uni = list(set(list(label_arr)))
        # Store mapping relation of RGB and label values with dictionary
        # self.label_rgb_mapdic = {}
        for label_uni_i in tqdm(self.label_uni):
            if label_uni_i == 0:
                min_max_rgb_i = [0, 0, 0]
            else:
                min_max_rgb_i = [random.randint(0,255)/255,random.randint(0,255)/255,random.randint(0,255)/255]
            self.label_rgb_mapdic[label_uni_i] = min_max_rgb_i
        rgb = []
        for label_i in tqdm(label_arr):
            rgb.append(self.label_rgb_mapdic[label_i])
        self.rgb_arr = np.array(rgb)
        print('Mapping finished')
        return self.rgb_arr

    def rgb_label_mapping(self, re_assign_rgb, dic_map):
        print('mapping back to label')
        self.rgb_label_mapdic = {tuple(value):key for key, value in dic_map.items()}
        label = []
        for rgb_i in tqdm(re_assign_rgb):
            label.append(self.rgb_label_mapdic[tuple(rgb_i)])
        re_assign_label_arr = np.array(label)
        return re_assign_label_arr

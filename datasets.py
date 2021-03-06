import numpy as np
import json
import pandas as pd
import math
from random import sample
import os
import cv2

path = '/home/austin/Datasets/HeROS_v2'
File = os.listdir(path)
save_path = '/home/austin/Datasets/FCN_Aff'

def json2label(idx,f):
    label = np.zeros((4, 224, 224))
    with open(idx,"r") as F:
        data = json.load(F)
        points_list = pd.DataFrame(data['shapes'])
        id = int(points_list.shape[0]/2)

        sample = points_list['points'][id]

        x = sample[0][0] - sample[1][0]
        y = sample[0][1] - sample[1][1]

        if y > 0:
            x = -x
        y = abs(y)
        
        theta = math.degrees(math.atan2(y, x))
        '''
            0 -> grasp, -90
            1 -> grasp, -45
            2 -> grasp, 0
            3 -> grasp, 45
        '''

        if (theta < 22.5) or (theta > 157.5):
            theta = 2
        elif (theta >= 22.5) and (theta < 67.5):
            theta = 3
        elif (theta >= 67.5) and (theta < 112.5):
            theta = 0
        else:
            theta = 1

        for idx in data['shapes']:
            p = idx['points']
            cv2.line(label[theta], (int(p[0][0]), int(p[0][1])), (int(p[1][0]), int(p[1][1])), 255,2)

        return label, theta
        

count = 0
angle_class_count = [0,0,0,0]
for folder in File:
    ele_color = os.listdir(path+'/'+folder+'/color')
    ele_color.sort()
    ele_depth = os.listdir(path+'/'+folder+'/depth')
    ele_depth.sort()

    if len(ele_color) == 3:
        Label, Theta = json2label(path+'/'+folder+'/color/'+ele_color[1], folder)
        angle_class_count[Theta] += 1

        color = cv2.imread(path+'/'+folder+'/color/'+ele_color[0])

        depth = np.load(path+'/'+folder+'/depth/'+ele_depth[0])
        depth[depth > 1000] = 0

        cv2.imwrite(save_path+'/color/color_'+str(count)+'.jpg', color)
        np.save(save_path+'/depth/depth_'+str(count), depth)
        np.save(save_path+'/label/label_'+str(count), Label)

        f = open(save_path+'/idx/id_'+str(count)+'.txt', "a")
        f.write(str(Theta)+'\n')
        f.close()

        count += 1

print(angle_class_count)

# create data list for training and testing
data_list = os.listdir(save_path+'/color')
test = sample(data_list, int(len(data_list)*0.05))
train = list(set(data_list).difference(set(test)))

f = open(save_path+'/train.txt', "a")
for name in train:
    f.write(name.split('_')[1].split('.')[0]+'\n')
f.close()

f = open(save_path+'/test.txt', "a")
for name in test:
    f.write(name.split('_')[1].split('.')[0]+'\n')
f.close()
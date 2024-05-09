import cv2
from albumentations import Compose, PadIfNeeded
# from transforms.albu import IsotropicResize
import numpy as np
import os
import cv2
import torch
from statistics import mean


# def transform_frame(image, image_size):
#     transform_pipeline = Compose([
#         IsotropicResize(max_side=image_size, interpolation_down=cv2.INTER_LINEAR, interpolation_up=cv2.INTER_LINEAR),
#         PadIfNeeded(min_height=image_size, min_width=image_size, border_mode=cv2.BORDER_REPLICATE)
#     ]
#     )
#     return transform_pipeline(image=image)['image']


def resize(image, image_size):
    try:
        return cv2.resize(image, dsize=(image_size, image_size))
    except:
        return []


def custom_round(values):
    result = []
    for value in values:
        if value > 0.55:
            result.append(1)
        else:
            result.append(0)
    return np.asarray(result)


def custom_video_round(preds):
    for pred_value in preds:
        if pred_value > 0.55:
            return pred_value
    return mean(preds)


def get_method(video, data_path):
    methods = os.listdir(os.path.join(data_path, "manipulated_sequences"))
    methods.extend(os.listdir(os.path.join(data_path, "original_sequences")))
    methods.append("DFDC")
    methods.append("Original")
    selected_method = ""
    for method in methods:
        if method in video:
            selected_method = method
            break
    return selected_method


#def shuffle_dataset(dataset):
#     import random
#     random.seed(4)
#     random.shuffle(dataset[0])
#     random.shuffle(dataset[1])
#     return dataset

def shuffle_dataset(dataset):
    import random
    random.seed(4)
    newdataset = [None for _ in range(len(dataset))]
    randIdx = list(range(len(dataset)))
    random.shuffle(randIdx)
    for img, ridx in zip(dataset, randIdx):
        newdataset[ridx] = img
    return newdataset #dataset

def create_label(dataset:list, DFcheckStr:str):
    labels = []
    for imgPath in dataset:
        if DFcheckStr in imgPath:
            labels.append(0) # 0 for forged image
        else: labels.append(1) # 1 for original image
    return np.asarray(labels)

def get_n_params(model):
    pp = 0
    for p in list(model.parameters()):
        nn = 1
        for s in list(p.size()):
            nn = nn * s
        pp += nn
    return pp


def check_correct(preds, labels):
    preds = preds.cpu()
    labels = labels.cpu()
    preds = [np.asarray(torch.sigmoid(pred).detach().numpy()).round() for pred in preds]

    correct = 0
    positive_class = 0
    negative_class = 0
    tp, fp, tn, fn = 0, 0, 0, 0
    for i in range(len(labels)):
        pred = int(preds[i])
        if labels[i] == pred:
            correct += 1
        if pred == 1:
            positive_class += 1
        else:
            negative_class += 1
        # tp, fp, tn, fn
        if (pred == 1) and (labels[i] == 1): tp += 1
        elif (pred == 1) and (labels[i] == 0): fp += 1
        elif (pred == 0) and (labels[i] == 0): tn += 1
        elif (pred == 0) and (labels[i] == 1): fn += 1

    return correct, positive_class, negative_class, (tp, fp, tn, fn)
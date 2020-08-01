# encoding: utf-8
"""
@author:  liaoxingyu
@contact: sherlockliao01@gmail.com
"""

import torchvision.transforms as T

from .transforms import *
from .autoaugment import *
from PIL import Image

def build_transforms(cfg, is_train=True):
    res = []

    if is_train:
        size_train = cfg.INPUT.SIZE_TRAIN

        # augmix augmentation
        do_augmix = cfg.INPUT.DO_AUGMIX

        # auto augmentation
        do_autoaug = cfg.INPUT.DO_AUTOAUG
        total_iter = cfg.SOLVER.MAX_ITER

        # horizontal filp
        do_flip = cfg.INPUT.DO_FLIP
        flip_prob = cfg.INPUT.FLIP_PROB

        # padding
        do_pad = cfg.INPUT.DO_PAD
        padding = cfg.INPUT.PADDING
        padding_mode = cfg.INPUT.PADDING_MODE

        # color jitter
        do_cj = cfg.INPUT.DO_CJ

        # random rotation
        do_rot = cfg.INPUT.DO_ROTATION

        # random erasing
        do_rea = cfg.INPUT.REA.ENABLED
        rea_prob = cfg.INPUT.REA.PROB
        rea_mean = cfg.INPUT.REA.MEAN
        # random patch
        do_rpt = cfg.INPUT.RPT.ENABLED
        rpt_prob = cfg.INPUT.RPT.PROB

        if do_autoaug:
            res.append(ImageNetPolicy(total_iter))
        res.append(T.Resize(size_train, interpolation=3))
        if do_rot:
            res.append(T.RandomRotation(180,resample=Image.BILINEAR)) 
        if do_flip:
            res.append(T.RandomHorizontalFlip(p=flip_prob))
        if do_pad:
            res.extend([T.Pad(padding, padding_mode=padding_mode),
                        T.RandomCrop(size_train)])
        if do_cj:
            res.append(T.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0))
        if do_augmix:
            res.append(AugMix())
        if do_rea:
            res.append(RandomErasing(probability=rea_prob, mean=rea_mean))
        if do_rpt:
            res.append(RandomPatch(prob_happen=rpt_prob))
    else:
        size_test = cfg.INPUT.SIZE_TEST
        res.append(T.Resize(size_test, interpolation=3))
    res.append(ToTensor())
    return T.Compose(res)

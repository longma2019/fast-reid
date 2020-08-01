import glob
import os.path as osp
# import re
import warnings

from .bases import ImageDataset
from ..datasets import DATASET_REGISTRY


@DATASET_REGISTRY.register()
class Fangdao_16stores(ImageDataset):
    dataset_dir = ''

    def __init__(self, root='datasets', **kwargs):

        # data_dir = "/data/ywu/fangdao/samples_attributes_4/client/"
        data_dir = "/home/ywu/projects/download_track/samples_attributes_4/client/"
        
        cam_info = {'100000027':{'pos':['ee:bb:03:01:00:c3', 'ee:bb:03:01:02:98'], 'door': ['ee:ee:bb:03:10:05']},#位置重复  保留05
            '100001071':{'pos':['ee:bb:03:01:00:b2', 'ee:bb:03:01:03:37', 'ee:bb:03:01:02:93'], 'door': ['ee:bb:03:01:02:ad']},
            '100000159':{'pos':['ee:bb:03:01:00:e7', 'ee:bb:03:01:02:40'], 'door': ['ee:bb:03:01:01:c6']},
            '100001093':{'pos':['ee:bb:03:01:03:9a', 'ee:bb:03:01:03:31', 'ee:bb:03:01:02:1b', 'ee:bb:03:01:03:25', 'ee:bb:03:01:00:ce', 'ee:bb:03:01:03:05', 'ee:bb:03:01:03:93'], 'door': ['ee:bb:03:01:02:b3', 'ee:bb:03:01:02:00']},
            '100001082':{'pos':['ee:bb:03:01:01:13', 'ee:bb:03:01:03:71', 'ee:bb:03:01:01:cf'], 'door': []}}

        self.dataset_dir = data_dir

        # fname_list = os.listdir(data_dir)
        val_dataname = '100000027_2020-03-17'
        # val_dataname = '100001071_2020-02-18'

        val_storeid = val_dataname.split('_')[0]
        query_cam = cam_info[val_storeid]['pos']
        query_cam = [x.replace(':', '-') for x in query_cam]

        # self.train_dir = osp.join(self.dataset_dir, 'train')
        # self.query_dir = osp.join(self.dataset_dir, 'query')
        # self.gallery_dir = osp.join(self.dataset_dir, 'gallery')

        train, query, gallery = self.split_samples(data_dir, val_dataname, query_cam)
        # query = self._process_dir(self.query_dir, relabel=False)
        # gallery = self._process_dir(self.gallery_dir, relabel=False)

        # if verbose:
        #     print("=> Fangdao_Fullbody loaded from {}".format(data_dir))
        #     self.print_dataset_statistics(train, query, gallery)

        self.train = train
        self.query = query
        self.gallery = gallery

        # self.num_train_pids, self.num_train_imgs, self.num_train_cams = self.get_imagedata_info(self.train)
        # self.num_query_pids, self.num_query_imgs, self.num_query_cams = self.get_imagedata_info(self.query)
        # self.num_gallery_pids, self.num_gallery_imgs, self.num_gallery_cams = self.get_imagedata_info(self.gallery)

        super(Fangdao_16stores, self).__init__(train, query, gallery, **kwargs)

    def split_samples(self, data_dir, val_dataname, query_cam):
        # data_dir_2 = '/data/ywu/fangdao/samples_attributes_2/client'
        # data_dir_val = '/data/ywu/fangdao/samples_attributes_3/client'
        data_dir_val = '/home/ywu/projects/download_track/samples_attributes_3/client'
        # pdb.set_trace()
        img_paths = glob.glob(osp.join(data_dir, '*.jpg'))
        # img_paths += glob.glob(osp.join(data_dir_2, '*.jpg'))
        img_paths_val = glob.glob(osp.join(data_dir_val, '*.jpg'))
        print('img_paths_val: ', len(img_paths_val))
        img_paths_val = [x for x in img_paths_val if val_dataname in x]
        print('img_paths_val: ', len(img_paths_val))
        # exit()
        img_paths += img_paths_val
        # fname_list = os.listdir(data_dir)

        # if 'train' in data_dir.split('/'):
        #     print('before extra: ', len(img_paths))
        #     img_paths+=glob.glob(osp.join(self.dataset_dir, 'train_extra', '*.jpg'))
        #     # img_paths+=glob.glob(osp.join(self.dataset_dir, '100001071_2019-12-18_cleaned', '*.jpg'))
        #     print('after extra: ', len(img_paths))
        # pattern = re.compile(r'([-\d]+)_c(\d)')
        pid_info = {}
        cid_info = {}
        pid_container = set()
        pid_train_container = set()
        cid_container = set()
        for fname_path in img_paths:
            fname = fname_path.split('/')[-1]
            str_info = fname.split('#')
            pid = '#'.join(str_info[:2])
            cid = str_info[-1].split('_')[0]
            if pid not in pid_info.keys():
                pid_info[pid] = []
                cid_info[pid] = []
            pid_info[pid].append(fname_path)
            cid_info[pid].append(cid)
            pid_container.add(pid)
            if val_dataname not in pid:
                pid_train_container.add(pid)
            cid_container.add(cid)

        # for pid, fname_set in pid_info.items():


        # pid_container = set()
        # cid_container = set()
        # for img_path in img_paths:
        #     # print(img_path)
        #     pid = int(img_path.split('/')[-1].split('_')[0])
        #     cid = img_path.split('/')[-1].split('_')[1]
        #     if pid == -1:
        #         continue # junk images are just ignored
        #     pid_container.add(pid)
        #     cid_container.add(cid)
        pid2label = {pid:label for label, pid in enumerate(pid_container)}
        pid2label_train = {pid:label for label, pid in enumerate(pid_train_container)}
        cid2label = {cid:label for label, cid in enumerate(cid_container)}

        # pdb.set_trace()
        train, query, gallery = [], [], []

        for pid, fname_set in pid_info.items():
            # pid2 = pid2label[pid]
            for i in range(len(fname_set)):
                img_path = fname_set[i] # osp.join(data_dir, fname_set[i])
                camid = cid_info[pid][i]
                camid2 = cid2label[camid]
                if val_dataname not in pid: # training
                    train.append((img_path, pid2label_train[pid], camid2))
                else:
                    if camid in query_cam:
                        # query.append((img_path, pid, camid2))
                        query.append((img_path, pid2label[pid], camid2))
                    else:
                        gallery.append((img_path, pid2label[pid], camid2))


        # for img_path in img_paths:
        #     pid, camid = img_path.split('/')[-1].split('_')[:2]
        #     pid = int(pid)
        #     if pid == -1:
        #         continue # junk images are just ignored
        #     # assert 0 <= pid <= 1501  # pid == 0 means background
        #     # assert 1 <= camid <= 6
        #     # camid -= 1 # index starts from 0
        #     camid = cid2label[camid]
        #     if relabel:
        #         pid = pid2label[pid]
                
        #     data.append((img_path, pid, camid))
        # pdb.set_trace()
        return train, query, gallery
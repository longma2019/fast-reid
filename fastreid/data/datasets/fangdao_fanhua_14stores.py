import os.path as osp
import glob
import re
import os
import pdb
import json
from collections import defaultdict

import warnings

from .bases import ImageDataset
from ..datasets import DATASET_REGISTRY

def get_pid_info(trackid_associated_list):
    # pair_set = [x.split(' ') for x in info_match]
    # print('pair_set', pair_set[0:3])
    pair_0 = [k for k, v in trackid_associated_list.items() if len(v)>0]
    pair_1 = [v for k, v in trackid_associated_list.items() if len(v)>0]

    track_set = list(trackid_associated_list.keys())

    info_track = defaultdict(list)
    id_map = {}
    id = 0
    for i in range(len(pair_0)):
        # if pair_0[i] == '2019-11-26_07-50-24-562_ee_bb_03_01_00_e7':
        #     print(i, pair_1[i])
        # if id==221:
        #     aaaa=2
        if pair_0[i] not in id_map.keys() and pair_1[i] not in id_map.keys():
            id_map[pair_0[i]] = id
            id_map[pair_1[i]] = id
            info_track[id] += [pair_0[i], pair_1[i]]
            id+=1
        elif pair_1[i] not in id_map.keys():
            id_map[pair_1[i]] = id_map[pair_0[i]]
            info_track[id_map[pair_1[i]]].append(pair_1[i])
        elif pair_0[i] not in id_map.keys():
            id_map[pair_0[i]] = id_map[pair_1[i]]
            info_track[id_map[pair_0[i]]].append(pair_0[i])
        else:
            id_0 = id_map[pair_0[i]]
            id_1 = id_map[pair_1[i]]
            if id_0 != id_1:
                # print('hi')
                info_track[id_0] += info_track[id_1]
                for trackid in info_track[id_1]:
                    id_map[trackid] = id_0
                info_track.pop(id_1, None)

    # print('number of IDs after merge', len(info_track))

    for trackid in track_set:
        if trackid not in id_map.keys():
            id_map[trackid] = id
            info_track[id] = [trackid]
            id+=1
    # print('number of IDs', len(set(id_map.values())))

    data_info = {}
    data_info['tracklet_pids'] = id_map
    data_info['pid_info'] = info_track

    return data_info

def get_one_sample_list(data_name, data_path, anno_info, track_info, remove_info):

    samples_all = {}

    trackid_associated_list = anno_info['trackid_associated_list']
    category_list = anno_info['category_list']

    for track_id, _ in category_list.items():
        if track_id not in trackid_associated_list.keys():
            trackid_associated_list[track_id] = []
    # print(data_name, '#track in anno:', len(category_list))

    frame_set_selected_list = {}
    for track_id, track in track_info.items():
        frame_set_selected_list[track_id] = list(track['frame_info'].keys())

    data_info = get_pid_info(trackid_associated_list)

    pid_info = data_info['pid_info']

    tid_shown = []
    pid_shown = []
    fname_shown = []
    img_set = []
    count = 0
    # print(data_name)
    for pid, tid_list in pid_info.items():
        # print(data_name, pid)
        pid_t = '{}#{}'.format(data_name,pid)
        # pid_container.add(pid_t)
        for tid in tid_list:
            track = track_info[tid]
            att = category_list[tid]
            if att != 'client':
                continue
            # print(tid)
            # save_path_att = '{}/{}'.format(save_path, att)
            # if not os.path.exists(save_path_att):
            #     os.mkdir(save_path_att)
            # cid = '{}#{}'.format(data_name, tid.split('_')[2])
            cid = tid.split('_')[2]
            # cid_container.add(cid)
            for fname in frame_set_selected_list[tid]:
                # if 'bodyBboxOfCurrent' not in track['frame_info'][fname].keys():
                #     continue
                # bodyBboxOfCurrent = track['frame_info'][fname]['bodyBboxOfCurrent']
                # samples_all.append((os.path.join(data_path, tid, fname+'.jpg'), pid_t, cid))

                # samples_all.append(os.path.join(data_path, tid, fname+'.jpg'))
                # print(fname)

                if '{}#{}.jpg'.format(tid, fname) in remove_info:
                    continue 

                samples_all[fname] = {'img_path': os.path.join(data_path, tid, fname+'.jpg'), 'pid': pid_t, 'cid': cid}
                    # shutil.copyfile(os.path.join(data_path, tid, fname+'.jpg'), os.path.join(save_path_att, '{}#{}#{}#{}.jpg'.format(data_name,pid,tid,fname)))
    # print('finished!!!!!!!!')
    return samples_all


def get_samples(data_root, remove_path, info_path, data_name_set, path_anno):
    samples_all = {}
    for data_name in data_name_set:
        data_path = '{}/{}'.format(data_root, data_name)
        remove_fname = '{}/{}.txt'.format(remove_path, data_name)

        with open('{}/{}_anno.json'.format(path_anno, data_name), 'r') as f:
            anno_info = json.load(f)

        with open('{}/{}.json'.format(info_path, data_name), 'r') as f:
            track_info = json.load(f)
        remove_info = []
        if os.path.exists(remove_fname):
            with open(remove_fname) as f:
                remove_info = f.read().splitlines()

        sample_one = get_one_sample_list(data_name, data_path, anno_info, track_info, remove_info)

        samples_all.update(sample_one)

    return samples_all

def get_samples_val(data_path_val, data_name, path_anno):

    data_path = '{}/{}'.format(data_path_val, data_name)
    remove_fname = '/hddc/ywu/data/blf/reid/sample_remove_list/{}.txt'.format(data_name)

    with open('{}/{}_anno.json'.format(path_anno, data_name), 'r') as f:
        anno_info = json.load(f)

    with open('/hddc/ywu/data/blf/reid/track_info/{}.json'.format(data_name), 'r') as f:
        track_info = json.load(f)
    remove_info = []
    if os.path.exists(remove_fname):
        with open(remove_fname) as f:
            remove_info = f.read().splitlines()

    sample_one = get_one_sample_list(data_name, data_path, anno_info, track_info, remove_info)

    return sample_one

def get_pid_cid(samples):
    pid_container = set()
    cid_container = set()
    for k, info in samples.items():
        
        pid_container.add(info['pid'])
        cid_container.add(info['cid'])

    return pid_container, cid_container


def get_all_sample(val_dataname, query_cam):
    date = '2020-06-25'
    data_name_set = ['100000058', '100000078', '100000181', '100000199', '100000225', '100000228', '100000282', '100000298', '100000327', '100003003', '100019002', '123000086', '123000155', '123001073']
    data_name_set = ['{}_{}'.format(x,date) for x in data_name_set]

    # val_dataname = '100000027_2020-03-17'
    data_root = '/hddc/ywu/data/blf/reid/2020-06-25'
    info_path = '/hddc/ywu/data/blf/reid/track_info'
    remove_path = '/hddc/ywu/data/blf/reid/sample_remove_list'

    data_root_val = '/hddc/ywu/data/blf/reid'

    path_anno = '/hddc/ywu/data/blf/reid/annotation'

    pid_container = set()
    pid_train_container = set()
    cid_container = set()

    # samples_train = get_samples_train(data_name_set, path_anno)
    # samples_val = get_samples_val(data_path_val, val_dataname, path_anno)
    samples_train = get_samples(data_root, remove_path, info_path, data_name_set, path_anno)#get_samples(data_name_set, path_anno)
    samples_val = get_samples(data_root_val, remove_path, info_path, val_dataname, path_anno)

    pid_train_container, cid_container = get_pid_cid(samples_train)

    pid2label_train = {pid:label for label, pid in enumerate(pid_train_container)}
    cid2label = {cid:label for label, cid in enumerate(cid_container)}

    train, query, gallery = [], [], []

    for k, sample_info in samples_train.items():
        img_path = sample_info['img_path']
        pid = sample_info['pid']
        cid = sample_info['cid']
        train.append((img_path, pid2label_train[pid], cid2label[cid]))

    pid_container_val, cid_container_val = get_pid_cid(samples_val)
    pid2label_val = {pid:label for label, pid in enumerate(pid_container_val)}
    cid2label_val = {cid:label for label, cid in enumerate(cid_container_val)}
    for k, sample_info in samples_val.items():
        img_path = sample_info['img_path']
        pid = sample_info['pid']
        cid = sample_info['cid']
        # print(cid, query_cam)
        # pdb.set_trace()
        # train.append((img_path, pid2label_train[pid], cid2label[cid]))
        if cid in query_cam:
            query.append((img_path, pid2label_val[pid], cid2label_val[cid]))
        else:
            gallery.append((img_path, pid2label_val[pid], cid2label_val[cid]))


    return train, query, gallery

@DATASET_REGISTRY.register()
class Fangdao_Fanhua_14stores(ImageDataset):
    dataset_dir = ''
    def __init__(self, root='datasets', **kwargs):

        cam_info = {'100000027':{'pos':['ee:bb:03:01:00:c3', 'ee:bb:03:01:02:98'], 'door': ['ee:ee:bb:03:10:05']},#位置重复  保留05
            '100001071':{'pos':['ee:bb:03:01:00:b2', 'ee:bb:03:01:03:37', 'ee:bb:03:01:02:93'], 'door': ['ee:bb:03:01:02:ad']},
            '100000159':{'pos':['ee:bb:03:01:00:e7', 'ee:bb:03:01:02:40'], 'door': ['ee:bb:03:01:01:c6']},
            '100001093':{'pos':['ee:bb:03:01:03:9a', 'ee:bb:03:01:03:31', 'ee:bb:03:01:02:1b', 'ee:bb:03:01:03:25', 'ee:bb:03:01:00:ce', 'ee:bb:03:01:03:05', 'ee:bb:03:01:03:93'], 'door': ['ee:bb:03:01:02:b3', 'ee:bb:03:01:02:00']},
            '100001082':{'pos':['ee:bb:03:01:01:13', 'ee:bb:03:01:03:71', 'ee:bb:03:01:01:cf'], 'door': []}}
            
        # self.dataset_dir = data_dir

        # fname_list = os.listdir(data_dir)
        val_dataname = ['100000027_2020-03-17']
        # val_dataname = '100001071_2020-02-18'

        query_cam = []
        for name in val_dataname:
            val_storeid = name.split('_')[0]
            query_cam += cam_info[val_storeid]['pos']
        query_cam = [x.replace(':', '-') for x in query_cam]

        train, query, gallery = get_all_sample(val_dataname, query_cam)

        # pdb.set_trace()

        self.train = train
        self.query = query
        self.gallery = gallery

        super(Fangdao_Fanhua_14stores, self).__init__(train, query, gallery, **kwargs)

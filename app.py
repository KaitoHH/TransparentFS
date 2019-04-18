from flask import Flask, render_template
from fs.TFS import TFS
from fs.NormalFS import NormalFS
import random

from faker import Faker
from flask import Flask
from flask import request, jsonify
from fs.client import BatchFSWrapper
import os
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

import config
from fs.NormalFS import NormalFS
from fs.TFS import TFS
from fs.client import BatchFSWrapper

app = Flask(__name__)
tfs_1 = TFS()


@app.route('/')
def index():
    return render_template('ads_demo.html')


@app.route('/1', methods=['POST'])
def demo1():
    json = request.json
    f = tfs_1.__getattribute__(json['method'])
    ret = f(**json['args'])
    return jsonify({'ret': ret, 'bitmap': tfs_1.bitmap, 'file_list': tfs_1.to_json(tfs_1.file_list)})


@app.route('/1/init')
def demo1_init():
    global tfs_1
    tfs_1 = TFS()
    return jsonify({'bitmap': tfs_1.bitmap, 'file_list': tfs_1.to_json(tfs_1.file_list)})


@app.route('/2')
def demo2():
    tfs = TFS()
    nfs = NormalFS()
    fake = Faker()
    normal_set, contrib_set, all_set = set(), set(), set()
    fs = BatchFSWrapper([nfs, tfs])
    weight = [1] * 3 + [2] * 2 + [3] * 0 + [4] + [5] + [6]
    bitmap_hist = []
    for _ in range(150):
        change = False
        ins = random.choice(weight)
        tfs_old = tfs.bitmap.copy()
        nfs_old = nfs.bitmap.copy()
        if ins == 1:
            name = fake.file_name()
            while name in all_set:
                name = fake.file_name()
            try:
                fs.add_normal_file(name, random.randint(1, 5))
                normal_set.add(name)
                all_set.add(name)
                change = True
            except LookupError:
                continue
        elif ins == 2:
            name = fake.file_name()
            while name in all_set:
                name = fake.file_name()
            try:
                fs.add_contrib_file(name, random.randint(1, 5))
                contrib_set.add(name)
                all_set.add(name)
                change = True
            except LookupError:
                continue
        elif ins == 3:
            if len(normal_set):
                file = random.choice(list(normal_set))
                fs.stat_normal_file(file)
                change = True
        elif ins == 4:
            if len(contrib_set):
                file = random.choice(list(contrib_set))
                fs.stat_contrib_file(file)
                change = True
        elif ins == 5:
            if len(normal_set):
                file = random.choice(list(normal_set))
                fs.delete_normal_file(file)
                normal_set.remove(file)
                all_set.remove(file)
                change = True
        elif ins == 6:
            if len(contrib_set):
                file = random.choice(list(contrib_set))
                fs.delete_contrib_file(file)
                contrib_set.remove(file)
                all_set.remove(file)
                change = True
        if change:
            bitmap_hist.append(
                {'event': config.global_event_recorder, 'tfs_diff': tfs.bitmap_diff(tfs_old, tfs.bitmap),
                 'nfs_diff': nfs.bitmap_diff(nfs_old, nfs.bitmap)})

    tfs_old = tfs.bitmap.copy()
    nfs_old = nfs.bitmap.copy()
    for file in list(contrib_set):
        fs.delete_contrib_file(file)
    bitmap_hist.append(
        {'event': 'delete all', 'tfs_diff': tfs.bitmap_diff(tfs_old, tfs.bitmap),
         'nfs_diff': nfs.bitmap_diff(nfs_old, nfs.bitmap)})

    return jsonify({'items': bitmap_hist})

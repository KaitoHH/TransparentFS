import os
import random

from faker import Faker
from flask import Flask
from flask import render_template
from flask import request, jsonify, session

import config
import jsonpickle
from fs.NormalFS import NormalFS
from fs.TFS import TFS
from fs.client import BatchFSWrapper

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

fake = Faker()
app = Flask(__name__)
app.config['SECRET_KEY'] = fake.uuid4()


def get_session_tfs():
    tfs = session.get('tfs', None)
    if tfs:
        tfs = jsonpickle.decode(tfs)
    else:
        tfs = TFS()
    return tfs


@app.route('/')
def index():
    return render_template('ads_demo.html')


@app.route('/1', methods=['POST'])
def demo1():
    tfs = get_session_tfs()
    json = request.json
    f = tfs.__getattribute__(json['method'])
    ret = f(**json['args'])
    session['tfs'] = jsonpickle.encode(tfs)
    return jsonify({'ret': ret, 'bitmap': tfs.bitmap, 'file_list': tfs.to_json(tfs.file_list)})


@app.route('/1/init', methods=['GET'])
def demo1_init():
    tfs = get_session_tfs()
    return jsonify({'ret': None, 'bitmap': tfs.bitmap, 'file_list': tfs.to_json(tfs.file_list)})


@app.route('/2')
def demo2():
    rate = float(request.args.get('rate', 1.5))
    tfs = TFS()
    nfs = NormalFS()
    normal_set, contrib_set, all_set = set(), set(), set()
    fs = BatchFSWrapper([nfs, tfs])
    weight = [1] * int(10 * rate) + [2] * 10 + [3] * 0 + [4] * 5 + [5] * int(5 * rate) + [6] * 5
    bitmap_hist = []
    for _ in range(300):
        change = False
        ins = random.choice(weight)
        tfs_old = tfs.bitmap.copy()
        nfs_old = nfs.bitmap.copy()
        if ins == 1:
            name = fake.file_name()
            while name in all_set:
                name = fake.file_name()
            try:
                fs.add_normal_file(name, int(max(0, random.gauss(8, 4))))
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
                fs.add_contrib_file(name, int(max(0, random.gauss(6, 3))))
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

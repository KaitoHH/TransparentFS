from flask import Flask
from TFS import TFS
from NormalFS import NormalFS
from flask import request, jsonify
from client import BatchFSWrapper
import random
from faker import Faker

app = Flask(__name__)
tfs_1 = TFS()


@app.route('/1', methods=['POST'])
def demo1():
    json = request.json
    f = tfs_1.__getattribute__(json['method'])
    ret = f(**json['args'])
    return jsonify({'ret': ret, 'bitmap': tfs_1.bitmap, 'file_list': tfs_1.to_json(tfs_1.file_list)})


@app.route('/2')
def demo2():
    tfs = TFS()
    nfs = NormalFS()
    fake = Faker()
    normal_set, contrib_set, all_set = set(), set(), set()
    fs = BatchFSWrapper([tfs, nfs])
    weight = [1] * 3 + [2] * 2 + [3] * 0 + [4] + [5] + [6]
    for _ in range(150):
        ins = random.choice(weight)
        if ins == 1:
            name = fake.file_name()
            while name in all_set:
                name = fake.file_name()
            normal_set.add(name)
            all_set.add(name)
            fs.add_normal_file(name, random.randint(1, 5))
        elif ins == 2:
            name = fake.file_name()
            while name in all_set:
                name = fake.file_name()
            contrib_set.add(name)
            all_set.add(name)
            fs.add_contrib_file(name, random.randint(1, 10))
        elif ins == 3:
            if len(normal_set):
                file = random.choice(list(normal_set))
                fs.stat_normal_file(file)
        elif ins == 4:
            if len(contrib_set):
                file = random.choice(list(contrib_set))
                fs.stat_contrib_file(file)
        elif ins == 5:
            if len(normal_set):
                file = random.choice(list(normal_set))
                fs.delete_normal_file(file)
                normal_set.remove(file)
                all_set.remove(file)
        elif ins == 6:
            if len(contrib_set):
                file = random.choice(list(contrib_set))
                fs.delete_contrib_file(file)
                contrib_set.remove(file)
                all_set.remove(file)
    # for file in list(contrib_set):
    #     fs.delete_contrib_file(file)
    return jsonify({'tfs': tfs.bitmap, 'nfs': nfs.bitmap})

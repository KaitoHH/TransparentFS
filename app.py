from flask import Flask
from TFS import TFS
from NormalFS import NormalFS
from flask import request, jsonify
from client import BatchFSWrapper

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
    fs = BatchFSWrapper([tfs, nfs])

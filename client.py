from TFS import TFS
from NormalFS import NormalFS


class BatchFSWrapper(object):
    def __init__(self, caller_list):
        self.caller = caller_list

    def __getattr__(self, item):
        return self.iterate_call(item)

    def iterate_call(self, attr):
        def wrapper(*args, **kwargs):
            for caller in self.caller:
                method = caller.__getattribute__(attr)
                method(*args, **kwargs)

        return wrapper


tfs = TFS()
nfs = NormalFS()
fs = BatchFSWrapper([tfs, nfs])

fs.add_normal_file('a', 10)
fs.add_contrib_file('_b', 20)
fs.add_normal_file('c', 3)
fs.stat_normal_file('c')
fs.view_top_n_status(50)
fs.stat_normal_file('c')
fs.view_top_n_status(50)
fs.stat_contrib_file('_b')
fs.view_top_n_status(50)
fs.delete_contrib_file('_b')
fs.view_top_n_status(50)

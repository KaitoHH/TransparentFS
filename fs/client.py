from fs.TFS import TFS
from fs.NormalFS import NormalFS
import config


class BatchFSWrapper(object):
    def __init__(self, caller_list):
        self.caller = caller_list

    def __getattr__(self, item):
        return self.iterate_call(item)

    def iterate_call(self, attr):
        def wrapper(*args, **kwargs):
            config.global_event_recorder = {'method': attr, 'args': args}
            # print(attr, *args)
            for caller in self.caller:
                method = caller.__getattribute__(attr)
                method(*args, **kwargs)

        return wrapper


if __name__ == '__main__':
    tfs = TFS()
    nfs = NormalFS()
    fs = BatchFSWrapper([tfs, nfs])

    fs.add_normal_file('provide.odp', 2)
    fs.add_contrib_file('share.txt', 8)
    fs.add_contrib_file('reduce.csv', 2)
    fs.add_contrib_file('available.js', 1)
    fs.add_normal_file('party.numbers', 5)
    fs.delete_normal_file('party.numbers')
    fs.add_contrib_file('seat.wav', 8)
    fs.delete_contrib_file('seat.wav')
    fs.view_top_n_status(50)

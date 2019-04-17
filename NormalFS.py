import config
from BaseFS import BaseFS


class NormalFSMeta(object):
    def __init__(self, block_offset, length):
        self.block_offset = block_offset
        self.length = length


class NormalFS(BaseFS):
    FREE = False
    ALLOCATED = True

    def __init__(self):
        self.bitmap = [NormalFS.FREE] * config.block_numbers
        self.file_list = {}

    def allocate_blocks(self, blocks):
        cnt = 0
        offset = 0
        for pos in range(config.block_numbers):
            if self.bitmap[pos] == NormalFS.FREE:
                if offset == -1:
                    offset = pos
                cnt += 1
                if cnt >= blocks:
                    return offset
            else:
                offset = -1
                cnt = 0

    def update_blocks_status(self, offset, length, status):
        for pos in range(offset, offset + length):
            self.bitmap[pos] = status

    def add_file(self, filename, blocks):
        offset = self.allocate_blocks(blocks)
        self.file_list[filename] = NormalFSMeta(offset, blocks)
        self.update_blocks_status(offset, blocks, NormalFS.ALLOCATED)

    def delete_file(self, filename):
        meta = self.file_list[filename]
        self.update_blocks_status(meta.block_offset, meta.length, NormalFS.FREE)

    def delete_contrib_file(self, filename):
        self.delete_file(filename)

    def delete_normal_file(self, filename):
        self.delete_file(filename)

    def add_contrib_file(self, filename, blocks):
        self.add_file(filename, blocks)

    def add_normal_file(self, filename, blocks):
        self.add_file(filename, blocks)

    def view_top_n_status(self, n):
        for pos in range(n):
            print(int(self.bitmap[pos]), end='')
        print()


if __name__ == '__main__':
    nfs = NormalFS()
    nfs.add_normal_file('a', 10)
    nfs.view_top_n_status(50)
    nfs.add_contrib_file('_b', 20)
    nfs.view_top_n_status(50)
    nfs.add_normal_file('c', 3)
    nfs.view_top_n_status(50)
    nfs.delete_normal_file('a')
    nfs.delete_contrib_file('_b')
    nfs.view_top_n_status(50)
    nfs.delete_normal_file('c')
    nfs.view_top_n_status(50)
    nfs.add_normal_file('d', 15)
    nfs.view_top_n_status(50)
    nfs.delete_normal_file('d')
    nfs.view_top_n_status(50)

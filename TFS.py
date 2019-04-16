import os

block_numbers = 16 * 16 * 16


class TFSFileMeta(object):
    class FileType:
        NORMAL = 0
        CONTRIB = 1

    def __init__(self, block_offset, file_type):
        self.offset = block_offset
        self.type = file_type


class TFS(object):
    FREE = 0
    TRANSPARENT = 1
    ALLOCATED = 2

    def __init__(self, path):
        for i in range(block_numbers):
            open(os.path.join(path, '{:03x}'.format(i)), 'ab').close()
        self.bitmap = [TFS.FREE] * block_numbers
        self.fileList = {}

    def allocate_blocks(self, blocks, lm_fn):
        cnt = 0
        offset = 0
        for pos in range(block_numbers):
            if lm_fn(self.bitmap[pos]):
                if offset == -1:
                    offset = pos
                cnt += 1
                if cnt >= blocks:
                    return offset
            else:
                offset = -1
                cnt = 0

    def allocate_normal_file_block(self, blocks):
        return self.allocate_blocks(blocks, lambda s: s == TFS.FREE or s == TFS.TRANSPARENT)

    def allocate_transparent_file_block(self, blocks):
        return self.allocate_blocks(blocks, lambda s: s == TFS.FREE)

    def batch_update_block_status(self, offset, length, state):
        for pos in range(offset, offset + length):
            self.bitmap[pos] = state

    def add_normal_file(self, filename, blocks):
        offset = self.allocate_normal_file_block(blocks)
        self.fileList[filename] = TFSFileMeta(offset, TFSFileMeta.FileType.NORMAL)
        self.batch_update_block_status(offset, blocks, TFS.ALLOCATED)

    def add_contrib_file(self, filename, blocks):
        offset = self.allocate_transparent_file_block(blocks)
        self.fileList[filename] = TFSFileMeta(offset, TFSFileMeta.FileType.CONTRIB)
        self.batch_update_block_status(offset, blocks, TFS.TRANSPARENT)

    def view_top_n_status(self, n):
        for pos in range(n):
            print(self.bitmap[pos], end='')
        print()


if __name__ == '__main__':
    tfs = TFS('tfs')
    tfs.add_normal_file('a', 10)
    tfs.view_top_n_status(50)
    tfs.add_contrib_file('_b', 20)
    tfs.view_top_n_status(50)
    tfs.add_normal_file('c', 3)
    tfs.view_top_n_status(50)

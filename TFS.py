import os
import config
from BaseFS import BaseFS


class TFSFileMeta(object):
    class FileType:
        NORMAL = 0
        CONTRIB = 1

    def __init__(self, block_offset, length, file_type):
        self.offset = block_offset
        self.length = length
        self.type = file_type


class TFS(BaseFS):
    FREE = 0
    TRANSPARENT = 1
    ALLOCATED = 2
    FREE_OVERWRITTEN = 3
    ALLOCATED_OVERWRITTEN = 4
    INVALID = -1

    def __init__(self):
        # for i in range(block_numbers):
        #     open(os.path.join(path, '{:03x}'.format(i)), 'ab').close()
        self.bitmap = [TFS.FREE] * config.block_numbers
        self.file_list = {}

    def allocate_blocks(self, blocks, lm_fn):
        cnt = 0
        offset = 0
        for pos in range(config.block_numbers):
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
        return self.allocate_blocks(blocks,
                                    lambda s: s == TFS.FREE or s == TFS.TRANSPARENT or s == TFS.FREE_OVERWRITTEN)

    def allocate_transparent_file_block(self, blocks):
        return self.allocate_blocks(blocks, lambda s: s == TFS.FREE)

    def batch_update_block_status(self, offset, length, operation, fn=lambda s: True):
        for pos in range(offset, offset + length):
            if fn(self.bitmap[pos]):
                self.bitmap[pos] = TFSFileStateMachine.apply(self.bitmap[pos], operation)

    def add_normal_file(self, filename, blocks):
        offset = self.allocate_normal_file_block(blocks)
        self.file_list[filename] = TFSFileMeta(offset, blocks, TFSFileMeta.FileType.NORMAL)
        self.batch_update_block_status(offset, blocks, TFSFileStateMachine.Operation.WRITE)

    def add_contrib_file(self, filename, blocks):
        offset = self.allocate_transparent_file_block(blocks)
        self.file_list[filename] = TFSFileMeta(offset, blocks, TFSFileMeta.FileType.CONTRIB)
        self.batch_update_block_status(offset, blocks, TFSFileStateMachine.Operation.WRITE_CONTRIB)

    def delete_normal_file(self, filename):
        meta = self.file_list[filename]
        self.batch_update_block_status(meta.offset, meta.length, TFSFileStateMachine.Operation.DELETE)

    def delete_contrib_file(self, filename):
        meta = self.file_list[filename]
        self.batch_update_block_status(meta.offset, meta.length, TFSFileStateMachine.Operation.DELETE,
                                       lambda s: s == TFS.TRANSPARENT)

    def view_top_n_status(self, n):
        for pos in range(n):
            print(self.bitmap[pos], end='')
        print()


class TFSFileStateMachine(object):
    class Operation:
        WRITE = 0
        WRITE_CONTRIB = 1
        DELETE = 2
        CLEAN = 3

    transfer_map = {
        TFS.FREE: [TFS.ALLOCATED, TFS.TRANSPARENT, TFS.INVALID, TFS.INVALID],
        TFS.TRANSPARENT: [TFS.ALLOCATED_OVERWRITTEN, TFS.INVALID, TFS.FREE, TFS.INVALID],
        TFS.ALLOCATED_OVERWRITTEN: [TFS.INVALID, TFS.INVALID, TFS.FREE_OVERWRITTEN, TFS.ALLOCATED],
        TFS.FREE_OVERWRITTEN: [TFS.ALLOCATED_OVERWRITTEN, TFS.INVALID, TFS.INVALID, TFS.FREE],
        TFS.ALLOCATED: [TFS.INVALID, TFS.INVALID, TFS.FREE, TFS.INVALID]
    }

    @staticmethod
    def apply(state, operation):
        return TFSFileStateMachine.transfer_map[state][operation]


if __name__ == '__main__':
    tfs = TFS()
    tfs.add_normal_file('a', 10)
    tfs.view_top_n_status(50)
    tfs.add_contrib_file('_b', 20)
    tfs.view_top_n_status(50)
    tfs.add_normal_file('c', 3)
    tfs.view_top_n_status(50)
    tfs.delete_normal_file('a')
    tfs.delete_contrib_file('_b')
    tfs.view_top_n_status(50)
    tfs.delete_normal_file('c')
    tfs.view_top_n_status(50)
    tfs.add_normal_file('d', 15)
    tfs.view_top_n_status(50)
    tfs.delete_normal_file('d')
    tfs.view_top_n_status(50)

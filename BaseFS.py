class BaseFS(object):
    def add_normal_file(self, filename, blocks):
        raise NotImplementedError

    def add_contrib_file(self, filename, blocks):
        raise NotImplementedError

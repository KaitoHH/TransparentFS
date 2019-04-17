class BaseFS(object):
    def add_normal_file(self, filename, blocks):
        raise NotImplementedError

    def add_contrib_file(self, filename, blocks):
        raise NotImplementedError

    def delete_normal_file(self, filename):
        raise NotImplementedError

    def delete_contrib_file(self, filename):
        raise NotImplementedError

    def stat_normal_file(self, filename):
        raise NotImplementedError

    def stat_contrib_file(self, filename):
        raise NotImplementedError

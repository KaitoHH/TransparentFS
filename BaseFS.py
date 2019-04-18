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

    @staticmethod
    def to_json(file_list):
        return {key: file_list[key].__dict__ for key in file_list}

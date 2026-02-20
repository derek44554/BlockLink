class BlockModel:
    def __init__(self, data):
        self.data = data

    @property
    def bid(self):
        """
        获取 BID
        """
        return self.data['bid']

    def __getitem__(self, key):
        """
        获取 数据
        """

        data = self.data.get(key, None)
        return data

    def __setitem__(self, key, value):
        """
        写入数据
        """
        self.data[key] = value

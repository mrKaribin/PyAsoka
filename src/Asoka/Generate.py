from random import randint


class Generate:

    class Key:
        @staticmethod
        def hybrid(length=16):
            simbols = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
            key = ''
            for i in range(length):
                key += simbols[randint(0, 61)]
            return key

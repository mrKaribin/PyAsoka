from PyAsoka.FileSystem.File import File
from PyAsoka.TagSystem.Tag import Tag
from PyAsoka.TagSystem.TagLink import TagLink
from PyAsoka.src.Instruments.File import File as OsFile


class FileSystemTester:
    def __init__(self):
        pass

    @staticmethod
    def file_default_operations():
        data = OsFile('avatar.jpg').read_bytes()
        file = File(name='avatar', data=data, format='jpg')
        tag = Tag(id=1)
        file.save()
        tag.load()

        tag_link = TagLink(tag_id=tag.id(), obj_id=file.object()._id_())
        tag_link.save()

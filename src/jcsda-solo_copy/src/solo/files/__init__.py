from ..factory import create_factory
from .file_file import FileFile
from .file_s3 import FileS3
from .s3_file import S3File
from .s3_s3 import S3S3
from .s3 import S3
from .file import File


file_factory = create_factory('File')
file_factory.register('file_file', FileFile)
file_factory.register('file_s3', FileS3)
file_factory.register('s3_file', S3File)
file_factory.register('s3_s3', S3S3)
file_factory.register('s3', S3)
file_factory.register('file', File)
# for non supported protocols we assume file file.
file_factory.register_default(FileFile)

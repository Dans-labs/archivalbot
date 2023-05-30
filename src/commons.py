import logging
import os
import shutil

from dynaconf import Dynaconf

settings = Dynaconf(settings_files=["conf/settings.toml", "conf/.secrets.toml"],
                    environments=True)

logging.basicConfig(filename=settings.LOG_FILE, level=settings.LOG_LEVEL,
                    format=settings.LOG_FORMAT)

data = {}

def zip_folder(dir_path_to_zip, zip_path_destination):
    # name with dates
    zip_name = os.path.basename(os.path.normpath(dir_path_to_zip))
    zip_target = os.path.dirname(dir_path_to_zip)
    format = "zip"
    shutil.make_archive(zip_name, format, root_dir=dir_path_to_zip)
    shutil.move('%s.%s' % (zip_name, format), zip_path_destination)
    return os.path.join(zip_path_destination, zip_name + '.zip')


def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    print(source, destination, archive_from, archive_to)
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)
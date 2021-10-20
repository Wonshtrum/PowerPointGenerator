import pkg_resources
import zipfile
import glob
import time
import os


class Zipper():
	def __init__(self, output):
		self.zipfile = zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED)

	def put_file(self, path, data, compress=False):
		if compress:
			data = data.replace("\t", "").replace("\n", "")
		date_time = time.localtime(time.time())[:6]
		zinfo = zipfile.ZipInfo(path, date_time)
		self.zipfile.writestr(zinfo, data)

	def close(self):
		self.zipfile.close()


def create_base(name):
	base_path = pkg_resources.resource_filename(__name__, "base")
	base_path_length = len(base_path)+1
	base_files = glob.glob(f"{base_path}/**", recursive=True)
	base_files.extend(glob.glob(f"{base_path}/**/.rels", recursive=True))
	zipper = Zipper(name)
	for file_path in base_files:
		if os.path.isfile(file_path):
			zipped_file_path = file_path[base_path_length:]
			with open(file_path, "rb") as stream:
				zipper.put_file(zipped_file_path, stream.read())
	return zipper

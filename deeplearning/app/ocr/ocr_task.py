import os.path

from u_base import u_file
from u_base import u_log as log
from cnocr.utils import read_img
from cnocr import CnOcr


def cn_ocr_online_picture(image_url):
    path = r'result'
    filename = u_file.get_file_name_from_url(image_url)
    log.info('begin download file from url: {}, save as: {}'.format(image_url, filename))
    u_file.download_file(image_url, filename, path)
    log.info('download image success. url: {}'.format(image_url))
    ocr = CnOcr()
    image_path = read_img(os.path.join(path, filename))
    log.info('ocr process finished.')
    result = ocr.ocr(image_path)
    print(result)


if __name__ == '__main__':
    cn_ocr_online_picture('http://5b0988e595225.cdn.sohucs.com/images/20180801/8139831a7f7d4f098f8da8f1702cbe8a.jpeg')
# resize all images in dir with larger edge and output to another dir
#
# - usage:
#   python resize_image.py src_dir dst_dir larger_edge
#
#   e.g.
#   python resize_image.py /tmp/images /tmp/small 160
#
# - requires:
#   opencv-python
#   tqdm
#
# Authors: etworker

import sys
import os
import os.path as osp
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


def resize_image(src_file_path: str, dst_file_path: str, larger_edge: int) -> bool:
    """
    resize image file

    Args:
        src_file_path (str): source image file path
        dst_file_path (str): destination image file path
        larger_edge (int): image larger edge

    Returns:
        bool: if resize ok
    """

    if not osp.isfile(src_file_path):
        print(f'file not exist: {src_file_path}')
        return False

    try:
        img = cv2.imread(src_file_path)
        h, w, c = img.shape
        ratio = float(w) / h
        if w > h:
            w = larger_edge
            h = int(w / ratio)
        else:
            h = larger_edge
            w = int(h * ratio)

        img = cv2.resize(img, (w, h))
        cv2.imwrite(dst_file_path, img)

        return True
    except Exception as ex:
        print(f'resize failed, file = {src_file_path}, error = {ex}')
        return False


def resize_image_dir(src_dir: str, dst_dir: str, larger_edge: int = 160) -> bool:
    """
    resize images in src_dir, output to dst_dir

    Args:
        src_dir (str): source image dir
        dst_dir (str): destination image dir
        larger_edge (int, optional): image larger edge. Defaults to 160.

    Returns:
        bool: if resize image dir ok
    """

    if not osp.isdir(src_dir):
        print(f'dir not exist: {src_dir}')
        return False

    if not osp.isdir(dst_dir):
        os.makedirs(dst_dir)

    image_ext_set = set(['.jpg', '.png', '.jpeg'])
    with ThreadPoolExecutor() as executor:
        file_pair_list = []
        for file_name in tqdm(os.listdir(src_dir)):
            _, ext = osp.splitext(file_name)
            if ext not in image_ext_set:
                continue

            dst_file_path = osp.join(dst_dir, file_name)
            if osp.isfile(dst_file_path):
                continue

            file_pair_list.append((osp.join(src_dir, file_name), dst_file_path))

        if not file_pair_list:
            print(f'no image to resize')
            return True

        print(f'total image file num = {len(file_pair_list)}, action!')
        fs = [
            executor.submit(resize_image, src_file_path, dst_file_path, larger_edge)
            for src_file_path, dst_file_path in file_pair_list
        ]

        ok_cnt, fail_cnt = 0, 0
        for future in as_completed(fs):
            if future.result():
                ok_cnt += 1
                if ok_cnt % 1000 == 0:
                    print(f'{ok_cnt}/{len(file_pair_list)} ...')
            else:
                fail_cnt += 1
                print(f'fail = {fail_cnt}')

        print(f'finished, ok = {ok_cnt}, fail = {fail_cnt}')

        return True


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'usage: python resize_image.py src_dir dst_dir larger_edge')
        print('e.g. python resize_image.py /tmp/images {} 160'.format(
            osp.realpath(osp.join(osp.dirname(__file__), 'small_image'))))
    else:
        src_dir, dst_dir, larger_edge = sys.argv[1:4]
        resize_image_dir(src_dir, dst_dir, int(larger_edge))

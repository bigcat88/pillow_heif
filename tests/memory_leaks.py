from gc import collect as garbage_collect
from time import sleep
from os import path
from PIL import Image
from pillow_heif import register_heif_opener
from pympler import tracker


register_heif_opener()
TESTS_DIR = path.dirname(path.abspath(__file__))


def open_image(image_path):
    image = Image.open(image_path)
    image.load()
    assert image is not None


def perform_opens():
    image_path = path.join(TESTS_DIR, 'images', 'Pug', 'PUG1.HEIC')
    for i in range(10):
        open_image(image_path)


'''To test for memory leaks run 2 times, changing value in perform_opens from '10' to 2-5k, and compare results.'''
if __name__ == '__main__':
    tr = tracker.SummaryTracker()
    perform_opens()
    sleep(60*3)
    garbage_collect()
    tr.print_diff()

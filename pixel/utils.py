from math import sqrt
import numpy as np
import pyautogui
from time import sleep

try:
    from scapy.consts import WINDOWS
except:
    WINDOWS = True

if WINDOWS:
    PYGUI_RES = (1, 1)
    SCREENSHOT_RES = (1, 1)
    CATEGORIES_ZONE = (315, 159, 268, 713)
    SOMEWHERE_ON_CATEGORIES = (394, 784)
    ITEMS_COLUMN_X = 719  # Pyautogui pos
    BOTTOM_LINE_Y = 849  # Pyautogui pos
    TOP_ITEM_POS = (ITEMS_COLUMN_X, 224)  # Pyautogui pos
    TOP_ITEM_IMAGE_REGION = (607, 203, 27, 27)  # Screenshot pos
    def scroll(n: int):
        for _ in range(abs(n)):
            sleep(.1)
            pyautogui.scroll(200 * n // abs(n))
else:
    CATEGORIES_ZONE = (428, 312, 506, 1392) # Screenshot pos
    PYGUI_RES = (1680, 1050)
    SCREENSHOT_RES = (3360, 2100)
    SOMEWHERE_ON_CATEGORIES = (300, 800) # Pyautogui pos
    ITEMS_COLUMN_X = 714 # Pyautogui pos
    BOTTOM_LINE_Y = 840 # Pyautogui pos
    TOP_ITEM_POS = (ITEMS_COLUMN_X, 214) # Pyautogui pos
    TOP_ITEM_IMAGE_REGION = (998, 398, 54, 54) # Screenshot pos
    def scroll(n):
        pyautogui.scroll(n)


def scroll_max(direction: int):
    """

    :param direction: +1 for up, -1 for down
    :return:
    """
    for i in range(10):
        pyautogui.scroll(10000*direction)


def tuple_diff(tuple1, tuple2):
    return sqrt((tuple1[0] - tuple2[0]) ** 2 + (tuple1[1] - tuple2[1]) ** 2)

def convert_opencv_pos(pos: tuple):
    """
    On retina screen, you need to adjust
    :param pos:
    :return:
    """
    x, y = pos
    return (x/SCREENSHOT_RES[0]*PYGUI_RES[0], y/SCREENSHOT_RES[1]*PYGUI_RES[1])

def convert_pyautogui_pos(pos: tuple):
    """
    On retina screen, you need to adjust
    :param pos:
    :return:
    """
    x, y = pos
    return (x/PYGUI_RES[0]*SCREENSHOT_RES[0], y/PYGUI_RES[1]*SCREENSHOT_RES[1])

def offset_to_center(image: np.array):
    """
    Get the middle of an image
    :param image:
    :return:
    """
    x, y = image.shape[1], image.shape[0]
    return x // 2, y // 2

def apply_offset(locations: np.array, offset: tuple):
    """
    Modify entry array locations to apply to every row the offset
    :param locations:
    :param offset:
    :return:
    """
    for i in range(locations.shape[0]):
        locations[i][0] += offset[0]
        locations[i][1] += offset[1]
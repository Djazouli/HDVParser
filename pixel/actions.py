import pyautogui
import os
from time import sleep
import cv2
import numpy as np
import random


PYGUI_RES = (1680, 1050)
SCREENSHOT_RES = (3360, 2100)

import pathlib
BASE_FOLDER = pathlib.Path(__file__).parent.absolute()

import logging
logger = logging.getLogger("PIXEL")

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



class Action():
    def execute(self) -> None:
        raise NotImplementedError("You need to override this")
    def next_action(self):
        """

        :return: Next action or None
        """
        raise NotImplementedError("You need to override this")


class ClickOnUnclickedCategories(Action):
    """
    Click on the categories on the left of the screen. Make some template matching to find unchecked categories.
    Once all are checked, scroll down, until scrolling down does not provide any unchecked categories
    """
    def __init__(self):
        super().__init__()
        self.did_something = False

    def get_visible_unclicked_categories(self):
        method = cv2.TM_CCOEFF_NORMED
        unclicked_filepath = os.path.join(BASE_FOLDER, "images", "unclicked_category.png")
        image = cv2.imread(unclicked_filepath)
        screenshot = np.array(pyautogui.screenshot().convert("RGB"))
        # TODO: Could screen only a region
        result = cv2.matchTemplate(image, screenshot, method)
        loc = np.where(result >= 0.8)
        X = np.average(loc[1])  # all on the same column
        Y = []
        for y in loc[0]:
            if not Y or abs(Y[-1] - y) > 3:
                Y.append(y)
        X = [X] * len(Y)
        locations = np.array(list(zip(X, Y)), np.int32)
        apply_offset(locations, offset_to_center(image))
        return locations

    def next_action(self) -> Action or None:
        return ClickOnUnclickedCategories() if self.did_something else GoToBottomItemsAndClick()

    def execute(self) -> None:
        locations = self.get_visible_unclicked_categories()
        for pos in locations:
            pyautogui.click(*convert_opencv_pos(pos))
            sleep(.5)
        cont = locations.shape[0]
        wait = True
        while wait:
            # Wait that all clicks are taken into account
            sleep(1)
            wait = self.get_visible_unclicked_categories().shape[0]
        pyautogui.scroll(-cont)
        self.did_something = bool(cont)

class ClickOnTopItem(Action):
    """
    Click on the item at the top of the list, then scroll up
    """
    click_pos = (514, 214)
    screen_pos = convert_pyautogui_pos((499, 199))
    screen_size = convert_pyautogui_pos((27, 27))
    def __init__(self):
        super().__init__()
        self.old = None

    def screenshot_minia(self) -> np.array:
        return np.array(pyautogui.screenshot(region=(*self.screen_pos, *self.screen_size)).convert("LA"))


    def execute(self) -> None:
        pyautogui.click(x=self.click_pos[0], y=self.click_pos[1])
        self.old = self.screenshot_minia()
        pyautogui.scroll(1)
        sleep(random.randint(1,5) / 10) # Dont make it too obvious we're a bot

    def next_action(self) -> Action or None:
        if self.old is None:
            raise ValueError("We dont have a screenshot for this action")
        new = self.screenshot_minia()
        comparison = (new == self.old).all()
        if comparison:
            sleep(.1) # it may be because UI hasnt understood scrolling yet
            new = self.screenshot_minia()
            comparison = (new == self.old).all()
            if comparison:
                logger.info("Reached top of the HDV")
                return None
        return ClickOnTopItem()

class GoToBottomItemsAndClick(Action):
    """
    Scroll to the bottom of the item's list, then click on every item until we reach the top of the list.
    Then we switch to action ClickOnTopItem
    """
    def __init__(self):
        super().__init__()

    def execute(self) -> None:
        # Absolute values are found by moving my mouse around and triggering pyautogui.position()
        pyautogui.moveTo(499, 813)
        pyautogui.scroll(-4000)
        sleep(1)
        nbr_of_items = 13
        for i in range(nbr_of_items):
            y = 840 - i*(840-214)/nbr_of_items
            pyautogui.click(499, y)
            sleep(1.)
            pyautogui.click(499, y)
            sleep(1.)

    def next_action(self) -> Action or None:
        return ClickOnTopItem()

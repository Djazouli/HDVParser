import pyautogui
import os
from time import sleep
import cv2
import numpy as np
import random
from pixel.utils import *

import pathlib
BASE_FOLDER = pathlib.Path(__file__).parent.absolute()

import logging
logger = logging.getLogger("PIXEL")


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
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
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
        scroll(-cont)
        self.did_something = bool(cont)

class GoToCategoriesTop(Action):
    def __init__(self):
        super().__init__()

    def execute(self) -> None:
        pyautogui.moveTo(*SOMEWHERE_ON_CATEGORIES) # Somewhere on categories
        scroll_max(1)
        return

    def next_action(self) -> Action:
        return ClickNextCategory()

class ClickNextCategory(Action):
    def __init__(self):
        super().__init__()
        self.finished = False

    def get_clicked_pos(self) -> tuple or None:
        pyautogui.screenshot("test.png", region=CATEGORIES_ZONE)
        located = pyautogui.locateCenterOnScreen(
            os.path.join(BASE_FOLDER, "images", "clicked_category.png"),
            confidence=0.8,
            region=CATEGORIES_ZONE,
        )
        #if located is not None:
        #    located = located[0] + CATEGORIES_ZONE[0], located[1] + CATEGORIES_ZONE[1]
        return located

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

    def get_next_unclicked(self, clicked_pos: tuple=None) -> tuple or None:
        unclicked_positions = self.get_visible_unclicked_categories()
        for unclicked_position in unclicked_positions:
            unclicked_position = convert_opencv_pos(unclicked_position)
            if clicked_pos is not None and unclicked_position[1] < clicked_pos[1]:
                continue
            return unclicked_position[0], unclicked_position[1]
        return None

    def execute(self) -> None:
        clicked_pos = self.get_clicked_pos()
        if clicked_pos is not None:
            clicked_pos = convert_opencv_pos(clicked_pos)
            pyautogui.moveTo(*clicked_pos)
            sleep(.2)
            scroll(-1)
            sleep(.5)
            new_clicked = convert_opencv_pos(self.get_clicked_pos())
            if tuple_diff(clicked_pos, new_clicked) < 10:
                # scroll didn't do anything
                clicked_pos = self.get_next_unclicked(new_clicked)
            pyautogui.click(*new_clicked) # Uncheck box
            if clicked_pos is None:
                self.finished = True
                return
            pyautogui.click(*clicked_pos) # check next category
        else:
            clicked_pos = self.get_next_unclicked()
            pyautogui.click(*clicked_pos)
        sleep(3.) # Depends on how fast your computer can load the items
        return

    def next_action(self) -> Action:
        return GoToCategoriesTop() if self.finished else GoToBottomItemsAndClick()

class ClickOnTopItem(Action):
    """
    Click on the item at the top of the list, then scroll up
    """
    click_pos = TOP_ITEM_POS
    def __init__(self):
        super().__init__()
        self.old = None

    def screenshot_minia(self) -> np.array:
        return np.array(pyautogui.screenshot(region=TOP_ITEM_IMAGE_REGION).convert("LA"))


    def execute(self) -> None:
        pyautogui.click(x=self.click_pos[0], y=self.click_pos[1])
        self.old = self.screenshot_minia()
        scroll(1)
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
                return ClickNextCategory()
        return ClickOnTopItem()

class GoToBottomItemsAndClick(Action):
    """
    Scroll to the bottom of the item's list, then click on every item until we reach the top of the list.
    Then we switch to action ClickOnTopItem
    """
    def __init__(self):
        super().__init__()

    def execute(self) -> None:
        pyautogui.moveTo(ITEMS_COLUMN_X, BOTTOM_LINE_Y)
        scroll_max(-1)
        sleep(1)
        nbr_of_items = 13
        for i in range(nbr_of_items):
            y = BOTTOM_LINE_Y - i*(BOTTOM_LINE_Y-TOP_ITEM_POS[1])/nbr_of_items
            pyautogui.click(ITEMS_COLUMN_X, y)
            sleep(1.)
            pyautogui.click(ITEMS_COLUMN_X, y)
            sleep(1.)

    def next_action(self) -> Action or None:
        return ClickOnTopItem()

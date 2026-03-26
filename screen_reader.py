import re
import logging
import numpy as np
import pyautogui
import cv2
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

# Uncomment and set path if tesseract is not in PATH on Windows:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def screenshot(region=None) -> Image.Image:
    """Take a screenshot, optionally cropped to region [x, y, w, h]."""
    if region:
        x, y, w, h = region
        return pyautogui.screenshot(region=(x, y, w, h))
    return pyautogui.screenshot()


def screenshot_cv(region=None) -> np.ndarray:
    img = screenshot(region)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def find_button(template_path: str, confidence: float = 0.8):
    """
    Find a UI button on screen using template matching.
    Returns (x, y) center if found, else None.
    """
    try:
        location = pyautogui.locateOnScreen(template_path, confidence=confidence)
        if location:
            return pyautogui.center(location)
    except pyautogui.ImageNotFoundException:
        pass
    except Exception as e:
        logger.error(f"find_button error ({template_path}): {e}")
    return None


def read_text_from_region(region: list, preprocess: bool = True) -> str:
    """
    OCR text from a screen region.
    region: [x, y, w, h]
    """
    img = screenshot_cv(region)
    if preprocess:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789% "
    text = pytesseract.image_to_string(img, config=config)
    return text.strip()


def read_creature_name(region: list) -> str:
    """Read the creature name from the battle UI."""
    raw = read_text_from_region(region, preprocess=True)
    cleaned = re.sub(r"[^a-zA-Z ]", "", raw).strip()
    logger.debug(f"Creature name OCR: '{raw}' → '{cleaned}'")
    return cleaned


def read_capture_percentage(region: list) -> int:
    """
    Read the capture % shown in battle UI.
    Returns integer 0-100, or -1 if unreadable.
    """
    raw = read_text_from_region(region, preprocess=True)
    match = re.search(r"(\d{1,3})\s*%?", raw)
    if match:
        val = int(match.group(1))
        logger.debug(f"Capture % OCR: '{raw}' → {val}%")
        return min(val, 100)
    logger.warning(f"Could not parse capture % from: '{raw}'")
    return -1


def is_battle_active(battle_indicator_path: str) -> bool:
    """Check if a battle is currently happening using image detection."""
    return find_button(battle_indicator_path, confidence=0.75) is not None

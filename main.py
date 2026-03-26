"""
Miscrits AutoFarm Bot
---------------------
F10  = Pause / Resume
F12  = Stop completely
"""

import time
import logging
import threading
import sys
from enum import Enum

import keyboard

import screen_reader as sr
from config_manager import ConfigManager
from battle_handler import BattleHandler, BattleResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("autofarm.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)


class BotState(Enum):
    RUNNING = "running"
    PAUSED  = "paused"
    STOPPED = "stopped"


class AutoFarmBot:
    def __init__(self):
        self.cfg = ConfigManager()
        self.state = BotState.PAUSED
        self.stop_event = threading.Event()
        self._register_hotkeys()

    def _register_hotkeys(self):
        pause_key = self.cfg.keys.get("pause_resume", "F10")
        stop_key  = self.cfg.keys.get("stop", "F12")

        keyboard.add_hotkey(pause_key, self._toggle_pause)
        keyboard.add_hotkey(stop_key, self._stop)
        logger.info(f"Hotkeys → Pause/Resume: {pause_key} | Stop: {stop_key}")

    def _toggle_pause(self):
        if self.state == BotState.RUNNING:
            self.state = BotState.PAUSED
            logger.info("=== BOT PAUSED ===")
        elif self.state == BotState.PAUSED:
            self.state = BotState.RUNNING
            logger.info("=== BOT RESUMED ===")

    def _stop(self):
        self.state = BotState.STOPPED
        self.stop_event.set()
        logger.info("=== BOT STOPPED ===")

    def _wait_for_battle(self) -> bool:
        """
        Wait until a battle starts.
        Returns True if battle detected, False if stopped/paused.
        """
        indicator = self.cfg.assets.get("battle_start_indicator")
        interval  = self.cfg.timing.get("battle_check_interval_ms", 800) / 1000

        while not self.stop_event.is_set():
            if self.state == BotState.STOPPED:
                return False
            if self.state == BotState.PAUSED:
                time.sleep(0.5)
                continue

            if sr.is_battle_active(indicator):
                return True

            time.sleep(interval)
        return False

    def _read_creature_name(self) -> str:
        region = self.cfg.regions.get("creature_name")
        if not region:
            logger.warning("No creature_name region configured.")
            return ""
        name = sr.read_creature_name(region)
        if not name:
            logger.warning("Could not read creature name from screen.")
        return name

    def run(self):
        logger.info("AutoFarm Bot started. Press F10 to start/pause, F12 to stop.")
        logger.info("Waiting for you to press F10 to begin...")

        while self.state != BotState.STOPPED:
            # Wait for resume if paused
            if self.state == BotState.PAUSED:
                time.sleep(0.3)
                continue

            # Wait for a battle encounter
            battle_found = self._wait_for_battle()
            if not battle_found:
                break

            # Short delay to let battle UI fully load
            time.sleep(0.5)

            # Read creature name
            creature_name = self._read_creature_name()
            if not creature_name:
                logger.warning("Empty creature name, skipping this encounter.")
                continue

            logger.info(f"Encounter: '{creature_name}'")

            # Reset stop event before each battle (only stop within-battle)
            self.stop_event.clear()
            handler = BattleHandler(self.cfg, self.stop_event)
            result = handler.run_battle(creature_name)

            logger.info(f"Battle result: {result.value} ({creature_name})")

            # If stop was triggered inside battle, pause the bot
            if result in (BattleResult.MANUAL_STOP, BattleResult.CAPTURE_FAILED):
                self.state = BotState.PAUSED
                logger.info("Bot paused. Press F10 to resume when ready.")

            # Small cooldown between encounters
            scan_interval = self.cfg.timing.get("scan_interval_ms", 500) / 1000
            time.sleep(scan_interval)

        logger.info("Bot exited.")


if __name__ == "__main__":
    bot = AutoFarmBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")

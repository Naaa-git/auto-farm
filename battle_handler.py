import time
import logging
import pyautogui
from enum import Enum

import screen_reader as sr
import notifier

logger = logging.getLogger(__name__)


class BattleResult(Enum):
    KILLED = "killed"
    CAPTURED = "captured"
    MANUAL_STOP = "manual_stop"
    CAPTURE_FAILED = "capture_failed"
    FLED = "fled"


class BattleHandler:
    def __init__(self, cfg, stop_event):
        self.cfg = cfg
        self.stop_event = stop_event

    def _press_attack(self):
        key = self.cfg.keys.get("attack", "1")
        pyautogui.press(key)
        delay = self.cfg.timing.get("after_attack_delay_ms", 1500) / 1000
        time.sleep(delay)

    def _press_capture(self):
        key = self.cfg.keys.get("capture", "c")
        pyautogui.press(key)
        delay = self.cfg.timing.get("after_capture_delay_ms", 2000) / 1000
        time.sleep(delay)

    def _press_flee(self):
        key = self.cfg.keys.get("flee", "f")
        pyautogui.press(key)
        time.sleep(1.5)

    def _get_capture_pct(self) -> int:
        region = self.cfg.regions.get("capture_percentage")
        if not region:
            return -1
        return sr.read_capture_percentage(region)

    def _is_battle_still_active(self) -> bool:
        indicator = self.cfg.assets.get("battle_start_indicator")
        if not indicator:
            return True
        return sr.is_battle_active(indicator)

    def handle_kill(self, creature_name: str) -> BattleResult:
        """Spam attack until creature dies."""
        logger.info(f"[KILL] {creature_name}")
        while not self.stop_event.is_set():
            if not self._is_battle_still_active():
                logger.info(f"[KILL] Battle ended: {creature_name} killed.")
                return BattleResult.KILLED
            self._press_attack()
        return BattleResult.MANUAL_STOP

    def handle_manual(self, creature_name: str) -> BattleResult:
        """Stop bot and notify user to handle manually."""
        logger.info(f"[MANUAL] Stopping for: {creature_name}")
        self.stop_event.set()
        notifier.notify_manual_creature(creature_name, self.cfg)
        return BattleResult.MANUAL_STOP

    def handle_auto_capture(self, creature_name: str) -> BattleResult:
        """
        Attack until capture % >= threshold, then attempt capture.
        If capture fails (battle still active after capture attempt), notify and stop.
        """
        threshold = self.cfg.capture_threshold
        logger.info(f"[AUTO CAPTURE] {creature_name} | Threshold: {threshold}%")

        while not self.stop_event.is_set():
            if not self._is_battle_still_active():
                # Battle ended without us capturing — creature may have died
                logger.warning(f"[AUTO CAPTURE] Battle ended unexpectedly for {creature_name}")
                return BattleResult.KILLED

            pct = self._get_capture_pct()
            logger.debug(f"[AUTO CAPTURE] {creature_name} capture%={pct}")

            if pct == -1:
                # Can't read %, attack once and retry
                self._press_attack()
                continue

            if pct >= threshold:
                logger.info(f"[AUTO CAPTURE] Attempting capture at {pct}%...")
                self._press_capture()

                # Check if battle ended (capture succeeded)
                time.sleep(self.cfg.timing.get("after_capture_delay_ms", 2000) / 1000)
                if not self._is_battle_still_active():
                    logger.info(f"[AUTO CAPTURE] Captured: {creature_name}!")
                    return BattleResult.CAPTURED

                # Battle still active = capture missed
                logger.warning(f"[AUTO CAPTURE] Capture MISSED: {creature_name}")
                self.stop_event.set()
                notifier.notify_capture_failed(creature_name, self.cfg)
                return BattleResult.CAPTURE_FAILED

            # Capture % not yet at threshold, attack once
            self._press_attack()

        return BattleResult.MANUAL_STOP

    def run_battle(self, creature_name: str) -> BattleResult:
        """Entry point: determine mode and handle battle accordingly."""
        mode = self.cfg.get_capture_mode(creature_name)
        logger.info(f"[BATTLE] {creature_name} → mode: {mode}")

        if mode == "manual":
            return self.handle_manual(creature_name)
        elif mode == "auto":
            return self.handle_auto_capture(creature_name)
        else:
            return self.handle_kill(creature_name)

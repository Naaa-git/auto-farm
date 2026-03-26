import threading
import logging
import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger(__name__)


def play_sound(frequency: int = 1000, duration_ms: int = 800):
    """Play a beep sound (Windows only via winsound)."""
    try:
        import winsound
        winsound.Beep(frequency, duration_ms)
    except ImportError:
        logger.warning("winsound not available (non-Windows). Skipping sound.")
    except Exception as e:
        logger.error(f"Sound error: {e}")


def show_popup(title: str, message: str, timeout_ms: int = 0):
    """
    Show a popup notification in a separate thread.
    timeout_ms=0 means popup stays until closed manually.
    """
    def _show():
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        if timeout_ms > 0:
            root.after(timeout_ms, root.destroy)

        messagebox.showinfo(title, message, parent=root)
        root.destroy()

    t = threading.Thread(target=_show, daemon=True)
    t.start()


def notify_manual_creature(creature_name: str, cfg):
    """Notify when a MANUAL mode creature appears."""
    freq = cfg.get("notification", "sound_frequency", default=1000)
    dur = cfg.get("notification", "sound_duration_ms", default=800)
    timeout = cfg.get("notification", "popup_timeout_ms", default=0)

    play_sound(freq, dur)
    show_popup(
        title="Miscrits AutoFarm - Creature Found!",
        message=f"'{creature_name}' ada di capture list!\n\nBot berhenti. Silakan handle manual.",
        timeout_ms=timeout
    )
    logger.info(f"[NOTIFY] Manual creature: {creature_name}")


def notify_capture_failed(creature_name: str, cfg):
    """Notify when auto capture attempt fails/misses."""
    freq = cfg.get("notification", "sound_frequency", default=1000)
    dur = cfg.get("notification", "sound_duration_ms", default=800)
    timeout = cfg.get("notification", "popup_timeout_ms", default=0)

    play_sound(freq, dur)
    play_sound(freq, dur)
    show_popup(
        title="Miscrits AutoFarm - Capture Gagal!",
        message=f"Capture '{creature_name}' MISS!\n\nBot berhenti. Silakan handle manual.",
        timeout_ms=timeout
    )
    logger.info(f"[NOTIFY] Capture failed: {creature_name}")

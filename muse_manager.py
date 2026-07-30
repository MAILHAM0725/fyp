# muse_manager.py
import subprocess
import time
import threading

# Try to import all resolve variants safely
try:
    from pylsl import resolve_stream
except Exception:
    resolve_stream = None

try:
    from pylsl import resolve_byprop
except Exception:
    resolve_byprop = None

try:
    from pylsl import resolve_streams
except Exception:
    resolve_streams = None


class MuseManager:
    def __init__(self, on_disconnect_callback=None, on_reconnect_callback=None):
        self.muse_process = None
        self.muse_connected = False
        self.monitor_thread = None
        self.stop_monitor = False
        self.on_disconnect_callback = on_disconnect_callback
        self.on_reconnect_callback = on_reconnect_callback

    # ---------- LSL compatibility helper ----------
    def _find_eeg_streams(self, timeout_sec=5):
        """
        Return a list of EEG LSL streams using whatever pylsl API is available.
        Works across pylsl versions (resolve_stream / resolve_byprop / resolve_streams).
        """
        # 1) Preferred modern API
        if resolve_stream is not None:
            try:
                return resolve_stream('type', 'EEG', timeout=timeout_sec)
            except TypeError:
                # Some builds don't like keyword or signature
                try:
                    return resolve_stream('type', 'EEG', timeout_sec)
                except Exception:
                    pass
            except Exception:
                pass

        # 2) Alternative API
        if resolve_byprop is not None:
            try:
                return resolve_byprop('type', 'EEG', timeout=timeout_sec)
            except TypeError:
                try:
                    return resolve_byprop('type', 'EEG', timeout_sec)
                except Exception:
                    pass
            except Exception:
                pass

        # 3) Legacy plural API (note: positional only, old param is 'wait_time')
        if resolve_streams is not None:
            try:
                return [s for s in resolve_streams(timeout_sec) if s.type() == 'EEG']
            except TypeError:
                # Some very old versions might require an int/float only
                try:
                    return [s for s in resolve_streams(float(timeout_sec)) if s.type() == 'EEG']
                except Exception:
                    pass
            except Exception:
                pass

        # Nothing worked
        return []

    # ---------- Public API ----------
    def connect_muse(self):
        """Start muselsl stream in background using subprocess (Windows-stable)."""
        if self.muse_connected:
            print("[INFO] Muse already connected.")
            return True

        try:
            print("[INFO] Launching muselsl stream process...")
            self.muse_process = subprocess.Popen(
                ["python", "-m", "muselsl", "stream"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # Wait longer for Bluetooth initialization (Muse can take 10–15s)
            for i in range(15):
                time.sleep(1)
                print(f"[DEBUG] Waiting for EEG stream... {i+1}/15")
                streams = self._find_eeg_streams(timeout_sec=2)
                if streams:
                    self.muse_connected = True
                    print("[SUCCESS] Muse stream detected and connected!")
                    self.start_monitor_thread()
                    return True

            print("[ERROR] No EEG stream found after waiting 15 seconds.")
            self.disconnect_muse()
            return False

        except Exception as e:
            print(f"[ERROR] Muse connection failed: {e}")
            self.disconnect_muse()
            return False

    def disconnect_muse(self):
        """Stop Muse stream and clean up fully."""
        print("[INFO] Forcing Muse disconnect...")
        self.stop_monitor = True

        # terminate any background muselsl process
        if self.muse_process:
            try:
                self.muse_process.terminate()
                self.muse_process.wait(timeout=3)
            except Exception:
                pass
            self.muse_process = None

        # reset all flags and threads
        self.muse_connected = False
        self.monitor_thread = None
        print("[INFO] Muse fully disconnected and cleaned up.")

    def start_monitor_thread(self):
        """Start a background thread to detect disconnections."""
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
        self.stop_monitor = False
        self.monitor_thread = threading.Thread(target=self.monitor_connection, daemon=True)
        self.monitor_thread.start()

    def monitor_connection(self):
        """Continuously check if Muse stream is alive."""
        while not self.stop_monitor:
            try:
                streams = self._find_eeg_streams(timeout_sec=2)
                if not streams:
                    print("[WARNING] Muse disconnected!")
                    self.handle_disconnection()
                    break
            except Exception as e:
                print(f"[ERROR] Connection check failed: {e}")
                self.handle_disconnection()
                break
            time.sleep(3)

    def handle_disconnection(self):
        """Handle Muse disconnection and attempt infinite reconnects."""
        print("[WARNING] Muse disconnected detected in monitor thread.")
        self.muse_connected = False

        # stop current monitoring thread safely
        self.stop_monitor = True
        if self.monitor_thread:
            self.monitor_thread = None

        if self.on_disconnect_callback:
            try:
                self.on_disconnect_callback()
            except TypeError:
                self.on_disconnect_callback

        # === Reconnect loop until success ===
        attempt = 1
        while True:
            print(f"[INFO] Attempting reconnection #{attempt}...")
            self.disconnect_muse()  # full reset
            time.sleep(2)

            success = self.connect_muse()
            if success:
                print(f"[SUCCESS] Reconnected successfully on attempt {attempt}.")
                if self.on_reconnect_callback:
                    try:
                        self.on_reconnect_callback()
                    except TypeError:
                        self.on_reconnect_callback
                return
            else:
                print(f"[RETRY] Reconnect attempt {attempt} failed, retrying in 5s...")
                time.sleep(5)
                attempt += 1

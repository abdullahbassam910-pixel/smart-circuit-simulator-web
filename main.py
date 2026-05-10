import sys
import time
import traceback
import tkinter as tk
from functools import wraps
from tkinter import messagebox

try:
    from ui.app import CircuitProApp
except ImportError as error:
    print(f"[CRITICAL] Failed to import CircuitProApp: {error}")
    sys.exit(1)


APP_NAME = "SMART CIRCUIT SIMULATOR PRO"
APP_VERSION = getattr(CircuitProApp, "VERSION", "6.2")

WINDOW_SIZE = "1440x860"
MIN_WIDTH = 1220
MIN_HEIGHT = 740
APP_BG = "#151821"


def log(level, msg):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")


def configure_root(root):
    """Configure the main application window."""
    root.title(f"{APP_NAME} v{APP_VERSION}")
    root.geometry(WINDOW_SIZE)
    root.minsize(MIN_WIDTH, MIN_HEIGHT)
    root.configure(bg=APP_BG)
    root.protocol("WM_DELETE_WINDOW", lambda: on_app_close(root))


def on_app_close(root):
    """Close the application safely."""
    log("INFO", "Cleaning up resources and closing...")

    try:
        root.quit()
        root.destroy()
    except tk.TclError:
        pass
    except Exception as error:
        log("ERROR", f"Error while closing application: {error}")


def handle_exception(error):
    """Show unexpected errors in terminal and message box."""
    log("ERROR", f"Uncaught exception: {error}")
    traceback.print_exc()

    error_msg = (
        "Application Error\n\n"
        f"{error}\n\n"
        "Check terminal for details."
    )

    try:
        messagebox.showerror("Critical Error", error_msg)
    except Exception:
        pass


def install_exception_hook():
    """Route uncaught exceptions through the app error handler."""
    def _hook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        handle_exception(exc_value)

    sys.excepthook = _hook


def measure_startup(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        log("DEBUG", f"Application core loaded in {round(end - start, 4)}s")
        return result

    return wrapper


@measure_startup
def init_application():
    """Create root window and load the main app."""
    log("INFO", f"Initializing {APP_NAME} v{APP_VERSION} engine...")

    root = tk.Tk()
    configure_root(root)

    try:
        app = CircuitProApp(root)
        log("SUCCESS", f"CircuitProApp v{APP_VERSION} engine is online.")
        return root, app

    except Exception as error:
        handle_exception(error)

        try:
            root.destroy()
        except Exception:
            pass

        return None, None


def main():
    install_exception_hook()

    log("INFO", "========================================")
    log("INFO", f" Starting {APP_NAME} v{APP_VERSION} ")
    log("INFO", " Modular UI / Save-Load / Undo-Redo / Zoom ")
    log("INFO", "========================================")

    root, app = init_application()

    if root and app:
        try:
            log("INFO", "Mainloop started. Application is running.")
            root.mainloop()

        except Exception as error:
            handle_exception(error)

        finally:
            log("INFO", "Application session terminated successfully.")

    else:
        log("CRITICAL", "Application failed to start. Emergency exit.")
        sys.exit(1)


if __name__ == "__main__":
    main()

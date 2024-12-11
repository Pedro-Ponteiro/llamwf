import win32gui  # type: ignore
from PIL import ImageGrab


class ScreenshotTaker:
    def __init__(self):
        pass

    def _list_all_windows(self):
        """Return a list of (hwnd, title) for all top-level windows."""
        windows = []

        def enum_handler(h, _):
            title = win32gui.GetWindowText(h)
            if title:
                windows.append((h, title))

        win32gui.EnumWindows(enum_handler, None)
        return windows

    def _find_window_by_title_fragment(self, title_fragment, windows):
        """
        Given a title fragment and a list of (hwnd, title) tuples,
        return the first hwnd whose title contains the fragment.
        """
        title_fragment_lower = title_fragment.lower()
        matching = [
            hwnd for hwnd, title in windows if title_fragment_lower in title.lower()
        ]
        return matching[0] if matching else None

    def _get_window_rect(self, hwnd):
        """Return (left, top, right, bottom) coordinates for the given hwnd."""
        return win32gui.GetWindowRect(hwnd)

    def _focus_window(self, hwnd):
        """Attempt to bring the window to the foreground."""
        win32gui.SetForegroundWindow(hwnd)

    def _capture_region(self, left, top, right, bottom):
        """Capture a screenshot of the region (left, top, right, bottom)."""
        return ImageGrab.grab(bbox=(left, top, right, bottom))

    def _capture_window_screenshot(self, hwnd):
        """
        Given a hwnd, return a PIL Image of that window.
        This function composes the others: it gets the rect and then captures it.
        """
        rect = self._get_window_rect(hwnd)
        left, top, right, bottom = rect
        return self._capture_region(left, top, right, bottom)

    def take_screenshot_of_window(self, title_fragment):
        # List all windows
        windows = self._list_all_windows()
        # Find the desired window
        hwnd = self._find_window_by_title_fragment(title_fragment, windows)

        if hwnd is None:
            raise Exception("Window not found!")

        # Bring the window into focus (side-effect)
        self._focus_window(hwnd)

        # Capture screenshot of that window
        img = self._capture_window_screenshot(hwnd)
        return img


# if __name__ == "__main__":
#     # Exemplo de uso:
#     st = ScreenshotTaker()
#     image = st.take_screenshot_of_window("Notepad")
#     # Aqui `image` é um objeto PIL.Image. Você pode salvá-lo se quiser:
#     # image.save("window_screenshot.png")
#     # Ou manipulá-lo conforme sua necessidade.

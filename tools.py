import time
import pygetwindow as gw
# -------------------------
# Calculator Tool
# -------------------------

def calculate(expression):

    try:

        # Only allow basic mathematical characters
        allowed = "0123456789+-*/().% "

        if not all(
            character in allowed
            for character in expression
        ):
            return None

        result = eval(
            expression,
            {"__builtins__": None},
            {}
        )

        return result

    except Exception:

        return None


# -------------------------
# Time Tool
# -------------------------

from datetime import datetime

def get_current_time():

    current_time = datetime.now().strftime("%I:%M %p")

    return current_time

def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


def get_current_day():
    return datetime.now().strftime("%A")

def get_current_year():
    return datetime.now().year

# -------------------------
# Unit Conversion Tool
# -------------------------

def convert_units(value, from_unit, to_unit):

    conversions = {
        # Length → meters
        "meter": ("length", 1),
        "meters": ("length", 1),
        "m": ("length", 1),

        "kilometer": ("length", 1000),
        "kilometers": ("length", 1000),
        "km": ("length", 1000),

        "centimeter": ("length", 0.01),
        "centimeters": ("length", 0.01),
        "cm": ("length", 0.01),

        "millimeter": ("length", 0.001),
        "millimeters": ("length", 0.001),
        "mm": ("length", 0.001),

        "mile": ("length", 1609.344),
        "miles": ("length", 1609.344),

        "yard": ("length", 0.9144),
        "yards": ("length", 0.9144),

        "foot": ("length", 0.3048),
        "feet": ("length", 0.3048),

        "inch": ("length", 0.0254),
        "inches": ("length", 0.0254),

        # Weight → kilograms
        "kilogram": ("weight", 1),
        "kilograms": ("weight", 1),
        "kg": ("weight", 1),

        "gram": ("weight", 0.001),
        "grams": ("weight", 0.001),
        "g": ("weight", 0.001),

        "pound": ("weight", 0.45359237),
        "pounds": ("weight", 0.45359237),
        "lb": ("weight", 0.45359237),
        "lbs": ("weight", 0.45359237),

        "ounce": ("weight", 0.0283495231),
        "ounces": ("weight", 0.0283495231),
        "oz": ("weight", 0.0283495231),
    }

    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()

    # Temperature conversions
    if from_unit in ["celsius", "c"] and to_unit in ["fahrenheit", "f"]:
        return (value * 9 / 5) + 32

    if from_unit in ["fahrenheit", "f"] and to_unit in ["celsius", "c"]:
        return (value - 32) * 5 / 9

    if from_unit in ["celsius", "c"] and to_unit in ["kelvin", "k"]:
        return value + 273.15

    if from_unit in ["kelvin", "k"] and to_unit in ["celsius", "c"]:
        return value - 273.15

    if from_unit in ["fahrenheit", "f"] and to_unit in ["kelvin", "k"]:
        return (value - 32) * 5 / 9 + 273.15

    if from_unit in ["kelvin", "k"] and to_unit in ["fahrenheit", "f"]:
        return (value - 273.15) * 9 / 5 + 32

    # Length / weight conversions
    if from_unit not in conversions or to_unit not in conversions:
        return None

    from_type, from_factor = conversions[from_unit]
    to_type, to_factor = conversions[to_unit]

    # Don't allow meaningless conversions
    if from_type != to_type:
        return None

    base_value = value * from_factor
    result = base_value / to_factor

    return result

# -------------------------
# Weather Tool
# -------------------------

import requests
def get_weather(city):

    try:
        url = f"https://wttr.in/{city}?format=j1"

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        current = data["current_condition"][0]

        temperature = current["temp_C"]
        feels_like = current["FeelsLikeC"]
        description = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]

        return {
            "city": city,
            "temperature": temperature,
            "feels_like": feels_like,
            "description": description,
            "humidity": humidity
        }

    except Exception:
        return None

# -------------------------
# System Information Tool
# -------------------------

import psutil
import platform


def get_system_info():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()

    disk = psutil.disk_usage("C:\\")

    system = platform.system()
    release = platform.release()
    processor = platform.processor()

    return (
        f"CPU usage is {cpu} percent. "
        f"RAM usage is {ram.percent} percent. "
        f"Available RAM is {round(ram.available / (1024 ** 3), 1)} GB. "
        f"C drive usage is {disk.percent} percent. "
        f"Operating system is {system} {release}. "
        f"Processor is {processor}."
    )

# -------------------------
# Timer Tool
# -------------------------

import threading


def set_timer(seconds):

    from notifications import notify

    def timer_finished():
        notify("Timer finished!")

    timer = threading.Timer(
        seconds,
        timer_finished
    )

    timer.start()

    return f"Timer set for {seconds} seconds."

# -------------------------
# Reminder Tool
# -------------------------

def set_reminder(seconds, message):

    from notifications import notify

    def reminder_finished():
        notify(f"Reminder: {message}")

    timer = threading.Timer(
        seconds,
        reminder_finished
    )

    timer.start()

    return f"Reminder set for {seconds} seconds: {message}"

# -------------------------
# Application Launcher Tool
# -------------------------

import subprocess


def launch_application(application):

    applications = {
        "chrome": "chrome",
        "google chrome": "chrome",

        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",

        "paint": "mspaint.exe",
        "wordpad": "write.exe",

        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",

        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",

        "powershell": "powershell.exe",

        "vscode": "code",
        "visual studio code": "code"
    }

    application = application.lower().strip()

    if application not in applications:
        return f"I don't know how to open {application} yet."

    try:
        subprocess.Popen(
            applications[application],
            shell=True
        )

        return f"Opening {application}."

    except Exception:
        return f"I couldn't open {application}."

# -------------------------
# Website Launcher Tool
# -------------------------

import subprocess

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def open_website(website):
    print("========== OPEN_WEBSITE CALLED ==========")
    print("Website:", website)

    websites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "chatgpt": "https://chatgpt.com",
        "github": "https://github.com",
        "gmail": "https://mail.google.com",
        "google drive": "https://drive.google.com",
        "linkedin": "https://www.linkedin.com",
        "instagram": "https://www.instagram.com",
        "facebook": "https://www.facebook.com",
        "whatsapp": "https://web.whatsapp.com",
    }

    website = website.lower().strip()

    if website not in websites:
        return f"I don't know how to open {website} yet."

    try:
        # Reuse an existing Chrome window if possible.
        if _activate_chrome_window():
            import pyautogui
            import time

            pyautogui.hotkey("ctrl", "l")
            time.sleep(0.2)
            pyautogui.write(websites[website], interval=0.01)
            pyautogui.press("enter")
        else:
            subprocess.Popen([CHROME_PATH, websites[website]])

        return f"Opening {website}."

    except Exception as error:
        print("Website launcher error:", repr(error))
        return f"I couldn't open {website}."

# -------------------------
# Volume Control Tool
# -------------------------

from pycaw.pycaw import AudioUtilities


def get_volume_controller():
    speakers = AudioUtilities.GetSpeakers()
    return speakers.EndpointVolume


def set_volume(level):
    volume = get_volume_controller()

    level = max(0, min(100, level))
    volume.SetMasterVolumeLevelScalar(level / 100, None)

    return f"Volume set to {int(level)} percent."


def increase_volume(amount=10):
    volume = get_volume_controller()

    current = volume.GetMasterVolumeLevelScalar() * 100
    new_level = min(100, current + amount)

    volume.SetMasterVolumeLevelScalar(new_level / 100, None)

    return f"Volume increased to {round(new_level)} percent."


def decrease_volume(amount=10):
    volume = get_volume_controller()

    current = volume.GetMasterVolumeLevelScalar() * 100
    new_level = max(0, current - amount)

    volume.SetMasterVolumeLevelScalar(new_level / 100, None)

    return f"Volume decreased to {round(new_level)} percent."


def mute_volume():
    volume = get_volume_controller()
    volume.SetMute(1, None)

    return "Volume muted."


def unmute_volume():
    volume = get_volume_controller()
    volume.SetMute(0, None)

    return "Volume unmuted."

# -------------------------
# Media Control Tool
# -------------------------

import pyautogui

def media_play_pause():
    pyautogui.press("playpause")
    return "Play/pause toggled."

def media_next():
    pyautogui.press("nexttrack")
    return "Next track."

def media_previous():
    pyautogui.press("prevtrack")
    return "Previous track."


# -------------------------
# Computer Control Tools
# -------------------------

import os
from pathlib import Path
from datetime import datetime


def _desktop_path():
    return Path.home() / "Desktop"


def open_path(target):
    """Open a file/folder path, or locate a unique matching item in common user folders."""
    target = str(target).strip().strip('"').strip("'")

    known_folders = {
        "desktop": Path.home() / "Desktop",
        "downloads": Path.home() / "Downloads",
        "documents": Path.home() / "Documents",
        "pictures": Path.home() / "Pictures",
        "music": Path.home() / "Music",
        "videos": Path.home() / "Videos",
    }

    path = known_folders.get(target.lower())
    if path is None:
        path = Path(os.path.expandvars(os.path.expanduser(target)))

    if path.exists():
        try:
            os.startfile(str(path))
            return f"Opening {path.name or path}."
        except Exception:
            return f"I couldn't open {path}."

    # Search common user locations for a unique match.
    query = Path(target).name.lower()
    matches = []
    roots = [
        Path.home() / "Desktop",
        Path.home() / "Documents",
        Path.home() / "Downloads",
        Path.home() / "Pictures",
    ]

    for root in roots:
        if not root.exists():
            continue
        try:
            for item in root.rglob("*"):
                if item.name.lower() == query or query in item.stem.lower():
                    matches.append(item)
                    if len(matches) >= 10:
                        break
        except (PermissionError, OSError):
            continue
        if len(matches) >= 10:
            break

    if len(matches) == 1:
        try:
            os.startfile(str(matches[0]))
            return f"Opening {matches[0].name}."
        except Exception:
            return f"I found {matches[0].name}, but I couldn't open it."

    if len(matches) > 1:
        names = "; ".join(str(item) for item in matches[:5])
        return f"I found multiple matches: {names}."

    return f"I couldn't find {target}."


def search_files(query):
    """Search common user folders for files or folders matching a name."""
    query = str(query).strip().strip('"').strip("'").lower()
    if not query:
        return "Tell me what file or folder to search for."

    roots = [
        Path.home() / "Desktop",
        Path.home() / "Documents",
        Path.home() / "Downloads",
        Path.home() / "Pictures",
    ]

    matches = []
    for root in roots:
        if not root.exists():
            continue
        try:
            for item in root.rglob("*"):
                if query in item.name.lower():
                    matches.append(item)
                    if len(matches) >= 10:
                        break
        except (PermissionError, OSError):
            continue
        if len(matches) >= 10:
            break

    if not matches:
        return f"I couldn't find anything matching {query}."

    if len(matches) == 1:
        return f"I found {matches[0].name} at {matches[0]}."

    result = "; ".join(str(item) for item in matches[:5])
    extra = len(matches) - 5
    if extra > 0:
        result += f"; and {extra} more."
    return f"I found these matches: {result}"


def create_folder(name):
    """Create a folder on the Desktop unless a full path is supplied."""
    name = str(name).strip().strip('"').strip("'")
    if not name:
        return "Tell me what you want to name the folder."

    path = Path(os.path.expandvars(os.path.expanduser(name)))
    if not path.is_absolute():
        path = _desktop_path() / name

    try:
        path.mkdir(parents=True, exist_ok=False)
        return f"Created the folder {path.name} on {path.parent}."
    except FileExistsError:
        return f"The folder {path.name} already exists."
    except Exception:
        return f"I couldn't create the folder {path.name}."


def take_screenshot():
    """Capture the full screen and save it to the Desktop."""
    try:
        import pyautogui
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = _desktop_path() / f"Vectoria_Screenshot_{timestamp}.png"
        pyautogui.screenshot().save(str(path))
        return f"Screenshot saved to {path}."
    except Exception:
        return "I couldn't take the screenshot."


def lock_computer():
    """Lock the Windows workstation."""
    try:
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        return "Computer locked."
    except Exception:
        return "I couldn't lock the computer."


# -------------------------
# Browser Navigation Tools
# -------------------------

def browser_scroll_up(amount=400):
    pyautogui.scroll(amount)
    return "Scrolled up."

def browser_scroll_down(amount=400):
    pyautogui.scroll(-amount)
    return "Scrolled down."

def browser_go_back():
    pyautogui.hotkey("alt", "left")
    return "Went back."

def browser_go_forward():
    pyautogui.hotkey("alt", "right")
    return "Went forward."

def browser_refresh():
    pyautogui.press("f5")
    return "Page refreshed."

def browser_new_tab():
    pyautogui.hotkey("ctrl", "t")
    return "New tab opened."

def browser_next_tab():
    pyautogui.hotkey("ctrl", "tab")
    return "Switched to the next tab."

def browser_previous_tab():
    pyautogui.hotkey("ctrl", "shift", "tab")
    return "Switched to the previous tab."

def browser_switch_to_tab(tab_number):
    try:
        tab_number = int(tab_number)
    except (TypeError, ValueError):
        return "Invalid tab number."

    if tab_number < 1 or tab_number > 8:
        return "I can switch directly to tabs one through eight."

    if tab_number == 1:
        pyautogui.hotkey("ctrl", "1")
    elif tab_number == 2:
        pyautogui.hotkey("ctrl", "2")
    elif tab_number == 3:
        pyautogui.hotkey("ctrl", "3")
    elif tab_number == 4:
        pyautogui.hotkey("ctrl", "4")
    elif tab_number == 5:
        pyautogui.hotkey("ctrl", "5")
    elif tab_number == 6:
        pyautogui.hotkey("ctrl", "6")
    elif tab_number == 7:
        pyautogui.hotkey("ctrl", "7")
    elif tab_number == 8:
        pyautogui.hotkey("ctrl", "8")

    return f"Switched to tab {tab_number}."

def browser_close_tab():
    pyautogui.hotkey("ctrl", "w")
    return "Tab closed."

def browser_focus_search():
    pyautogui.hotkey("ctrl", "l")
    return "Search bar focused."

def browser_type_text(text):
    browser_focus_search()
    pyautogui.write(str(text), interval=0.01)
    return "Text entered."

def browser_backspace():
    pyautogui.press("backspace")
    return "Deleted the previous character."

def browser_delete_word():
    pyautogui.hotkey("ctrl", "shift", "left")
    pyautogui.press("backspace")
    return "Deleted the previous word."

def browser_clear_search():
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")
    return "Search bar cleared."

def browser_search():
    pyautogui.press("enter")
    return "Search submitted."

def browser_skip_forward():
    pyautogui.press("l")
    return "Skipped forward 10 seconds."

def browser_skip_backward():
    pyautogui.press("j")
    return "Skipped backward 10 seconds."

def _activate_chrome_window():
    """Bring an existing Chrome window to the foreground when possible."""
    try:
        chrome_windows = [
            window for window in gw.getAllWindows()
            if window.title and "chrome" in window.title.lower()
        ]
        if not chrome_windows:
            return False

        window = next(
            (item for item in chrome_windows
             if "youtube" in item.title.lower()),
            chrome_windows[0]
        )
        if window.isMinimized:
            window.restore()
        window.activate()
        time.sleep(0.5)
        return True
    except Exception as error:
        print("Could not activate Chrome:", repr(error))
        return False


# Stores YouTube search results and selection for the current session.
youtube_search_query = ""
youtube_search_results = []
youtube_selected_video = None

youtube_homepage_selection_active = False


def browser_search_youtube(query):
    """Show YouTube search in the existing Chrome tab and collect up to five results."""
    global youtube_search_query, youtube_search_results, youtube_selected_video

    from urllib.parse import quote_plus

    query = str(query).strip()
    if not query:
        return "Tell me what you want to search for on YouTube."

    search_url = "https://www.youtube.com/results?search_query=" + quote_plus(query)

    # Display the search in the user's existing Chrome window/tab.
    if _activate_chrome_window():
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.2)
        pyautogui.write(search_url, interval=0.005)
        pyautogui.press("enter")
    else:
        # If Chrome is not open, launch it at the search URL.
        try:
            subprocess.Popen([CHROME_PATH, search_url])
        except Exception as error:
            print("Could not open YouTube:", repr(error))
            return "I couldn't open YouTube. Please make sure Chrome is installed."

    # Collect result titles in a separate headless session. Do not reuse the
    # user's Chrome profile; that can cause profile-lock and session errors.
    driver = None
    results = []
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        options = Options()
        options.binary_location = CHROME_PATH
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,900")

        driver = webdriver.Chrome(options=options)
        driver.get(search_url)
        wait = WebDriverWait(driver, 20)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "ytd-video-renderer")
            )
        )

        for video in driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer"):
            try:
                link = video.find_element(By.CSS_SELECTOR, "a#video-title")
                title = link.text.strip()
                url = link.get_attribute("href")
                if title and url and "/watch?" in url:
                    if not any(item["url"] == url for item in results):
                        results.append({"title": title, "url": url})
                if len(results) >= 5:
                    break
            except Exception:
                continue

    except Exception as error:
        print("YouTube result collection error:", repr(error))
        return (
            "I opened the YouTube search, but couldn't collect the video list. "
            "Check that Selenium and ChromeDriver are working."
        )
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass

    if not results:
        return "I opened YouTube, but couldn't find any usable video results."

    youtube_search_query = query
    youtube_search_results = results
    youtube_selected_video = None

    print(f"YouTube search results for: {query}")
    for number, result in enumerate(results, start=1):
        print(f"{number}. {result['title']}")

    choices = " ".join(
        f"Video {number}: {result['title']}."
        for number, result in enumerate(results, start=1)
    )
    return (
        f"I found {len(results)} videos for {query}. "
        f"{choices} Say select video one through five."
    )



def browser_select_youtube_video(index=1):
    """Focus a YouTube homepage video without playing it."""
    if not _activate_chrome_window():
        return "I couldn't find an open Chrome window."

    try:
        index = int(index)
    except (TypeError, ValueError):
        index = 1

    if index != 1:
        return "For homepage navigation, say select the first video, then use the arrow commands."

    # Escape browser/page overlays, then move keyboard focus onto the page.
    pyautogui.press("esc")
    pyautogui.press("tab", presses=8, interval=0.08)

    return (
        "Attempted to focus the first homepage video. "
        "Check that the visible outline is on the intended video. "
        "Nothing has been played."
    )
def browser_select_youtube_video(index=1):
    """Focus a YouTube homepage video without playing it."""
    if not _activate_chrome_window():
        return "I couldn't find an open Chrome window."

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By

        options = Options()
        options.debugger_address = "127.0.0.1:9222"
        driver = webdriver.Chrome(options=options)

        videos = driver.find_elements(
            By.CSS_SELECTOR,
            "ytd-rich-item-renderer a#thumbnail"
        )

        videos = [
            video for video in videos
            if video.is_displayed()
            and video.get_attribute("href")
            and "/watch?" in video.get_attribute("href")
        ]

        if not videos:
            return "I couldn't find visible video cards on the YouTube homepage."

        index = int(index)
        if index < 1 or index > len(videos):
            return f"Choose a video between 1 and {len(videos)}."

        video = videos[index - 1]

        driver.execute_script("""
            arguments[0].scrollIntoView({
                behavior: 'instant',
                block: 'center'
            });
            arguments[0].focus({preventScroll: true});
            arguments[0].style.outline = '4px solid #00aaff';
            arguments[0].style.outlineOffset = '3px';
        """, video)

        title = video.get_attribute("aria-label") or "Selected video"
        return f"Focused video {index}: {title}. Nothing has been played."

    except Exception as error:
        print("YouTube selection error:", repr(error))
        return (
            "Couldn't focus the video. Make sure Chrome is running "
            "with remote debugging enabled on port 9222."
        )



def browser_navigate_youtube_selection(direction):
    """Move keyboard focus around the YouTube homepage."""
    if not _activate_chrome_window():
        return "I couldn't find an open Chrome window."

    direction = str(direction).lower().strip()

    key_map = {
        "right": "right",
        "left": "left",
        "up": "up",
        "down": "down",
        "next": "right",
        "previous": "left",
    }

    key = key_map.get(direction)
    if not key:
        return "Say up, down, left, right, next, or previous."

    pyautogui.press(key)
    return f"Pressed {direction}. Check the visible focus outline."


def browser_play_selected_youtube_video():
    """Activate the currently keyboard-focused YouTube item."""
    if not _activate_chrome_window():
        return "I couldn't find an open Chrome window."

    pyautogui.press("enter")
    return "Pressed Enter on the currently focused item."



# -------------------------
# Window Control Tool
# -------------------------

import pygetwindow as gw


def find_window(target):
    target = target.lower().strip()

    windows = [
        window for window in gw.getAllWindows()
        if window.title
    ]

    # Exact match first
    for window in windows:
        if window.title.lower() == target:
            return window

    # Partial match
    for window in windows:
        if target in window.title.lower():
            return window

    return None


def minimize_window(target):
    window = find_window(target)

    if window is None:
        return f"I couldn't find the window {target}."

    try:
        window.minimize()
        return f"Minimized {target}."
    except Exception:
        return f"I couldn't minimize {target}."


def maximize_window(target):
    window = find_window(target)

    if window is None:
        return f"I couldn't find the window {target}."

    try:
        window.maximize()
        return f"Maximized {target}."
    except Exception:
        return f"I couldn't maximize {target}."


def activate_window(target):
    window = find_window(target)

    if window is None:
        return f"I couldn't find the window {target}."

    try:
        window.activate()
        return f"Switched to {target}."
    except Exception:
        return f"I couldn't switch to {target}."


def close_window(target):
    window = find_window(target)

    if window is None:
        return f"I couldn't find the window {target}."

    try:
        window.close()
        return f"Closed {target}."
    except Exception:
        return f"I couldn't close {target}."

# -------------------------
# Tool Registry
# -------------------------

TOOLS = {
    "browser_scroll_up": {"function": browser_scroll_up, "description": "Scrolls the active browser page up.", "requires_input": False},
    "browser_scroll_down": {"function": browser_scroll_down, "description": "Scrolls the active browser page down.", "requires_input": False},
    "browser_back": {"function": browser_go_back, "description": "Goes back one browser page.", "requires_input": False},
    "browser_forward": {"function": browser_go_forward, "description": "Goes forward one browser page.", "requires_input": False},
    "browser_refresh": {"function": browser_refresh, "description": "Refreshes the active browser page.", "requires_input": False},
    "browser_new_tab": {"function": browser_new_tab, "description": "Opens a new browser tab.", "requires_input": False},
    "browser_next_tab": {"function": browser_next_tab,"description": "Switches to the next browser tab.","requires_input": False},
    "browser_previous_tab": {"function": browser_previous_tab,"description": "Switches to the previous browser tab.","requires_input": False},
    "browser_switch_to_tab": {"function": browser_switch_to_tab,"description": "Switches directly to a specific browser tab from 1 to 8.","requires_input": True},
    "browser_close_tab": {"function": browser_close_tab, "description": "Closes the active browser tab.", "requires_input": False},
    "browser_focus_search": {"function": browser_focus_search, "description": "Focuses the browser address/search field.", "requires_input": False},
    "browser_type_text": {"function": browser_type_text, "description": "Types text into the browser address/search field.", "requires_input": True},
    "browser_backspace": {"function": browser_backspace, "description": "Deletes the previous character from the active browser field.", "requires_input": False},
    "browser_delete_word": {"function": browser_delete_word, "description": "Deletes the previous word from the active browser field.", "requires_input": False},
    "browser_clear_search": {"function": browser_clear_search, "description": "Clears the active browser address/search field.", "requires_input": False},
    "browser_search_youtube": {"function": browser_search_youtube,"description": "Searches YouTube for a user-provided topic and stores the top five results.","requires_input": True},
    "browser_select_youtube_video": {"function": browser_select_youtube_video,"description": "Focuses the first YouTube homepage video without playing it.","requires_input": True},
    "browser_navigate_youtube_selection": {"function": browser_navigate_youtube_selection,"description": "Moves keyboard focus around the YouTube homepage without playing a video.","requires_input": True},
    "browser_play_selected_youtube_video": {"function": browser_play_selected_youtube_video,"description": "Activates the currently focused YouTube item using Enter.","requires_input": False},
    "browser_search": {"function": browser_search, "description": "Submits the current browser search/address entry.", "requires_input": False},
    "calculator": {
        "function": calculate,
        "description": "Performs mathematical calculations.",
        "requires_input": True
    },

    "time": {
        "function": get_current_time,
        "description": "Returns the current time.",
        "requires_input": False
    },

    "date": {
        "function": get_current_date,
        "description": "Returns the current date.",
        "requires_input": False
    },

    "day": {
        "function": get_current_day,
        "description": "Returns the current day of the week.",
        "requires_input": False
    },

    "year": {
        "function": get_current_year,
        "description": "Returns the current year.",
        "requires_input": False
    },

    "unit_converter": {
        "function": convert_units,
        "description": "Converts between compatible units such as length, weight, and temperature.",
        "requires_input": True
    },
    "weather": {
        "function": get_weather,
        "description": "Returns current weather information for a city.",
        "requires_input": True
    },

    "timer": {
        "function": set_timer,
        "description": "Sets a timer for a specified number of seconds.",
        "requires_input": True
    },

    "reminder": {
        "function": set_reminder,
        "description": "Sets a reminder that displays a message after a specified amount of time.",
        "requires_input": True
    },

    "website_launcher": {
    "function": open_website,
    "description": "Opens websites in the default web browser.",
    "requires_input": True
    },

    "application_launcher": {
        "function": launch_application,
        "description": "Opens applications installed on the Windows computer.",
        "requires_input": True
    },

    "volume_up": {
        "function": increase_volume,
        "description": "Increases the system volume.",
        "requires_input": False
    },

    "volume_down": {
        "function": decrease_volume,
        "description": "Decreases the system volume.",
        "requires_input": False
    },

    "volume_mute": {
        "function": mute_volume,
        "description": "Mutes the system volume.",
        "requires_input": False
    },

    "volume_unmute": {
        "function": unmute_volume,
        "description": "Unmutes the system volume.",
        "requires_input": False
    },

    "volume_set": {
        "function": set_volume,
        "description": "Sets the system volume to a specific percentage.",
        "requires_input": True
    },

    "media_play_pause": {
        "function": media_play_pause,
        "description": "Plays or pauses the current media.",
        "requires_input": False
    },

    "media_next": {
        "function": media_next,
        "description": "Skips to the next media track.",
        "requires_input": False
    },

    "media_previous": {
        "function": media_previous,
        "description": "Goes back to the previous media track.",
        "requires_input": False
    },


    "open_path": {
        "function": open_path,
        "description": "Opens a file or folder on the computer.",
        "requires_input": True
    },

    "search_files": {
        "function": search_files,
        "description": "Searches common user folders for files or folders.",
        "requires_input": True
    },

    "create_folder": {
        "function": create_folder,
        "description": "Creates a new folder on the Desktop or at a supplied path.",
        "requires_input": True
    },

    "take_screenshot": {
        "function": take_screenshot,
        "description": "Takes a screenshot of the full screen and saves it to the Desktop.",
        "requires_input": False
    },

    "lock_computer": {
        "function": lock_computer,
        "description": "Locks the Windows computer.",
        "requires_input": False
    },
    "window_minimize": {
        "function": minimize_window,
        "description": "Minimizes a specific application window.",
        "requires_input": True
    },

    "window_maximize": {
        "function": maximize_window,
        "description": "Maximizes a specific application window.",
        "requires_input": True
    },

    "window_activate": {
        "function": activate_window,
        "description": "Switches to and activates a specific application window.",
        "requires_input": True
    },

    "system_info": {
        "function": get_system_info,
        "description": "Provides CPU, RAM, disk, operating system, and processor information.",
        "requires_input": False
    },

    "window_close": {
        "function": close_window,
        "description": "Closes a specific application window.",
        "requires_input": True
    },

    "browser_skip_forward": {
        "function": browser_skip_forward,
        "description": "Skips the active YouTube video forward by 10 seconds.",
        "requires_input": False
    },

    "browser_skip_backward": {
        "function": browser_skip_backward,
        "description": "Skips the active YouTube video backward by 10 seconds.",
        "requires_input": False
    },
}

# -------------------------
# Test
# -------------------------

if __name__ == "__main__":

    print("Available tools:")
    print(list(TOOLS.keys()))

    print("Calculator:", TOOLS["calculator"]["function"]("25 * 48"))
    print("Time:", TOOLS["time"]["function"]())
    print("Weather:", TOOLS["weather"]["function"]("Hyderabad"))

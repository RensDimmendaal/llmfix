#!/usr/bin/env -S uv run 
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "claudette",
#     "pynput",
#     "pyperclip",
#     "rumps",
#     "pillow",
#     "pyobjc",
# ]
# ///
import rumps, time, pyperclip, threading, base64, subprocess, tempfile, os
from pynput.keyboard import Key, Controller, Listener
from claudette import Chat
from PIL import Image
from io import BytesIO
from Cocoa import NSScreen, NSEvent

keyboard = Controller()

COMMAND_CODES = {
    "//CC": "// edit to be clear and concise",
    "//FF": "// edit to be friendly and informal",
    "//BLUF": "// edit to bring the bottom line upfront",
    "//DOH": "// edit to fix typo's and spelling mistakes",
    "//MD": "// transform to markdown",
    "//FS": "// make fastai style. concise, short var names, as much on one line as possible, but no `;`. Dont add ``python codefence.",
    "//SS": "",  # Screenshot mode
}

def replace_all(text, replacements):
    for old, new in replacements.items(): text = text.replace(old, new)
    return text

def resize_for_claude(img, max_pixels=1_150_000):
    w, h = img.size
    current_pixels = w * h
    if current_pixels <= max_pixels: return img
    ratio = (max_pixels / current_pixels) ** 0.5
    new_w, new_h = int(w * ratio), int(h * ratio)
    return img.resize((new_w, new_h), Image.LANCZOS)

def img_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def get_active_display():
    screens, mouse_location = NSScreen.screens(), NSEvent.mouseLocation()
    for i, screen in enumerate(screens):
        frame = screen.frame()
        if (frame.origin.x <= mouse_location.x <= frame.origin.x + frame.size.width and frame.origin.y <= mouse_location.y <= frame.origin.y + frame.size.height): return i + 1
    return 1

def capture_active_screen():
    active_display = get_active_display()
    fh, filepath = tempfile.mkstemp(".png")
    os.close(fh)
    subprocess.run(['screencapture', '-x', '-D', str(active_display), filepath])
    img = Image.open(filepath)
    img.load()
    os.unlink(filepath)
    return img

def llm(inp: str):
    prompt = (
        "Below is the text a user copied to their clipboard along with a screenshot. "
        "It contains a mix of text and instructions for you to fix. "
        "Apply the fixes and return only the text that the user should see. "
        "It will be applied to their clipboard so they can paste it. "
        "If the user says something like // DO THIS you can be sure it's an instruction. "
        "RETURN ONLY THE OUTPUT, NO YAPPING. NO PREAMBLE NO SIGN OFF.\n"
        "<user text>\n"
        f"{replace_all(inp, COMMAND_CODES)}\n"
        "</user text>"
    ).strip()
    if "//SS" in inp:
        screenshot = capture_active_screen()
        resized = resize_for_claude(screenshot)
        prompt= [dict(type="image", source=dict(type="base64", media_type="image/png", data=img_to_base64(resized))), dict(type="text", text=prompt)]
        model = "claude-sonnet-4-20250514"
    else: model = "claude-3-5-haiku-20241022"
    return Chat(model)(prompt).content[0].text

class HotkeyListener:
    def __init__(self, fix_callback):
        self.fix_callback = fix_callback
        self.pressed_keys = set()
        self.listener = None
        
    def start(self):
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        
    def stop(self):
        if self.listener: self.listener.stop()
            
    def on_press(self, key):
        self.pressed_keys.add(key)
        if (Key.cmd in self.pressed_keys and Key.ctrl in self.pressed_keys and hasattr(key, 'char') and key.char == 'j'):
            threading.Thread(target=self.fix_callback, daemon=True).start()
            
    def on_release(self, key): self.pressed_keys.discard(key)

class ToolbarApp(rumps.App):
    def __init__(self):
        super().__init__("App")
        self.title = "L"
        self.hotkey_listener = HotkeyListener(self.fix)
        
    def run(self):
        self.hotkey_listener.start()
        try: super().run()
        finally: self.hotkey_listener.stop()

    @rumps.clicked(f"Fix")
    def fix(self, _=None):
        self.title = "..."
        old_clipboard = pyperclip.paste()

        with keyboard.pressed(Key.cmd):
            keyboard.tap("c")
        time.sleep(0.1)
        if inp := pyperclip.paste():
            pyperclip.copy(llm(inp))
        with keyboard.pressed(Key.cmd):
            keyboard.tap("v")
        time.sleep(0.1)

        pyperclip.copy(old_clipboard)
        self.title = "L"

if __name__ == "__main__":
    app = ToolbarApp()
    app.run()

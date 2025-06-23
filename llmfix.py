# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "claudette",
#     "pynput",
#     "pyperclip",
#     "rumps",
# ]
# ///
import rumps
from pynput.keyboard import Key, Controller, Listener
import time
import pyperclip
from claudette import Chat
import threading

KEYBOARD_SHORTCUT = "<cmd>+<shift>+<alt>+<ctrl>+f"
COMMAND_CODES = {
    "//CC": "// edit to be clear and concise",
    "//FF": "// edit to be friendly and informal",
    "//BLUF": "// edit to bring the bottom line to the front",
    "//DOH": "// edit to fix typo's and spelling mistakes",
    "//MD": "// transform to markdown",
}


def replace_all(text, replacements):
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def llm(inp: str):
    return (
        Chat("claude-3-5-haiku-20241022")(
            f"""        
Below is the text a user copied to their clipboard. It contains a mix of text and instructions for you to fix. Apply the fixes and return only the text that the user should see. It will be applied to their clipboard so they can paste it. if the user says something like // DO THIS you can be sure it's an instruction.
RETURN ONLY THE OUTPUT, NO YAPPING. NO PREAMBLE NO SIGN OFF.
<user text>
{replace_all(inp, COMMAND_CODES)}
</user text>
""".strip()
        )
        .content[0]
        .text
    )


keyboard = Controller()


class HotkeyListener:
    def __init__(self, fix_callback):
        self.fix_callback = fix_callback
        self.pressed_keys = set()
        self.listener = None
        
    def start(self):
        self.listener = Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()
        
    def stop(self):
        if self.listener:
            self.listener.stop()
            
    def on_press(self, key):
        self.pressed_keys.add(key)
        # Check for the hotkey combination: cmd+shift+alt+ctrl+f
        if (Key.cmd in self.pressed_keys and 
            Key.shift in self.pressed_keys and 
            Key.alt in self.pressed_keys and 
            Key.ctrl in self.pressed_keys and 
            hasattr(key, 'char') and key.char == 'f'):
            # Run the fix callback in a separate thread to avoid blocking
            threading.Thread(target=self.fix_callback, daemon=True).start()
            
    def on_release(self, key):
        self.pressed_keys.discard(key)


class ToolbarApp(rumps.App):
    def __init__(self):
        super().__init__("App")
        self.title = "L"
        self.hotkey_listener = HotkeyListener(self.fix)
        
    def run(self):
        self.hotkey_listener.start()
        try:
            super().run()
        finally:
            self.hotkey_listener.stop()

    @rumps.clicked(f"Fix ({KEYBOARD_SHORTCUT})")
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

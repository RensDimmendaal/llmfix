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
from pynput.keyboard import Key, Controller, GlobalHotKeys
import time
import pyperclip
from claudette import Chat

KEYBOARD_SHORTCUT = "<cmd>+<shift>+<alt>+<ctrl>+f"
COMMAND_CODES = {
    "//CC": "// edit to be clear and concise",
    "//FF": "// edit to be friendly and informal",
    "//BLUF": "// edit to bring the bottom line to the front",
    "//DOH": "// edit to fix typo's and spelling mistakes",
    "//MD": "// transform to markdown",
}

def replace_all(text, replacements):
     for old, new in replacements.items(): text = text.replace(old, new)
     return text

def llm(inp: str):
    return Chat("claude-3-5-haiku-20241022")(f"""        
Below is the text a user copied to their clipboard. It contains a mix of text and instructions for you to fix. Apply the fixes and return only the text that the user should see. It will be applied to their clipboard so they can paste it. if the user says something like // DO THIS you can be sure it’s an instruction.
RETURN ONLY THE OUTPUT, NO YAPPING. NO PREAMBLE NO SIGN OFF.
<user text>
{replace_all(inp, COMMAND_CODES)}
</user text>
""".strip()).content[0].text

keyboard = Controller()

class ToolbarApp(rumps.App):
    def __init__(self):
        super().__init__("App")
        self.title = "L"

    @rumps.clicked(f"Fix ({KEYBOARD_SHORTCUT})")
    def fix(self,_=None):
        self.title = "..."
        old_clipboard = pyperclip.paste()

        with keyboard.pressed(Key.cmd): keyboard.tap('c')
        time.sleep(0.1)
        if inp:=pyperclip.paste():  pyperclip.copy(llm(inp))
        with keyboard.pressed(Key.cmd): keyboard.tap('v')
        time.sleep(0.1)

        pyperclip.copy(old_clipboard)
        self.title = "L"

if __name__ == "__main__":
    app = ToolbarApp()
    with GlobalHotKeys({KEYBOARD_SHORTCUT: app.fix}): app.run()
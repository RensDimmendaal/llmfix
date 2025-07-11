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
import rumps, time, pyperclip, threading, base64, subprocess, tempfile, os, logging, argparse
from pynput.keyboard import Key, Controller, Listener
from claudette import Chat
from PIL import Image
from io import BytesIO
from Cocoa import NSScreen, NSEvent

log = logging.getLogger(__name__)
kb = Controller()

CODES = {
    "//CC": "// edit to be clear and concise",
    "//FF": "// edit to be friendly and informal",
    "//BLUF": "// edit to bring the bottom line upfront",
    "//DOH": "// edit to fix typo's and spelling mistakes",
    "//MD": "// transform to markdown",
    "//FS": "// make fastai style. concise, short var names, as much on one line as possible, but no `;`. Dont add ``python codefence.",
    "//SS": "",
}

def replace_all(txt, reps):
    for old, new in reps.items(): txt = txt.replace(old, new)
    log.debug(f"Text after replacement: {txt[:100]}...")
    return txt

def resize_img(img, max_px=1_150_000):
    w, h = img.size
    px = w * h
    log.debug(f"Image size: {w}x{h} ({px} pixels)")
    if px <= max_px: 
        log.debug("No resize needed")
        return img
    r = (max_px / px) ** 0.5
    nw, nh = int(w * r), int(h * r)
    log.debug(f"Resizing to: {nw}x{nh} (ratio: {r:.2f})")
    return img.resize((nw, nh), Image.LANCZOS)

def img_b64(img):
    buf = BytesIO()
    img.save(buf, format='PNG')
    enc = base64.b64encode(buf.getvalue()).decode('utf-8')
    log.debug(f"Encoded to base64 ({len(enc)} chars)")
    return enc

def get_active_display():
    screens, mouse = NSScreen.screens(), NSEvent.mouseLocation()
    log.debug(f"Mouse: ({mouse.x}, {mouse.y}), {len(screens)} screens")
    for i, s in enumerate(screens):
        f = s.frame()
        log.debug(f"Screen {i+1}: {f.origin.x}, {f.origin.y}, {f.size.width}, {f.size.height}")
        if f.origin.x <= mouse.x <= f.origin.x + f.size.width and f.origin.y <= mouse.y <= f.origin.y + f.size.height: 
            log.debug(f"Active display: {i+1}")
            return i + 1
    log.debug("Defaulting to display 1")
    return 1

def capture_screen():
    log.debug("Starting capture")
    disp = get_active_display()
    fh, fp = tempfile.mkstemp(".png")
    os.close(fh)
    log.debug(f"Capturing screen {disp} to {fp}")
    subprocess.run(['screencapture', '-x', '-D', str(disp), fp])
    img = Image.open(fp)
    img.load()
    os.unlink(fp)
    log.debug("Capture done")
    return img

def llm(inp: str):
    log.debug(f"LLM input ({len(inp)} chars): {inp[:100]}...")
    prompt = (
        "Below is the text a user copied to their clipboard along with a screenshot. "
        "It contains a mix of text and instructions for you to fix. "
        "Apply the fixes and return only the text that the user should see. "
        "It will be applied to their clipboard so they can paste it. "
        "If the user says something like // DO THIS you can be sure it's an instruction. "
        "RETURN ONLY THE OUTPUT, NO YAPPING. NO PREAMBLE NO SIGN OFF.\n"
        "<user text>\n"
        f"{replace_all(inp, CODES)}\n"
        "</user text>"
    ).strip()
    
    if "//SS" in inp:
        log.info("Screenshot mode")
        ss = capture_screen()
        resized = resize_img(ss)
        prompt = [dict(type="image", source=dict(type="base64", media_type="image/png", data=img_b64(resized))), dict(type="text", text=prompt)]
        model = "claude-sonnet-4-20250514"
        log.info(f"Using {model} with screenshot")
    else: 
        model = "claude-3-5-haiku-20241022"
        log.debug(f"Using {model}")
    
    try:
        log.debug("Sending to LLM...")
        res = Chat(model)(prompt).content[0].text
        log.debug(f"Response ({len(res)} chars): {res[:100]}...")
        return res
    except Exception as e:
        log.error(f"LLM failed: {e}")
        raise

class HotkeyListener:
    def __init__(self, cb):
        self.cb, self.keys, self.listener = cb, set(), None
        log.debug("HotkeyListener init")
        
    def start(self):
        log.debug("Starting listener")
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        
    def stop(self):
        log.debug("Stopping listener")
        if self.listener: self.listener.stop()
            
    def on_press(self, key):
        self.keys.add(key)
        if Key.cmd in self.keys and Key.ctrl in self.keys and hasattr(key, 'char') and key.char == 'j':
            log.info("Hotkey detected! (Cmd+Ctrl+J)")
            threading.Thread(target=self.cb, daemon=True).start()
            
    def on_release(self, key): self.keys.discard(key)

class ToolbarApp(rumps.App):
    def __init__(self):
        super().__init__("App")
        self.title = "L"
        self.hotkey = HotkeyListener(self.fix)
        log.debug("App init")
        
    def run(self):
        log.info("Starting app")
        self.hotkey.start()
        try: super().run()
        finally: self.hotkey.stop()

    @rumps.clicked(f"Fix")
    def fix(self, _=None):
        log.info("Fix called")
        self.title = "..."
        old = pyperclip.paste()
        log.debug(f"Saved clipboard ({len(old)} chars)")

        log.debug("Copying with Cmd+C")
        with kb.pressed(Key.cmd): kb.tap("c")
        time.sleep(0.1)
        
        if inp := pyperclip.paste():
            log.debug(f"Got input ({len(inp)} chars): {inp[:100]}...")
            try:
                res = llm(inp)
                log.debug("LLM done, copying result")
                pyperclip.copy(res)
            except Exception as e:
                log.error(f"Error: {e}")
        else:
            log.warning("No input")
            
        log.debug("Pasting with Cmd+V")
        with kb.pressed(Key.cmd): kb.tap("v")
        time.sleep(0.1)

        log.debug("Restoring clipboard")
        pyperclip.copy(old)
        self.title = "L"
        log.info("Fix done")

def setup_logging(lvl):
    level = getattr(logging, lvl.upper())
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    log.setLevel(level)

def main():
    p = argparse.ArgumentParser(description='LLM Fix')
    p.add_argument('--log-level', '-l', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO')
    args = p.parse_args()
    setup_logging(args.log_level)
    log.info("Starting llmfix")
    ToolbarApp().run()

if __name__ == "__main__": main()

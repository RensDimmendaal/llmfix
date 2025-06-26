# LLMFix
> Transform any selected text with AI instantly - no copy-paste, no app switching, just select and fix

## Get Started

You write text all day, but fixing tone, clarity, or typos means switching apps and losing flow. LLMFix solves this: select any text anywhere on your Mac, hit a hotkey, and watch it transform instantly.

**Prerequisites**: Install [uv](https://docs.astral.sh/uv/getting-started/installation/)

1. **Clone and setup**:
   ```bash
   git clone git@github.com:AnswerDotAI/llmfix.git
   cd llmfix
   export ANTHROPIC_API_KEY="your_api_key_here"
   chmod +x llmfix.py
   ```

2. **Grant permissions**: Go to `System Preferences → Security & Privacy → Accessibility` and add your terminal app

![image](https://github.com/user-attachments/assets/09c8ef78-01cf-4265-b1be-b82d9972069c)


4. **Run the app**: `./llmfix.py`

5. **Test it**: 
   - Type in any text field: "Hi Squidward how's it going? // MAKE SPONGEBOB CASE"
   - Select the text and click the 'L' icon in your menu bar, then select "Fix", or use the hotkey `cmd+ctrl+j`
   - Your text becomes something like: "hI sQuIdWaRd HoW's It GoInG?"

Success! You can now use LLMFix to fix your text.

## Next Steps

Try out these additional features:

### Use built-in commands

Add these codes to any text for useful transformations:

- `//CC` - Make text clear and concise
- `//FF` - Make text friendly and informal  
- `//BLUF` - Put the bottom line up front
- `//DOH` - Fix typos and spelling mistakes
- `//MD` - Transform to markdown format

You can customize the commands by editing the `COMMAND_CODES` dictionary in the `llmfix.py` file.

### Add screenshots

If you add the `//SS` command, LLMFix captures a screenshot and uses it as additional context. 
This can be useful when you have a text editor open alongside another file with relevant information. 
If you have multiple monitors, then a screenshot of the monitor where your mouse is will be sent to llmfix.

### Customize the hotkey

You can change the hotkey by editing the `on_press` method in the `llmfix.py` file.

**Pro tip:** remap caps lock to `cmd+shift+alt+ctrl` using [Karabiner Elements](https://karabiner-elements.pqrs.org/) - then you can trigger fixes with just `capslock+<letter>`.
Then your hotkey is not only easier to use, but also less likely to conflict with other apps.

```python
# Example of a more complex hotkey setup
  if (Key.cmd in self.pressed_keys and 
      Key.ctrl in self.pressed_keys and 
      Key.shift in self.pressed_keys and 
      Key.alt in self.pressed_keys and 
      hasattr(key, 'char') and key.char == 'f'):
```

### Bring your own LLM

If you don't like using Claude, you can change the `llm` function to use any other model or API.


### Make it work on other platforms

This is a Mac only app. You can modify it for other platforms by:

1. replacing the rumps menu bar functionality.
2. replacing the screenshot functionality (we use mac specific features to detect active monitor).

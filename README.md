# LLMFix
> Transform any selected text with AI instantly - no copy-paste, no app switching, just select and fix

## Get Started

You write text all day, but fixing tone, clarity, or typos means switching apps and losing flow. LLMFix solves this: select any text anywhere on your Mac, hit a hotkey, and watch it transform instantly.

**Prerequisites**: Install [uv](https://docs.astral.sh/uv/getting-started/installation/)

1. **Clone and setup**:
   ```bash
   git clone https://github.com/AnswerDotAI/llmfix.git
   cd llmfix
   export ANTHROPIC_API_KEY="your_api_key_here"
   chmod +x llmfix.py
   ```

2. **Run the app**: `./llmfix.py`

3. **Grant permissions**: When prompted, go to `System Preferences → Security & Privacy → Input Monitoring` and add your terminal app

4. **Test it**: 
   - Type "Would you please be so kind and try this out //FF" in any text field
   - Select the text and click the 'L' icon in your menu bar, then select "Fix"
   - Your text becomes something like: "Hey, give this a try!"

## Next Steps

### Master the keyboard shortcut

The default hotkey is `cmd+shift+alt+ctrl+f`. This complex combination prevents conflicts with other apps. 

**Pro tip**: Remap caps lock to `cmd+shift+alt+ctrl` using [Karabiner Elements](https://karabiner-elements.pqrs.org/) - then you can trigger fixes with just `capslock+f`.

### Use built-in commands

Add these codes to any text for useful transformations:
- `//CC` - Make text clear and concise
- `//FF` - Make text friendly and informal  
- `//BLUF` - Put the bottom line up front
- `//DOH` - Fix typos and spelling mistakes
- `//MD` - Transform to markdown format

### Create custom commands

Any text after `//` becomes a command. Try:

```
Hi Squidward how's it going? // MAKE SPONGEBOB CASE
```

Result: `hI sQuIdWaRd HoW's It GoInG?`

### Customize the app

**Change the hotkey**  you can change the hotkey by editing the `on_press` method.

**Add preset commands** you can add preset commands by editing the `COMMAND_CODES` dictionary:

```python
COMMAND_CODES = {
    ...
    "//FORMAL": "// make this more professional",
    "//ELI5": "// explain like I'm 5 years old",
}
```


## FAQ

**Mac only?** Yes, but you can modify it for other platforms by replacing the rumps menu bar functionality.

**Claude only?** Yes, but you can swap the `llm` function for any other model or API.

**Why the complex hotkey?** It ensures no conflicts with existing app shortcuts. Much easier with caps lock remapped!


# LLMFix

Transform selected text with AI using customizable command codes and hotkeys.

## What is LLMFix?

LLMFix is a lightweight macOS utility that lets you quickly transform selected text using Claude AI. With a configurable keyboard shortcut, you can instantly edit, fix, or transform your text without interrupting your workflow.

## Features

1. **Global Hotkey**: Trigger text transformations from anywhere with a keyboard shortcut (default is `cmd + shift + option + ctrl + f`)
2. **Command Codes**: Use shorthand codes to apply specific transformations (e.g. //CC for clear and concise)
3. **Non-Intrusive**: Works with your clipboard without disrupting its contents
4. **Menu Bar App**: Simple status indicator in your menu bar
5. **Customizable**: This app is just a single python file, so you can customize it to your liking.

## Setup

### API Key
LLMFix uses Anthropic's Claude AI under the hood, so you'll need an Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

### Installation

## Usage

We recommend using [uv](https://docs.astral.sh/uv/getting-started/installation/)to run the script in an isolated virtual environment:

```bash
uv run llmfix.py
```

You might get prompted with "This process is not trusted! Input event monitoring will not be possible until it is added to accessibility clients." You can add it by going to `System Preferences -> Security & Privacy -> Input Monitoring` and adding the terminal app you use to run this script.

After running the script, you should see a new icon in your menu bar.
Now write some text for example "hey check this out // make it formal", select the text, and press the hotkey.

## Customizing the app

The app is just a single python file, so you can customize it to your liking.

### Customizing the hotkey

To change the hotkey, you can change the `KEYBOARD_SHORTCUT` variable in the script. For example, we like to remap our capslock to the combination of `ctrl+cmd+shift+option` so we can make custom hotkeys that never conflict with anything. On MacOS, you can set this up with apps like [Karabiner Elements](https://karabiner-elements.pqrs.org/) or [HyperKey](https://hyperkey.app/).

### Customizing the command codes

To change the command codes, you can change the `COMMAND_CODES` dictionary in the script.

## Anticipated FAQ

### Is it Mac only?
Yes. We're using [rumps](https://github.com/jaredks/rumps) for the menu bar app functionality, but you can easily remove that and then it would be cross-platform. The core functionality, supported by [pynput](https://github.com/moses-palmer/pynput) would work on Linux and Windows as well.

### Is it Claude only?
Yes. But feel free to replace the `llm` function with another one. You can even use local models as the task of rewriting text is something that most small/medium sized models can easily do.

### Are you going to put this on PyPI?
No. I've written this app three times. Once in swift, but distributing an app in the app store was too much hassle. Second as a pypi package, but even then the friction to publish it was too large. Now, I'm finally just sharing it as a script. Did you know you don't even have to clone the repo. You can run it from the raw url:

```bash
uv run https://raw.githubusercontent.com/answerdotai/llmfix/refs/heads/main/llmfix.py
```

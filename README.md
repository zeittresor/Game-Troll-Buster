# Game Troll Buster v0.2.0

**Game Troll Buster** is a small PyQt6 desktop application that lets a classic
ELIZA-inspired rule engine answer selected **incoming Steam friend chats** with
counter-questions.

<img width="1285" height="837" alt="sinkhole_for_steam trolls" src="https://github.com/user-attachments/assets/a1849fce-dab0-4f39-9e0d-27108c5b1cd7" />

The application itself is English-only by design.

## Highlights

- English PyQt6 interface
- Gamer-style dashboard
- Theme support:
  - Cyber Dark
  - Neon Purple
  - Matrix
  - Hellfire
  - Light
- Separate **Options** dialog
- Three ELIZA personalities:
  - Classic ELIZA
  - Dry Counter-Questions
  - Persistent Mirror
- Random human-like reply delay
- Maximum replies per contact
- Session auto-stop
- Global Pause / Resume button
- Per-contact enable switch
- Built-in Demo Mode
- System tray menu
- One readable `.txt` chat transcript per Steam contact/chat
- Optional timestamps
- Password and Steam Guard codes are not stored in `config.json`
- Game Troll Buster never sends the first message

## Transcript format

By default, logs look like this:

    [Troll]: do you want to support me

    [ELIZA]: Why do you think I would want to support you?

    [Troll]: because I need money

    [ELIZA]: Why do you need money?

Timestamps can optionally be enabled in **Options -> Logging**.

Logs are stored in:

    %USERPROFILE%\.game_troll_buster\chat_logs\

Each contact gets its own text file.

## First start

1. Extract the ZIP.
2. Run `install_and_run.bat`.
3. The installer creates `.venv` inside the Game Troll Buster folder.
4. Dependencies are installed only into that local environment.
5. The application starts in Demo Mode.

Try the built-in `Random Troll [DEMO]` contact with:

    do you want to support me

## Steam mode

Choose **Steam -> Connect**.

The optional network backend uses the open-source Python `steam` package to
connect to Steam's network protocol. Steam Guard prompts are handled in the GUI.

### Compatibility note

Steam friend chat is not exposed as a simple stable public REST endpoint for
arbitrary desktop clients. Valve documents friend-message interception/replying
inside Steamworks, while third-party clients typically use Steam's client
network protocol. Valve can change that protocol.

For that reason `steam_backend.py` is deliberately isolated from the rest of the
application. The GUI, options, themes, logs, and ELIZA engine can continue to
work even if the Steam transport layer later needs an update.

## Safety / loop protection

The responder only acts when all of these are true:

- a message is incoming;
- that contact is explicitly enabled;
- the global responder is not paused;
- the contact has not hit its reply limit;
- the configured session auto-stop has not been reached.

This avoids accidentally responding to every friend and reduces the chance of
an endless bot-to-bot loop.

## Local data

    %USERPROFILE%\.game_troll_buster\

Contains:

- `config.json`
- `chat_logs\`
- `steam\` session/sentry material used by the Steam library

## Windows EXE build

After running the installer once:

    build_exe.bat

The packaged application is created in:

    dist\Game Troll Buster\

## Files

- `app.py` - PyQt6 GUI
- `eliza_engine.py` - rule-based ELIZA engine
- `steam_backend.py` - optional Steam transport
- `storage.py` - configuration and text transcripts
- `themes.py` - visual themes
- `assets\game_troll_buster.svg` - app artwork

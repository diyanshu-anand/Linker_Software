# LINKER SOFTWARE

**Google Drive Image Link Converter | Version 1.0.0**

LINKER SOFTWARE is a desktop application that converts publicly shared Google Drive image links into proxy URLs suitable for embedding images on websites and other platforms. It also supports batch conversion, downloading images with an optional logo watermark, and reviewing recent conversions—all through a dark-themed graphical interface.

> **Important:** This version processes **Google Drive file links**, not Google Photos share links. Make sure each image is shared with **Anyone with the link** before converting it.

## Features

- **Website-ready image links:** Converts supported Google Drive URLs into `images.weserv.nl` proxy URLs.
- **Batch conversion:** Paste multiple links, one per line, and process them together.
- **Image downloads:** Downloads accessible images and saves them as PNG files in the `watermarked/` folder.
- **Logo watermark:** Applies a subtle, centered watermark when `logo.png` is available; otherwise saves the image without it.
- **Recent conversions:** Displays original links, converted URLs, and processing statuses with search and double-click selection.
- **Quick actions:** Paste, clear, copy the last proxy URL, preview it in a browser, or open the downloads folder.
- **Responsive processing:** Runs conversion in a background thread with a loading indicator.
- **Update support (in development):** Includes code to check a GitHub-hosted `update.json` and download updates; automatic executable replacement is not implemented in this version.

## How to use

1. Upload an image to **Google Drive**.
2. Open its sharing settings and change **General access** to **Anyone with the link** (Viewer).
3. Copy the file's share link. A supported link typically looks like:

   ```text
   https://drive.google.com/file/d/FILE_ID/view?usp=sharing
   ```

4. Launch LINKER SOFTWARE and paste the link into the **Google Drive Links** box. For multiple images, put each link on a separate line.
5. Click **Convert All**. The app generates proxy URLs and attempts to download each image.
6. Use **Copy** to copy the last generated proxy URL, **Open Image** to preview it, or **Recent Conversions** to select an earlier result. Downloaded PNGs are saved in `watermarked/`.

Example output:

```text
https://images.weserv.nl/?url=drive.google.com/uc?id=FILE_ID
```

**Note:** The conversion service is third-party, and image loading depends on Google Drive access and the service's availability. Do not share private or sensitive images using public links.

## Run from source

**Requirements:** Python 3 with Tkinter, an internet connection, and the Python packages `requests` and `Pillow`.

Install dependencies:

```powershell
py -m pip install requests Pillow
```

Place these files together in the project directory:

```text
project/
├── gssap_gui.py      # Rename your Python source to this, if necessary
├── Linker.png        # Optional application/header logo
├── logo.png          # Optional watermark/background logo
├── icon.ico          # Optional icon for the Windows executable
└── README.md
```

Start the application:

```powershell
py gssap_gui.py
```

The application creates a `watermarked/` folder automatically when it starts. The source uses paths relative to its own location.

## Build a Windows executable

Install PyInstaller:

```powershell
py -m pip install pyinstaller
```

Build a single-window executable from the project directory:

```powershell
pyinstaller --onefile --windowed --icon=icon.ico --add-data "Linker.png;." --add-data "logo.png;." gssap_gui.py
```

The output is normally found at:

```text
dist/gssap_gui.exe
```

**Packaging note:** The current source resolves its logos and output folder relative to `__file__`. A PyInstaller one-file build extracts bundled assets to a temporary directory; update the application's resource/output path handling before distributing it so downloaded images are saved to a persistent, writable location. If you omit the PNG assets, the application can run without those logos and the watermark.

## Keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl + Enter` | Convert links |
| `Ctrl + V` | Paste links |
| `Ctrl + L` | Clear input/output |
| `Ctrl + C` | Copy output URL |

Shortcuts are application-level bindings; use the on-screen buttons when editing text or copying selected text.

## Troubleshooting

- **Invalid Google Drive link:** Use a file URL containing `/file/d/FILE_ID/` or another supported `/d/FILE_ID` format.
- **Image download fails:** Verify that the file is an image, its sharing is set to **Anyone with the link**, and the internet connection is working.
- **Proxy link does not display:** Check public access and try opening the generated URL in a browser. Google Drive and the proxy service may impose access or traffic limits.
- **No watermark appears:** Place a valid `logo.png` alongside the source script.
- **Updates:** This source currently shows a demonstration update popup after startup. The real update checker is present but not enabled in the startup flow, and downloaded updates are not automatically installed.

## Technology

Python · Tkinter · Requests · Pillow · [images.weserv.nl](https://images.weserv.nl/)

## Credits

Researched, engineered, and developed by **Gauranga Creations**.

© Gauranga Creations. All rights reserved. No open-source license is specified in the supplied source.
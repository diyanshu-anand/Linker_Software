# import re

# def convert_drive_link_to_proxy(drive_link):
#     """
#     Converts a Google Drive public file URL to a proxy image URL.
#     """
#     match = re.search(r'/d/([a-zA-Z0-9_-]+)', drive_link)
#     if not match:
#         return "Invalid Google Drive link. Make sure it's in the correct format."
    
#     file_id = match.group(1)
#     return f"https://images.weserv.nl/?url=drive.google.com/uc?id={file_id}"

# def main():
#     print("Google Drive Image Link Converter")
#     print("Paste a public Google Drive link below. Type 'exit' to quit.\n")

#     while True:
#         drive_link = input("Drive Link: ").strip()
#         if drive_link.lower() == "exit":
#             print("Exiting. Goodbye!")
#             break
#         result = convert_drive_link_to_proxy(drive_link)
#         print(f"Converted Link: {result}\n")

# if __name__ == "__main__":
#     main()

# Done by avinash from here - Implementing GUI instead of CLI.
# Modified by divyanshu - adding watermarks, and making entire system newish
#  Auto update feature and some more are left to do....
import tkinter as tk
from tkinter import messagebox, ttk
import re
import webbrowser
import os
import requests
from io import BytesIO
from PIL import Image, ImageTk


# ============================================================
# APPLICATION VERSION
# ============================================================

APP_VERSION = "1.0.0"


# ============================================================
# ORIGINAL CONVERSION LOGIC
# DO NOT CHANGE
# ============================================================

def convert_drive_link_to_proxy(drive_link):
    """
    Converts a Google Drive public file URL to a proxy image URL.
    """
    match = re.search(
        r'/d/([a-zA-Z0-9\_-]+)',
        drive_link
    )

    if not match:
        return (
            "Invalid Google Drive link. "
            "Make sure it's in the correct format."
        )

    file_id = match.group(1)

    return (
        f"https://images.weserv.nl/"
        f"?url=drive.google.com/uc?id={file_id}"
    )


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# Software header logo
UI_LOGO_PATH = os.path.join(
    BASE_DIR,
    "Linker.png"
)

# Gauranga Creation logo
BACKGROUND_LOGO_PATH = os.path.join(
    BASE_DIR,
    "logo.png"
)

# Downloaded images
WATERMARK_DIR = os.path.join(
    BASE_DIR,
    "watermarked"
)

os.makedirs(
    WATERMARK_DIR,
    exist_ok=True
)


# ============================================================
# COLORS
# ============================================================

BG = "#0b1120"
HEADER_BG = "#0f172a"
HEADER_BG_2 = "#111c31"

PANEL = "#111827"
INPUT_BG = "#020617"

BLUE = "#2563eb"
BLUE_HOVER = "#3b82f6"

WHITE = "#f8fafc"
TEXT = "#cbd5e1"
MUTED = "#94a3b8"

BORDER = "#263449"


# ============================================================
# APPLICATION STATE
# ============================================================

history_data = []
last_proxy_url = ""

background_logo_image = None
background_logo_tk = None


# ============================================================
# GOOGLE DRIVE FILE ID
# ============================================================

def get_drive_file_id(drive_link):

    match = re.search(
        r'/d/([a-zA-Z0-9\_-]+)',
        drive_link
    )

    if not match:
        return None

    return match.group(1)


# ============================================================
# SAFE FILE NAME
# ============================================================

def safe_filename(text):

    name = re.sub(
        r'[^a-zA-Z0-9\_-]+',
        '_',
        text
    )

    name = name.strip("_")

    if not name:
        name = "image"

    return name[:60]


# ============================================================
# DIRECT GOOGLE DRIVE DOWNLOAD
# ============================================================

def download_drive_image(drive_link):

    file_id = get_drive_file_id(
        drive_link
    )

    if not file_id:
        raise ValueError(
            "Invalid Google Drive link."
        )

    session = requests.Session()

    download_url = (
        "https://drive.google.com/uc"
        f"?export=download&id={file_id}"
    )

    response = session.get(
        download_url,
        timeout=60,
        allow_redirects=True
    )

    response.raise_for_status()

    content_type = response.headers.get(
        "Content-Type",
        ""
    ).lower()

    # Normal image
    if "image" in content_type:
        return response.content

    # Google Drive confirmation
    html = response.text

    token_match = re.search(
        r'confirm=([0-9A-Za-z\_-]+)',
        html
    )

    if token_match:

        token = token_match.group(1)

        confirm_url = (
            "https://drive.google.com/uc"
            f"?export=download"
            f"&confirm={token}"
            f"&id={file_id}"
        )

        response = session.get(
            confirm_url,
            timeout=60,
            allow_redirects=True
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "image" in content_type:
            return response.content

    # Image signature fallback

    data = response.content

    if (
        data.startswith(b"\x89PNG")
        or data.startswith(b"\xff\xd8")
        or data.startswith(b"GIF")
        or data.startswith(b"RIFF")
        or data.startswith(b"BM")
    ):
        return data

    raise ValueError(
        "Google Drive did not return a valid image."
    )


# ============================================================
# WATERMARK
# ============================================================

def add_center_watermark(
    image,
    logo_path,
    opacity=0.10
):
    """
    Adds a very light centered watermark.

    The original image dimensions remain unchanged.
    """

    if not os.path.exists(
        logo_path
    ):
        return image

    try:

        logo = Image.open(
            logo_path
        ).convert("RGBA")

        image_width, image_height = image.size

        # Watermark maximum size
        max_logo_width = int(
            image_width * 0.30
        )

        max_logo_height = int(
            image_height * 0.30
        )

        logo.thumbnail(
            (
                max_logo_width,
                max_logo_height
            ),
            Image.Resampling.LANCZOS
        )

        # Apply transparency
        alpha = logo.getchannel("A")

        alpha = alpha.point(
            lambda p: int(
                p * opacity
            )
        )

        logo.putalpha(alpha)

        # Center position
        x = (
            image_width - logo.width
        ) // 2

        y = (
            image_height - logo.height
        ) // 2

        base = image.convert(
            "RGBA"
        )

        base.alpha_composite(
            logo,
            (
                x,
                y
            )
        )

        return base

    except Exception as error:

        print(
            "Watermark error:",
            error
        )

        return image


# ============================================================
# SAVE DOWNLOADED IMAGE
# ============================================================

def save_downloaded_image(
    image_bytes,
    original_link,
    index
):

    try:

        image = Image.open(
            BytesIO(image_bytes)
        )

        if image.mode not in (
            "RGB",
            "RGBA"
        ):
            image = image.convert(
                "RGB"
            )

    except Exception:

        raise ValueError(
            "Downloaded file is not a valid image."
        )

    # ========================================================
    # ADD CENTER WATERMARK
    # ========================================================

    image = add_center_watermark(
        image,
        BACKGROUND_LOGO_PATH,
        opacity=0.10
    )

    # ========================================================
    # FILE NAME
    # ========================================================

    safe_name = safe_filename(
        original_link
    )

    output_filename = (
        f"downloaded_{index}_"
        f"{safe_name}.png"
    )

    output_path = os.path.join(
        WATERMARK_DIR,
        output_filename
    )

    image.save(
        output_path,
        "PNG"
    )

    return output_path


# ============================================================
# DOWNLOAD IMAGE
# ============================================================

def download_image(
    proxy_url,
    original_link,
    index
):

    image_bytes = download_drive_image(
        original_link
    )

    return save_downloaded_image(
        image_bytes,
        original_link,
        index
    )


# ============================================================
# GAURANGA CREATION BACKGROUND LOGO
# ============================================================

def prepare_background_logo():

    if not os.path.exists(
        BACKGROUND_LOGO_PATH
    ):

        print(
            "Gauranga Creation logo not found:"
        )

        print(
            BACKGROUND_LOGO_PATH
        )

        return None

    try:

        logo = Image.open(
            BACKGROUND_LOGO_PATH
        ).convert("RGBA")

        original_width, original_height = (
            logo.size
        )

        max_width = 520
        max_height = 360

        scale = min(
            max_width / original_width,
            max_height / original_height
        )

        new_width = max(
            1,
            int(
                original_width * scale
            )
        )

        new_height = max(
            1,
            int(
                original_height * scale
            )
        )

        logo = logo.resize(
            (
                new_width,
                new_height
            ),
            Image.Resampling.LANCZOS
        )

        # UI background transparency
        alpha = logo.getchannel(
            "A"
        )

        alpha = alpha.point(
            lambda p: int(
                p * 0.10
            )
        )

        logo.putalpha(
            alpha
        )

        return logo

    except Exception as error:

        print(
            "Background logo error:",
            error
        )

        return None


# ============================================================
# DRAW BACKGROUND LOGO
# ============================================================

def draw_background_logo():

    global background_logo_tk

    if background_logo_image is None:
        return

    try:

        canvas_width = (
            background_canvas.winfo_width()
        )

        canvas_height = (
            background_canvas.winfo_height()
        )

        if canvas_width <= 1:
            canvas_width = 1100

        if canvas_height <= 1:
            canvas_height = 600

        # Position toward lower-right/center
        x = int(
            canvas_width * 0.72
        )

        y = int(
            canvas_height * 0.62
        )

        background_logo_tk = ImageTk.PhotoImage(
            background_logo_image
        )

        background_canvas.delete(
            "background_logo"
        )

        background_canvas.create_image(
            x,
            y,
            image=background_logo_tk,
            anchor="center",
            tags="background_logo"
        )

        background_canvas.tag_lower(
            "background_logo"
        )

    except Exception as error:

        print(
            "Background draw error:",
            error
        )


# ============================================================
# HISTORY
# ============================================================

def add_history(
    original,
    proxy,
    status,
    saved_path=""
):

    history_data.append(
        {
            "original": original,
            "proxy": proxy,
            "status": status,
            "saved": saved_path
        }
    )

    refresh_history()


def refresh_history():

    for item in history_tree.get_children():

        history_tree.delete(
            item
        )

    search_text = (
        search_var.get()
        .strip()
        .lower()
    )

    for item in history_data:

        combined = (
            item["original"]
            + " "
            + item["proxy"]
            + " "
            + item["status"]
            + " "
            + item["saved"]
        ).lower()

        if (
            search_text
            and search_text not in combined
        ):
            continue

        history_tree.insert(
            "",
            "end",
            values=(
                item["original"],
                item["proxy"],
                item["status"]
            )
        )


# ============================================================
# CONVERT ALL
# ============================================================

def convert_links():

    global last_proxy_url

    raw_text = input_text.get(
        "1.0",
        tk.END
    ).strip()

    if not raw_text:

        messagebox.showwarning(
            "No Links",
            "Please paste at least one Google Drive link."
        )

        return

    links = [
        line.strip()
        for line in raw_text.splitlines()
        if line.strip()
    ]

    success_count = 0
    error_count = 0

    last_valid_proxy = ""

    for index, drive_link in enumerate(
        links,
        start=1
    ):

        # ----------------------------------------------------
        # ORIGINAL CONVERSION LOGIC
        # ----------------------------------------------------

        result = convert_drive_link_to_proxy(
            drive_link
        )

        if result.startswith(
            "Invalid Google Drive link"
        ):

            add_history(
                drive_link,
                result,
                "INVALID"
            )

            error_count += 1

            continue

        proxy_url = result

        last_valid_proxy = proxy_url

        # ----------------------------------------------------
        # DOWNLOAD IMAGE
        # ----------------------------------------------------

        try:

            output_path = download_image(
                proxy_url,
                drive_link,
                index
            )

            add_history(
                drive_link,
                proxy_url,
                "SUCCESS",
                output_path
            )

            success_count += 1

        except Exception as error:

            add_history(
                drive_link,
                proxy_url,
                "ERROR",
                str(error)
            )

            error_count += 1

    # --------------------------------------------------------
    # LAST PROXY URL
    # --------------------------------------------------------

    if last_valid_proxy:

        last_proxy_url = (
            last_valid_proxy
        )

        output_entry.delete(
            0,
            tk.END
        )

        output_entry.insert(
            0,
            last_proxy_url
        )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    if (
        success_count > 0
        and error_count == 0
    ):

        messagebox.showinfo(
            "Conversion Complete",
            f"Successfully processed "
            f"{success_count} image(s).\n\n"
            f"Images saved in:\n"
            f"{WATERMARK_DIR}"
        )

    elif success_count > 0:

        messagebox.showwarning(
            "Partially Complete",
            f"Successful: {success_count}\n"
            f"Failed: {error_count}\n\n"
            f"Check Recent Conversions for details."
        )

    else:

        messagebox.showerror(
            "Conversion Failed",
            "No image could be processed.\n\n"
            "Make sure the Google Drive files "
            "are public and accessible."
        )


# ============================================================
# COPY
# ============================================================

def copy_output():

    value = (
        output_entry.get()
        .strip()
    )

    if not value:

        messagebox.showwarning(
            "Nothing to Copy",
            "There is no proxy URL to copy."
        )

        return

    root.clipboard_clear()

    root.clipboard_append(
        value
    )

    root.update()

    messagebox.showinfo(
        "Copied",
        "Proxy URL copied to clipboard."
    )


# ============================================================
# OPEN IMAGE
# ============================================================

def open_image():

    value = (
        output_entry.get()
        .strip()
    )

    if not value:

        messagebox.showwarning(
            "No Image",
            "Please convert a link first."
        )

        return

    webbrowser.open(
        value
    )


# ============================================================
# OPEN DOWNLOADED FOLDER
# ============================================================

def open_downloaded_folder():

    try:

        if os.name == "nt":

            os.startfile(
                WATERMARK_DIR
            )

        elif os.name == "posix":

            import subprocess

            subprocess.Popen(
                [
                    "xdg-open",
                    WATERMARK_DIR
                ]
            )

        else:

            webbrowser.open(
                WATERMARK_DIR
            )

    except Exception as error:

        messagebox.showerror(
            "Error",
            str(error)
        )


# ============================================================
# CLEAR
# ============================================================

def clear_input():

    input_text.delete(
        "1.0",
        tk.END
    )

    output_entry.delete(
        0,
        tk.END
    )


# ============================================================
# PASTE
# ============================================================

def paste_links():

    try:

        clipboard_text = (
            root.clipboard_get()
        )

        input_text.insert(
            tk.END,
            clipboard_text
        )

    except Exception:

        messagebox.showwarning(
            "Paste Error",
            "Clipboard does not contain text."
        )


# ============================================================
# TREE DOUBLE CLICK
# ============================================================

def tree_double_click(event):

    selected = (
        history_tree.selection()
    )

    if not selected:
        return

    values = history_tree.item(
        selected[0],
        "values"
    )

    if not values:
        return

    proxy_url = values[1]

    if proxy_url:

        output_entry.delete(
            0,
            tk.END
        )

        output_entry.insert(
            0,
            proxy_url
        )


# ============================================================
# KEYBOARD SHORTCUTS
# ============================================================

def shortcut_convert(event=None):
    convert_links()


def shortcut_paste(event=None):
    paste_links()


def shortcut_clear(event=None):
    clear_input()


def shortcut_copy(event=None):
    copy_output()


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "LINKER SOFTWARE"
)

root.geometry(
    "1100x760"
)

root.minsize(
    900,
    650
)

root.configure(
    bg=BG
)


# ============================================================
# APPLICATION ICON
# ============================================================

if os.path.exists(
    UI_LOGO_PATH
):

    try:

        app_icon = Image.open(
            UI_LOGO_PATH
        ).convert("RGBA")

        app_icon.thumbnail(
            (
                64,
                64
            ),
            Image.Resampling.LANCZOS
        )

        app_icon_tk = ImageTk.PhotoImage(
            app_icon
        )

        root.iconphoto(
            True,
            app_icon_tk
        )

        root.app_icon_tk = (
            app_icon_tk
        )

    except Exception as error:

        print(
            "Application icon error:",
            error
        )


# ============================================================
# MODERN HEADER
# ============================================================

header = tk.Frame(
    root,
    bg=HEADER_BG,
    height=88
)

header.pack(
    fill="x"
)

header.pack_propagate(
    False
)


# ============================================================
# HEADER LEFT ACCENT
# ============================================================

header_accent = tk.Frame(
    header,
    bg=BLUE,
    width=5
)

header_accent.pack(
    side="left",
    fill="y"
)


# ============================================================
# HEADER LOGO
# ============================================================

header_logo_frame = tk.Frame(
    header,
    bg=HEADER_BG,
    width=70,
    height=70
)

header_logo_frame.pack(
    side="left",
    padx=(18, 12),
    pady=9
)

header_logo_frame.pack_propagate(
    False
)


if os.path.exists(
    UI_LOGO_PATH
):

    try:

        header_logo = Image.open(
            UI_LOGO_PATH
        ).convert("RGBA")

        header_logo.thumbnail(
            (
                58,
                58
            ),
            Image.Resampling.LANCZOS
        )

        header_logo_tk = ImageTk.PhotoImage(
            header_logo
        )

        header_logo_label = tk.Label(
            header_logo_frame,
            image=header_logo_tk,
            bg=HEADER_BG,
            bd=0,
            highlightthickness=0
        )

        header_logo_label.image = (
            header_logo_tk
        )

        header_logo_label.pack(
            expand=True
        )

    except Exception as error:

        print(
            "Header logo error:",
            error
        )


# ============================================================
# HEADER TEXT
# ============================================================

header_text = tk.Frame(
    header,
    bg=HEADER_BG
)

header_text.pack(
    side="left",
    fill="y"
)


title_label = tk.Label(
    header_text,
    text="LINKER SOFTWARE",
    font=(
        "Segoe UI",
        18,
        "bold"
    ),
    fg=WHITE,
    bg=HEADER_BG
)

title_label.pack(
    anchor="w",
    pady=(13, 0)
)


subtitle_label = tk.Label(
    header_text,
    text="Google Drive Image Link Converter",
    font=(
        "Segoe UI",
        9
    ),
    fg=MUTED,
    bg=HEADER_BG
)

subtitle_label.pack(
    anchor="w"
)


# ============================================================
# HEADER RIGHT SIDE
# ============================================================

header_right = tk.Frame(
    header,
    bg=HEADER_BG
)

header_right.pack(
    side="right",
    padx=22
)


version_label = tk.Label(
    header_right,
    text=f"v{APP_VERSION}",
    font=(
        "Segoe UI",
        9,
        "bold"
    ),
    fg=MUTED,
    bg=HEADER_BG
)

version_label.pack(
    anchor="e"
)


status_label = tk.Label(
    header_right,
    text="● READY",
    font=(
        "Segoe UI",
        8,
        "bold"
    ),
    fg="#60a5fa",
    bg=HEADER_BG
)

status_label.pack(
    anchor="e",
    pady=(2, 0)
)


# ============================================================
# BLUE ACCENT LINE
# ============================================================

accent_line = tk.Frame(
    root,
    bg=BLUE,
    height=2
)

accent_line.pack(
    fill="x"
)


# ============================================================
# MAIN BACKGROUND CANVAS
# ============================================================

background_canvas = tk.Canvas(
    root,
    bg=BG,
    highlightthickness=0,
    bd=0
)

background_canvas.pack(
    fill="both",
    expand=True
)


# ============================================================
# PREPARE BACKGROUND LOGO
# ============================================================

background_logo_image = (
    prepare_background_logo()
)


# ============================================================
# CONTENT FRAME
# ============================================================

main_frame = tk.Frame(
    background_canvas,
    bg=BG
)

main_window = (
    background_canvas.create_window(
        18,
        18,
        window=main_frame,
        anchor="nw"
    )
)


# ============================================================
# KEEP CONTENT FITTED
# ============================================================

def resize_main_frame(event):

    background_canvas.itemconfig(
        main_window,
        width=max(
            100,
            event.width - 36
        ),
        height=max(
            100,
            event.height - 36
        )
    )

    draw_background_logo()


background_canvas.bind(
    "<Configure>",
    resize_main_frame
)


# ============================================================
# INPUT PANEL
# ============================================================

input_panel = tk.Frame(
    main_frame,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)

input_panel.pack(
    fill="x"
)


input_title = tk.Label(
    input_panel,
    text="Google Drive Links",
    font=(
        "Segoe UI",
        11,
        "bold"
    ),
    fg=WHITE,
    bg=PANEL
)

input_title.pack(
    anchor="w",
    padx=14,
    pady=(12, 6)
)


input_text = tk.Text(
    input_panel,
    height=6,
    bg=INPUT_BG,
    fg=WHITE,
    insertbackground=WHITE,
    selectbackground=BLUE,
    relief="flat",
    font=(
        "Consolas",
        10
    ),
    wrap="word"
)

input_text.pack(
    fill="x",
    padx=14,
    pady=(0, 10)
)


# ============================================================
# BUTTON HELPER
# ============================================================

def make_button(
    parent,
    text,
    command,
    width=15
):

    button = tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        font=(
            "Segoe UI",
            9,
            "bold"
        ),
        bg=HEADER_BG_2,
        fg=TEXT,
        activebackground=BLUE_HOVER,
        activeforeground=WHITE,
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=8,
        pady=7
    )

    # Simple modern hover effect
    def on_enter(event):
        button.configure(
            bg=BLUE_HOVER,
            fg=WHITE
        )

    def on_leave(event):
        button.configure(
            bg=HEADER_BG_2,
            fg=TEXT
        )

    button.bind(
        "<Enter>",
        on_enter
    )

    button.bind(
        "<Leave>",
        on_leave
    )

    return button


# ============================================================
# BUTTON ROW
# ============================================================

button_frame = tk.Frame(
    input_panel,
    bg=PANEL
)

button_frame.pack(
    fill="x",
    padx=14,
    pady=(0, 14)
)


paste_button = make_button(
    button_frame,
    "Paste",
    paste_links,
    12
)

paste_button.pack(
    side="left",
    padx=(0, 7)
)


convert_button = tk.Button(
    button_frame,
    text="Convert All",
    command=convert_links,
    font=(
        "Segoe UI",
        9,
        "bold"
    ),
    bg=BLUE,
    fg=WHITE,
    activebackground=BLUE_HOVER,
    activeforeground=WHITE,
    relief="flat",
    bd=0,
    cursor="hand2",
    padx=18,
    pady=7
)

convert_button.pack(
    side="left",
    padx=7
)


def convert_enter(event):
    convert_button.configure(
        bg=BLUE_HOVER
    )


def convert_leave(event):
    convert_button.configure(
        bg=BLUE
    )


convert_button.bind(
    "<Enter>",
    convert_enter
)

convert_button.bind(
    "<Leave>",
    convert_leave
)


clear_button = make_button(
    button_frame,
    "Clear",
    clear_input,
    12
)

clear_button.pack(
    side="left",
    padx=7
)


folder_button = make_button(
    button_frame,
    "Open Downloaded",
    open_downloaded_folder,
    18
)

folder_button.pack(
    side="right"
)


# ============================================================
# OUTPUT PANEL
# ============================================================

output_panel = tk.Frame(
    main_frame,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)

output_panel.pack(
    fill="x",
    pady=(14, 0)
)


output_title = tk.Label(
    output_panel,
    text="Last Proxy URL",
    font=(
        "Segoe UI",
        11,
        "bold"
    ),
    fg=WHITE,
    bg=PANEL
)

output_title.pack(
    anchor="w",
    padx=14,
    pady=(12, 6)
)


output_row = tk.Frame(
    output_panel,
    bg=PANEL
)

output_row.pack(
    fill="x",
    padx=14,
    pady=(0, 14)
)


output_entry = tk.Entry(
    output_row,
    bg=INPUT_BG,
    fg=WHITE,
    insertbackground=WHITE,
    relief="flat",
    font=(
        "Consolas",
        9
    )
)

output_entry.pack(
    side="left",
    fill="x",
    expand=True,
    ipady=8
)


copy_button = make_button(
    output_row,
    "Copy",
    copy_output,
    10
)

copy_button.pack(
    side="left",
    padx=(8, 0)
)


open_button = make_button(
    output_row,
    "Open Image",
    open_image,
    12
)

open_button.pack(
    side="left",
    padx=(8, 0)
)


# ============================================================
# HISTORY PANEL
# ============================================================

history_panel = tk.Frame(
    main_frame,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)

history_panel.pack(
    fill="both",
    expand=True,
    pady=(14, 0)
)


# ============================================================
# HISTORY HEADER
# ============================================================

history_header = tk.Frame(
    history_panel,
    bg=PANEL
)

history_header.pack(
    fill="x",
    padx=14,
    pady=(12, 8)
)


history_title = tk.Label(
    history_header,
    text="Recent Conversions",
    font=(
        "Segoe UI",
        11,
        "bold"
    ),
    fg=WHITE,
    bg=PANEL
)

history_title.pack(
    side="left"
)


search_var = tk.StringVar()


search_entry = tk.Entry(
    history_header,
    textvariable=search_var,
    bg=INPUT_BG,
    fg=WHITE,
    insertbackground=WHITE,
    relief="flat",
    font=(
        "Segoe UI",
        9
    ),
    width=38
)

search_entry.pack(
    side="right",
    ipady=6
)


search_label = tk.Label(
    history_header,
    text="Search URL / status",
    font=(
        "Segoe UI",
        8
    ),
    fg=MUTED,
    bg=PANEL
)

search_label.pack(
    side="right",
    padx=(0, 8)
)


# ============================================================
# TREEVIEW STYLE
# ============================================================

style = ttk.Style()

try:

    style.theme_use(
        "clam"
    )

except Exception:
    pass


style.configure(
    "Treeview",
    background=INPUT_BG,
    foreground=TEXT,
    fieldbackground=INPUT_BG,
    rowheight=30,
    borderwidth=0,
    font=(
        "Segoe UI",
        8
    )
)


style.configure(
    "Treeview.Heading",
    background=HEADER_BG_2,
    foreground=WHITE,
    relief="flat",
    font=(
        "Segoe UI",
        9,
        "bold"
    )
)


style.map(
    "Treeview",
    background=[
        (
            "selected",
            BLUE
        )
    ],
    foreground=[
        (
            "selected",
            WHITE
        )
    ]
)


# ============================================================
# TABLE
# ============================================================

table_frame = tk.Frame(
    history_panel,
    bg=PANEL
)

table_frame.pack(
    fill="both",
    expand=True,
    padx=14,
    pady=(0, 14)
)


columns = (
    "original",
    "proxy",
    "status"
)


history_tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    selectmode="browse"
)


history_tree.heading(
    "original",
    text="Original Google Drive Link"
)

history_tree.heading(
    "proxy",
    text="Converted Proxy URL"
)

history_tree.heading(
    "status",
    text="Status"
)


history_tree.column(
    "original",
    width=360,
    anchor="w"
)

history_tree.column(
    "proxy",
    width=470,
    anchor="w"
)

history_tree.column(
    "status",
    width=130,
    anchor="center"
)


scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=history_tree.yview
)


history_tree.configure(
    yscrollcommand=scrollbar.set
)


history_tree.pack(
    side="left",
    fill="both",
    expand=True
)


scrollbar.pack(
    side="right",
    fill="y"
)


history_tree.bind(
    "<Double-1>",
    tree_double_click
)


# ============================================================
# SEARCH
# ============================================================

search_var.trace_add(
    "write",
    lambda *args: refresh_history()
)


# ============================================================
# FOOTER
# ============================================================

footer = tk.Frame(
    root,
    bg="#070d18",
    height=32
)

footer.pack(
    fill="x"
)

footer.pack_propagate(
    False
)


footer_label = tk.Label(
    footer,
    text=(
        "LINKER SOFTWARE  •  "
        "Gauranga Creation"
    ),
    font=(
        "Segoe UI",
        8
    ),
    fg=MUTED,
    bg="#070d18"
)

footer_label.pack(
    expand=True
)


# ============================================================
# KEYBOARD SHORTCUTS
# ============================================================

root.bind(
    "<Control-Return>",
    shortcut_convert
)

root.bind(
    "<Control-v>",
    shortcut_paste
)

root.bind(
    "<Control-l>",
    shortcut_clear
)

root.bind(
    "<Control-c>",
    shortcut_copy
)


# ============================================================
# START APPLICATION
# ============================================================

root.mainloop()
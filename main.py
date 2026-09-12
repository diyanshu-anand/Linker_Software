import re

def convert_drive_link_to_proxy(drive_link):
    """
    Converts a Google Drive public file URL to a proxy image URL.
    """
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', drive_link)
    if not match:
        return "Invalid Google Drive link. Make sure it's in the correct format."
    
    file_id = match.group(1)
    return f"https://images.weserv.nl/?url=drive.google.com/uc?id={file_id}"

def main():
    print("Google Drive Image Link Converter")
    print("Paste a public Google Drive link below. Type 'exit' to quit.\n")

    while True:
        drive_link = input("Drive Link: ").strip()
        if drive_link.lower() == "exit":
            print("Exiting. Goodbye!")
            break
        result = convert_drive_link_to_proxy(drive_link)
        print(f"Converted Link: {result}\n")

if __name__ == "__main__":
    main()

import os
import sys
import shutil
import datetime
from PIL import Image


def get_date_taken(path, raise_on_error=False):
    try:
        img = Image.open(path)
        # 36867 is the EXIF tag for DateTimeOriginal
        exif_data = img._getexif()
        if exif_data:
            date_str = exif_data.get(36867)
            if date_str:
                # Format is usually "YYYY:MM:DD HH:MM:SS"
                try:
                    return datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    print(f"datetime metadata not in expected format: failed to parse {
                          date_str} into %Y:%m:%d %H:%M:%S for {path}\n\t\t->if run with -f date will be {datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        if raise_on_error:
            raise e
        # otherwise pass to fallback

    # fallback to file modification time if EXIF fails or is missing
    timestamp = os.path.getmtime(path)
    return datetime.datetime.fromtimestamp(timestamp)


def get_unique_path(destination_folder, filename):
    """
    Generates a unique filename if the file already exists in destination.
    image.jpg -> image(1).jpg -> image(2).jpg
    """
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    full_path = os.path.join(destination_folder, new_filename)

    while os.path.exists(full_path):
        new_filename = f"{name}({counter}){ext}"
        full_path = os.path.join(destination_folder, new_filename)
        counter += 1

    return full_path


def main():
    # Check for force flag
    force = False
    if "-f" in sys.argv:
        force = True
        sys.argv.remove("-f")
    if len(sys.argv) == 1:
        source = os.getcwd()
        dest = "D:\\Pictures"
        force = True
    if len(sys.argv) == 2:
        source = os.getcwd()
        dest = "D:\\Pictures"
        force = True
    if len(sys.argv) < 3:
        print("Usage: python script.py <source_dir> <dest_dir> [prefix] [-f]")
        sys.exit(1)
    else:
        source = sys.argv[1]
        dest = sys.argv[2]
        prefix = None
        if len(sys.argv) > 3:
            prefix = sys.argv[3]

    num_files = 0
    print(f"Validating metadata in {source}...")
    errors = []
    for root, dirs, files in os.walk(source):
        for file in files:
            num_files += 1
            path = os.path.join(root, file)
            try:
                # Attempt to read with strict error raising
                get_date_taken(path, raise_on_error=True)
            except Exception as e:
                errors.append(f"{file}: {e}")

    if errors:
        print("\nexceptions found during scan:")
        for err in errors:
            print(f" - {err}")

        if not force:
            print(
                "\noperation cancelled. use -f to force copy (failed files will use file modification time).")
            sys.exit(1)
        else:
            print("\n-f flag detected. proceeding despite errors...")

    print(f"found {num_files} files, proceeding to copy")
    # Create destination if it doesn't exist
    if not os.path.exists(dest):
        os.makedirs(dest)

    print(f"scanning {source}...")

    count = 0
    for root, dirs, files in os.walk(source):
        for file in files:
            source_path = os.path.join(root, file)

            # Get date object
            date_obj = get_date_taken(source_path)

            # Format folder structure: dest/YYYY/01-January/
            year_folder = date_obj.strftime("%Y")
            month_folder = date_obj.strftime("%m-%B")
            if prefix is not None:
                target_dir = os.path.join(
                    dest, year_folder, month_folder, prefix)
            else:
                target_dir = os.path.join(dest, year_folder, month_folder)

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            # handle duplicates
            target_path = get_unique_path(target_dir, file)

            try:
                shutil.copy2(source_path, target_path)
                print(f"copied {count}/{num_files}: {file} -> {target_path}")
                count += 1
            except Exception as e:
                print(f"error copying {file}: {e}")

    print(f"\nfinished: copied {count} images.")


if __name__ == "__main__":
    main()

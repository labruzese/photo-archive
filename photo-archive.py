import os
import sys
import shutil
import datetime
from PIL import Image


def get_date_taken(path):
    """
    Attempts to get the date from EXIF data. 
    Falls back to file modification time if EXIF is missing or broken.
    """
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
                    pass  # Silently fail format errors and go to fallback
    except Exception:
        pass  # Silently fail IO/EXIF errors and go to fallback

    # Fallback to file modification time
    timestamp = os.path.getmtime(path)
    return datetime.datetime.fromtimestamp(timestamp)


def get_unique_path(destination_folder, filename, reserved_paths):
    """
    Generates a unique filename if the file already exists in destination
    OR if we have already planned to put a file there during this run.
    """
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    full_path = os.path.join(destination_folder, new_filename)

    # Check against actual filesystem AND our internal list of paths we are about to create
    while os.path.exists(full_path) or full_path in reserved_paths:
        new_filename = f"{name}({counter}){ext}"
        full_path = os.path.join(destination_folder, new_filename)
        counter += 1

    return full_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <source_dir> <dest_dir> [prefix]")
        sys.exit(1)

    source = sys.argv[1]
    dest = sys.argv[2]
    prefix = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"scanning {source} and generating plan...\n")

    # List of tuples: (source_path, target_path, date_obj)
    planned_operations = []
    reserved_paths = set()  # To track collisions within the batch

    file_count = 0

    # --- PHASE 1: PLANNING ---
    for root, dirs, files in os.walk(source):
        for file in files:
            source_path = os.path.join(root, file)
            file_count += 1

            # Get date object (automatically handles fallback)
            date_obj = get_date_taken(source_path)

            # Format folder structure: dest/YYYY/01-January/
            year_folder = date_obj.strftime("%Y")
            month_folder = date_obj.strftime("%m-%B")

            if prefix:
                target_dir = os.path.join(
                    dest, year_folder, month_folder, prefix)
            else:
                target_dir = os.path.join(dest, year_folder, month_folder)

            # Calculate unique path
            target_path = get_unique_path(target_dir, file, reserved_paths)

            # Reserve this path so the next iteration knows it's taken
            reserved_paths.add(target_path)

            planned_operations.append((source_path, target_path, date_obj))

    if file_count == 0:
        print("No files found in source directory.")
        sys.exit(0)

    # --- PHASE 2: PREVIEW ---
    print("=" * 60)
    print(f"found {len(planned_operations)} files to organize.")
    print("=" * 60)

    for src, dst, date in planned_operations:
        rel_src = os.path.relpath(src, source)
        rel_dst = os.path.relpath(dst, dest)
        print(f"[{date.strftime('%Y-%m-%d')}] {rel_src} -> {rel_dst}")

    print("=" * 60)

    # --- PHASE 3: CONFIRMATION ---
    confirm = input(f"\nProceed with copying {
                    len(planned_operations)} files? (y/n): ").strip().lower()

    if confirm != 'y':
        print("Operation cancelled.")
        sys.exit(0)

    print("\nCopying files...")

    # --- PHASE 4: EXECUTION ---
    # Create necessary directories first
    # We can do this lazily in the loop or strictly here.
    # Doing it in loop ensures we only create folders for files we actually copy.

    success_count = 0
    for src, dst, date in planned_operations:
        target_dir = os.path.dirname(dst)

        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
            except OSError as e:
                print(f"Error creating directory {target_dir}: {e}")
                continue

        try:
            new_loc = shutil.copy2(src, dst)
            print(f"copied ({
                success_count}/{len(planned_operations)}): {os.path.basename(src)} -> {new_loc}")
            success_count += 1
        except Exception as e:
            print(f"error copying {src} -> {dst}: {e}")

    print(f"\nFinished: Copied {
          success_count}/{len(planned_operations)} images.")


if __name__ == "__main__":
    main()

script to automatically organizes photos into a date-based folder structure using EXIF metadata first then file modification date.

- Scan source recursively
- Organizes photos by date into `YYYY/MM-MonthName/` folders
- Read EXIF DateTimeOriginal data with file modification date fallback
- Renames with (num) if file already exists in archive directory
- Optional prefix for destination folders (`YYYY/MM-MonthName/prefix/img.png`)
- Besides possible duplicate renaming doesn't modify orginal file.
- Show a preview of planned operations and prompt before continuing

## Requirements

```bash
pip install Pillow
```

## Usage

```bash
python script.py <source_dir> <dest_dir> [prefix]
```

**Examples:**
```bash
python script.py ./photos ./organized
# With prefix
python script.py ./photos ./organized vacation
```

## Output Structure

```
dest_dir/
├── 2024/
│   ├── 01-January/
│   ├── 02-February/
│   └── ...
└── 2025/
    └── 03-March/
```

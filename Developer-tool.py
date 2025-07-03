import os
import sys
import subprocess
import shutil
import hashlib
import json

# Paths setup
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GDRE_TOOLS_EXE = os.path.join(BASE_DIR, 'gdre_tools.exe')
BASE_PCK = os.path.join(BASE_DIR, 'spring-dash-windows-64bit.pck')

GAME_FILES_DIR = os.path.join(BASE_DIR, 'game-files')
DEV_MOD_DIR = os.path.join(BASE_DIR, 'dev-mod')
BASELINE_CHECKSUMS_FILE = os.path.join(BASE_DIR, 'baseline_checksums.json')


def extract_pck(out_dir):
    if os.path.exists(out_dir):
        print(f"'{out_dir}' already exists, skipping extraction.")
        return
    os.makedirs(out_dir, exist_ok=True)
    cmd = [
        GDRE_TOOLS_EXE,
        '--headless',
        '--verbose',
        f'--recover={BASE_PCK}',
        f'--output={out_dir}'
    ]
    print(f"Extracting '{BASE_PCK}' into '{out_dir}'...")
    subprocess.run(cmd, check=True)


def md5_checksum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def scan_files(base_dir):
    files = {}
    for root, _, filenames in os.walk(base_dir):
        for name in filenames:
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, base_dir).replace('\\', '/')
            files[rel_path] = md5_checksum(full_path)
    return files


def copy_file(src_base, dst_base, rel_path):
    src_path = os.path.join(src_base, rel_path)
    dst_path = os.path.join(dst_base, rel_path)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.copy2(src_path, dst_path)
    print(f"Copied: {rel_path}")


def remove_file(base_dir, rel_path):
    path = os.path.join(base_dir, rel_path)
    if os.path.exists(path):
        os.remove(path)
        print(f"Removed: {rel_path}")
        # Clean up empty directories up the tree
        dir_path = os.path.dirname(path)
        while dir_path != base_dir and not os.listdir(dir_path):
            os.rmdir(dir_path)
            dir_path = os.path.dirname(dir_path)


def generate_baseline_checksums():
    checksums = scan_files(GAME_FILES_DIR)
    with open(BASELINE_CHECKSUMS_FILE, 'w') as f:
        json.dump(checksums, f, indent=2)
    print("Baseline checksums generated.")


def load_baseline_checksums():
    if not os.path.exists(BASELINE_CHECKSUMS_FILE):
        print("Baseline checksum file missing. Generating now.")
        generate_baseline_checksums()
    with open(BASELINE_CHECKSUMS_FILE, 'r') as f:
        return json.load(f)


def main():
    if not os.path.exists(GAME_FILES_DIR):
        extract_pck(GAME_FILES_DIR)
        generate_baseline_checksums()
    else:
        print("'game-files' folder exists, skipping extraction.")

    baseline_checksums = load_baseline_checksums()
    current_checksums = scan_files(GAME_FILES_DIR)

    added_or_changed = {
        f for f, chksum in current_checksums.items()
        if baseline_checksums.get(f) != chksum
    }
    removed = {f for f in baseline_checksums if f not in current_checksums}

    # Copy changed/added files to dev-mod
    for f in added_or_changed:
        copy_file(GAME_FILES_DIR, DEV_MOD_DIR, f)

    # Remove deleted files from dev-mod
    for f in removed:
        remove_file(DEV_MOD_DIR, f)

    print("Dev-mod update complete.")


if __name__ == '__main__':
    main()

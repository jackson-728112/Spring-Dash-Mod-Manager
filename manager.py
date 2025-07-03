import os
import sys
import subprocess
import zipfile
import tempfile
import shutil

# Determine base dir (PyInstaller-compatible)
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS  # For PyInstaller
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GDRE_TOOLS_EXE = os.path.join(BASE_DIR, 'gdre_tools.exe')
GDRE_TOOLS_PCK = os.path.join(BASE_DIR, 'gdre_tools.pck')
BASE_PCK = 'spring-dash-windows-64bit.pck'
OUTPUT_PCK = 'spring-dash-windows-64bit_MODDED.pck'
MODS_DIR = 'mods'
PAK_DIR = os.path.join(MODS_DIR, 'pak')
GAME_EXE = 'spring-dash-windows-64bit.exe'
GAME_ARGS = ['--main-pack', OUTPUT_PCK]

TEMP_DIRS = []  # Will hold paths of temporary extracted zip dirs

def extract_zip_to_temp(zip_path):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    TEMP_DIRS.append(temp_dir)
    return temp_dir

def copy_mod_contents_to_pak(mod_path):
    for root, _, files in os.walk(mod_path):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, mod_path)
            dest_path = os.path.join(PAK_DIR, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(abs_path, dest_path)

def prepare_pak_folder():
    if os.path.exists(PAK_DIR):
        shutil.rmtree(PAK_DIR)
    os.makedirs(PAK_DIR)

    for entry in os.listdir(MODS_DIR):
        full_path = os.path.join(MODS_DIR, entry)
        if full_path == PAK_DIR:
            continue
        if os.path.isdir(full_path):
            copy_mod_contents_to_pak(full_path)
        elif entry.lower().endswith('.zip'):
            temp_dir = extract_zip_to_temp(full_path)
            copy_mod_contents_to_pak(temp_dir)

def collect_patch_args_from_pak():
    patch_args = []
    for root, _, files in os.walk(PAK_DIR):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, PAK_DIR)
            res_path = f"res://{rel_path.replace(os.sep, '/')}"
            patch_args.append(f"--patch-file={abs_path}={res_path}")
    return patch_args

def collect_patch_args_from_individual_mods():
    patch_args = []

    for entry in os.listdir(MODS_DIR):
        entry_path = os.path.join(MODS_DIR, entry)
        if entry == 'pak':
            continue

        if os.path.isdir(entry_path):
            mod_root = entry_path
        elif entry.lower().endswith('.zip'):
            mod_root = extract_zip_to_temp(entry_path)
        else:
            continue

        for root, _, files in os.walk(mod_root):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, mod_root)
                res_path = f"res://mods/{entry}/{rel_path.replace(os.sep, '/')}"
                patch_args.append(f"--patch-file={abs_path}={res_path}")

    return patch_args

def apply_all_mods_together():
    prepare_pak_folder()

    patch_args = collect_patch_args_from_pak()
    patch_args += collect_patch_args_from_individual_mods()

    if not patch_args:
        print("No patch files found, nothing to do.")
        return False

    cmd = [
        GDRE_TOOLS_EXE,
        '--headless',
        '--verbose',
        f'--pck-patch={BASE_PCK}',
        f'--output={OUTPUT_PCK}',
    ] + patch_args

    print(f"Patching mods into '{OUTPUT_PCK}'...")
    try:
        subprocess.run(cmd, check=True)
        print("All mods patched successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to patch mods. Error: {e}")
        return False
    finally:
        for temp_dir in TEMP_DIRS:
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    success = apply_all_mods_together()
    if success:
        print(f"Launching the game: {GAME_EXE} with args {GAME_ARGS}")
        try:
            subprocess.run([GAME_EXE] + GAME_ARGS)
        except Exception as e:
            print(f"Failed to launch the game. Error: {e}")

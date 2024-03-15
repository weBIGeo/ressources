"""
weBIGeo
Copyright (C) 2024 Gerald Kimmersdorfer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import shutil
import sys
import stat

# Initialize counters
deleted_dirs_count = 0
deleted_files_count = 0
failed_deletions_count = 0

# necessary for some git files
def make_writable_and_remove(path):
    global failed_deletions_count
    try:
        os.chmod(path, stat.S_IWRITE)
        if os.path.isdir(path):
            shutil.rmtree(path)
            global deleted_dirs_count
            deleted_dirs_count += 1
        else:
            os.remove(path)
            global deleted_files_count
            deleted_files_count += 1
    except Exception as e:
        failed_deletions_count += 1
        print(f"Failed to delete {path}: {e}")

def delete_source_files():
    all_root_dirs = []

    # Fetch all directories in the root without the build and include folder
    for dir in os.listdir('.'):
        if os.path.isdir(dir) and dir != 'build' and dir != 'include':
            all_root_dirs.append(dir)

    all_files = []
    # Fetch all files inside the all_root_dirs
    for dir in all_root_dirs:
        for root, _, files in os.walk(dir, topdown=True):
            for file in files:
                all_files.append(os.path.join(root, file))

    print(f"Deleting {len(all_files)} source files  ...")

    for file in all_files:
        make_writable_and_remove(file)

def delete_files_except_extensions(extensions):
    all_files = []
    for root, dirs, files in os.walk('.', topdown=True):
        for file in files:
            if not any(file.endswith(ext) for ext in extensions):
                all_files.append(os.path.join(root, file))
                
    print(f"Deleting {len(all_files)} files based on their extension ...")

    for file in all_files:
        make_writable_and_remove(file)   

def delete_empty_dirs():
    for root, dirs, _ in os.walk('.', topdown=False):  # Traverse the tree from the bottom up
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):  # Check if the directory is empty
                try:
                    os.rmdir(dir_path)
                    global deleted_dirs_count
                    deleted_dirs_count += 1
                except Exception as e:
                    failed_deletions_count += 1
                    print(f"Failed to delete empty directory {dir_path}: {e}")



if __name__ == "__main__":
    # Check for correct directory by verifying the existence of 'build/' and 'include/dawn'
    if not os.path.isdir('build') or not os.path.isdir('include/dawn'):
        print("Error: The script must be run inside the dawn directory and should contain 'build/' and 'include/dawn' folders.")
        sys.exit(1)

    delete_source_files()
    delete_files_except_extensions(['.exe', '.ilk', '.pdb', '.lib', '.h', '.hpp', '.c', '.cpp'])
    delete_empty_dirs()
    print(f"Deletion complete. Deleted {deleted_files_count} files and {deleted_dirs_count} directories. Failed to delete {failed_deletions_count} items.")

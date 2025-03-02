import os
import zipfile
from pathlib import Path
from datetime import datetime

def load_gitignore(root_dir):
    """Loads .gitignore patterns into a set."""
    gitignore_path = Path(root_dir) / ".gitignore"
    if not gitignore_path.exists():
        print("No .gitignore found, including all files.")
        return set()

    patterns = set()
    print(f"Loading .gitignore from {gitignore_path}...")
    with open(gitignore_path, "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.add(line)
    print(f"Loaded {len(patterns)} ignore patterns.")
    return patterns

def should_ignore(path, root_dir, ignore_patterns):
    """Checks if a path should be ignored based on .gitignore patterns."""
    relative_path = os.path.relpath(path, root_dir).replace("\\", "/")

    for pattern in ignore_patterns:
        if pattern.endswith("/"):
            if relative_path.startswith(pattern.rstrip("/")):
                return True
        elif pattern.startswith("*"):
            if relative_path.endswith(pattern.lstrip("*")):
                return True
        elif pattern in relative_path:
            return True
    return False

def zip_directory_with_gitignore(source_dir, output_zip):
    """Creates a zip file of source_dir, respecting .gitignore."""
    print(f"Zipping directory: {source_dir}")
    print(f"Output file will be: {output_zip}")

    ignore_patterns = load_gitignore(source_dir)

    file_count = 0
    skipped_count = 0

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            relative_root = os.path.relpath(root, source_dir)
            if relative_root == ".":
                relative_root = ""

            # Apply ignore rules to directories
            dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), source_dir, ignore_patterns)]

            for file in files:
                file_path = os.path.join(root, file)
                if should_ignore(file_path, source_dir, ignore_patterns):
                    skipped_count += 1
                    continue

                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                file_count += 1

    print(f"✅ Zipping complete! Added {file_count} files.")
    print(f"⚠️ Skipped {skipped_count} files due to .gitignore rules.")

if __name__ == "__main__":
    source_dir = "."  # Current directory (assumes script is in root)

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_zip = f"snapshot-{timestamp}.zip"

    start_time = datetime.now()
    print(f"Starting zip process at {start_time.strftime('%Y-%m-%d %H:%M:%S')}...")

    zip_directory_with_gitignore(source_dir, output_zip)

    end_time = datetime.now()
    duration = end_time - start_time

    print(f"✅ Snapshot saved as {output_zip}")
    print(f"Finished at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️ Total duration: {duration}")

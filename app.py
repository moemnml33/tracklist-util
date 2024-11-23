import os
from csv import writer
from tinytag import TinyTag  # https://github.com/tinytag/tinytag

CSV_HEADERS = ["Track number", "Track name", "Artist name", "Album"]
FOLDERS_TO_IGNORE = ["/Volumes/KEY2UNDRGRD/General/Soundeo Djjjeff",
                     "/Volumes/KEY2UNDRGRD/General/Loopcloud", "/Volumes/KEY2UNDRGRD/General/Samples"]


def check_if_mytracklist_exists(mytracklist_path):
    """Check if mytracklist.csv exists and delete it if it does

    Args:
        mytracklist_path (str): path to mytracklist.csv
    """
    if os.path.exists(mytracklist_path):
        os.remove(mytracklist_path)


def list_folders(root, dirs):
    """List folders in the root directory

    Args:
        root (str): root directory
        dirs (list): list of directories in the root directory

    Returns:
        list_of_folders (list): list of folders in the root directory
    """
    for dir in dirs:
        if dir:
            try:
                folder_path = os.path.join(root, dir)
                list_of_folders.append(folder_path)
            except Exception as e:
                print(f"Error listing folder {folder_path}: {e}")
    return list_of_folders


def print_colored(text, color):
    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }
    reset = "\033[0m"
    print(f"{colors.get(color, '')}{text}{reset}")


def generate_mytracklist(target_dir, folders_to_ignore, mytracklist_path):
    """Generate mytracklist.csv file with track metadata from the root directory.
    It's a csv file that contains the metadata of all the tracks that are present in the specified path.

    Args:
        root (str): root directory
        files (list): list of files in the root directory
        folders_to_ignore (list): list of folders to ignore
        mytracklist_path (str): path to mytracklist.csv
    """
    global csv_index
    for (root, dirs, files) in os.walk(target_dir, topdown=True):
        if not any(root.startswith(folder) for folder in folders_to_ignore):
            print_colored(
                f"Generating tracklist for tracks in {root}...", "blue")
            for file in files:
                try:
                    track_full_path = os.path.join(root, file)
                    tag: TinyTag = TinyTag.get(track_full_path)
                    with open(mytracklist_path, 'a') as csvfile:
                        writer_obj = writer(csvfile)
                        data = [f"{csv_index}", f"{tag.title}",
                                f"{tag.artist}", f"{tag.album}"]
                        if not os.path.exists(mytracklist_path) or os.path.getsize(mytracklist_path) == 0:
                            writer_obj.writerow(CSV_HEADERS)
                        writer_obj.writerow(data)
                    csv_index += 1
                except Exception as e:
                    print_colored(
                        f"Error processing {track_full_path}: {e}", "red")

            print_colored(
                f"Tracklist for {root} folder generated! {len(files)} items added.", "green")
    print_colored(f"Tracklist complete.", "green")


if __name__ == "__main__":
    cwd = os.getcwd()
    mytracklist_path = f"{cwd}/mytracklist.csv"
    target_dir = "/Volumes/KEY2UNDRGRD/General"
    list_of_folders = []
    csv_index = 0

    check_if_mytracklist_exists(mytracklist_path)
    generate_mytracklist(target_dir, FOLDERS_TO_IGNORE, mytracklist_path)

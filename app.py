from asyncio import FastChildWatcher
import os
from csv import writer
from tinytag import TinyTag  # https://github.com/tinytag/tinytag
import pandas as pd
from fuzzywuzzy import fuzz
import re

CSV_HEADERS = ["Track name", "Artist name", "Album"]
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


def generate_tracklist(target_dir, folders_to_ignore, mytracklist_path):
    """Generate mytracklist.csv file with track metadata from the root directory.
    It's a csv file that contains the metadata of all the tracks that are present in the specified path.

    Args:
        root (str): root directory
        files (list): list of files in the root directory
        folders_to_ignore (list): list of folders to ignore
        mytracklist_path (str): path to mytracklist.csv
    """
    global csv_index
    csv_index = 0
    for (root, dirs, files) in os.walk(target_dir, topdown=True):
        if not any(root.startswith(folder) for folder in folders_to_ignore):
            print_colored(
                f"Generating tracklist for tracks in {root}...", "blue")
            for file in files:
                # Skip files starting with '._': when exporting tracks from a serato crate into a folder,
                # a duplicate of the file gets created, which is called AppleDouble file, which returns None for all tags
                try:
                    if file.startswith("._"):
                        # print_colored(
                        #     f"Skipping unsupported file: {file}", "yellow")
                        continue
                    track_full_path = os.path.join(root, file)
                    tag: TinyTag = TinyTag.get(track_full_path)
                    with open(mytracklist_path, 'a') as csvfile:
                        writer_obj = writer(csvfile)
                        data = [f"{tag.title}",
                                f"{tag.artist}", f"{tag.album}"]
                        if not os.path.exists(mytracklist_path) or os.path.getsize(mytracklist_path) == 0:
                            writer_obj.writerow(CSV_HEADERS)
                        writer_obj.writerow(data)
                    csv_index += 1
                except Exception as e:
                    print_colored(
                        f"Error processing {track_full_path}: {e}", "red")

            print_colored(
                f"Tracklist for {root} folder generated! {csv_index} items added.", "green")
    print_colored(f"Tracklist complete.", "green")


# Define the threshold for similarity
SIMILARITY_THRESHOLD = 85

# Function to check if two tracks are similar


def are_tracks_similar(track1, track2, threshold=SIMILARITY_THRESHOLD):
    return fuzz.token_sort_ratio(track1, track2) >= threshold

# Function to check if two artists are the same


def are_artists_same(artist1, artist2):
    return artist1.strip().lower() == artist2.strip().lower()


def are_albums_same(album1, album2):
    # Convert non-string values to empty strings and then compare
    album1 = str(album1).strip().lower() if isinstance(album1, str) else ""
    album2 = str(album2).strip().lower() if isinstance(album2, str) else ""
    return album1 == album2
# Iterate through both dataframes and compare


# def find_matches(df1, df2):
#     matches = []
#     for idx1, row1 in df1.iterrows():
#         for idx2, row2 in df2.iterrows():
#             if (are_tracks_similar(row1['Track name'], row2['Track name']) and
#                     are_artists_same(row1['Artist name'], row2['Artist name']) and
#                     are_albums_same(row1['Album'], row2['Album'])):
#                 matches.append({
#                     f"{df1}_index": idx1,
#                     f"{df2}_index": idx2,
#                     "Track 1": row1['Track name'],
#                     "Track 2": row2['Track name'],
#                     "Artist": row2['Artist name'],
#                     "Album": row2['Album'],
#                 })
#     return matches


def find_matches(df1, df2):
    matches = []
    for idx1, row1 in df1.iterrows():
        for idx2, row2 in df2.iterrows():
            if (not are_tracks_similar(row1['Track and Artist'], row2['Track and Artist'])):
                matches.append({
                    f"{df1}_index": idx1,
                    f"{df2}_index": idx2,
                    "Track 1": row1['Track and Artist'],
                    "Track 2": row2['Track and Artist'],
                })
    return matches


def find_missing_tracks(df3, matches):
    missing_tracks = []
    for match in matches:
        # Check if "Track 2" is not an exact match in df3
        if not any(df3['Track name'].str.strip() == match['Track 2'].strip()):
            missing_tracks.append({
                "Track 2": match['Track 2'],
                "Artist": match['Artist']
            })
    return missing_tracks

# Clean the "Track name" column in both DataFrames


def clean_field(field):
    # Convert to lowercase for consistent processing
    field = field.lower()

    # Remove the word "original mix"
    field = field.replace("original", "")
    field = field.replace("mix", "")

    # Remove all special characters using regex
    # Keep only letters, numbers, and spaces
    field = re.sub(r"[^a-z0-9\s]", "", field)

    # Remove all spaces and strip surrounding whitespace
    return field.replace(" ", "").strip()


if __name__ == "__main__":
    cwd = os.getcwd()
    mytracklist_path = f"{cwd}/mytracklist.csv"
    temptracklist_path = f"{cwd}/temptracklist.csv"
    spotify_library = f"{cwd}/My Spotify Library.csv"
    target_dir = "/Volumes/KEY2UNDRGRD/General"
    crate_to_check_path = f"{target_dir}/crate_to_check"
    list_of_folders = []

    # check_if_mytracklist_exists(mytracklist_path)
    # check_if_mytracklist_exists(temptracklist_path)
    # generate_tracklist(target_dir, FOLDERS_TO_IGNORE, mytracklist_path)
    # generate_tracklist(crate_to_check_path, [], temptracklist_path)

    spotify_library_df = pd.read_csv(spotify_library).iloc[:, :3]
    mytracklist_df = pd.read_csv(mytracklist_path)
    temptracklist_df = pd.read_csv(temptracklist_path)

    # print(spotify_library_df)
    # print(mytracklist_df)
    # print(temptracklist_df)

    # Call the function and get matches
    # matches = find_matches(spotify_library_df, mytracklist_df)

    # # Print or process matches
    # for match in matches:
    #     print(f"Match found between:\n"
    #           f" - DF1: {match['Track 1']} by {match['Artist']} on {match['Album']}\n"
    #           f" - DF2: {match['Track 2']} by {match['Artist']} on {match['Album']}\n")

    # # Call the function
    # missing_tracks = find_missing_tracks(temptracklist_df, matches)

    # # Print results
    # if missing_tracks:
    #     print("Tracks not found in temptracklist_df:")
    #     for track in missing_tracks:
    #         print(f" - Track: {track['Track 2']} by {track['Artist']}")
    # else:
    #     print("All tracks were found in temptracklist_df.")

    # Drop duplicates if needed
    spotify_library_df_modif = spotify_library_df.drop_duplicates()
    mytracklist_df_modif = mytracklist_df.drop_duplicates()
    temptracklist_df_modif = temptracklist_df.drop_duplicates()

    spotify_library_df_modif["Track name"] = spotify_library_df_modif["Track name"].apply(
        clean_field)
    mytracklist_df_modif["Track name"] = mytracklist_df_modif["Track name"].apply(
        clean_field)
    temptracklist_df_modif["Track name"] = temptracklist_df_modif["Track name"].apply(
        clean_field)

    spotify_library_df_modif["Artist name"] = spotify_library_df_modif["Artist name"].apply(
        clean_field)
    mytracklist_df_modif["Artist name"] = mytracklist_df_modif["Artist name"].apply(
        clean_field)
    temptracklist_df_modif["Artist name"] = temptracklist_df_modif["Artist name"].apply(
        clean_field)

    # Save each DataFrame to a separate CSV file
    spotify_library_df_modif.to_csv(
        "cleaned/spotify_library_cleaned.csv", index=False)
    mytracklist_df_modif.to_csv("cleaned/mytracklist_cleaned.csv", index=False)
    temptracklist_df_modif.to_csv(
        "cleaned/temptracklist_cleaned.csv", index=False)

    # Merge the two DataFrames based on the "Track name" column
    matched_tracks_spot_vs_owned = pd.merge(
        spotify_library_df_modif[['Track name']],
        mytracklist_df_modif[['Track name']],
        on='Track name',
        how='inner'  # 'inner' will return only matching rows
    )

    matched_tracks_spot_vs_owned.to_csv(
        "results/matched_tracks_spot_vs_owned.csv", index=False)

    print(f"\n Spotify playlist vs all owned: {matched_tracks_spot_vs_owned}")

    # Merge the two DataFrames based on the "Track name" column
    matched_tracks_spot_and_owned_vs_crate = pd.merge(
        matched_tracks_spot_vs_owned[['Track name']],
        temptracklist_df_modif[['Track name']],
        on='Track name',
        how='inner'  # 'inner' will return only matching rows
    )

    matched_tracks_spot_and_owned_vs_crate.to_csv(
        "results/matched_tracks_spot_and_owned_vs_crate.csv", index=False)
    print(
        f"\n Spotify playlist matched with owned vs Serato crate: {matched_tracks_spot_and_owned_vs_crate}")

    # Find the remainder of Spotify tracks not in owned tracks
    remainder_spotify = pd.merge(
        spotify_library_df_modif[['Track name']],
        mytracklist_df_modif[['Track name']],
        on='Track name',
        how='left',
        indicator=True  # Adds a column to indicate where each row originates
    )

    # Filter for rows only in Spotify
    remainder_spotify = remainder_spotify[remainder_spotify['_merge'] == 'left_only'].drop(columns=[
                                                                                           '_merge'])

    # Save the remainder to a CSV file
    remainder_spotify.to_csv("results/remainder_spotify.csv", index=False)

    # print(f"\n Remainder of Spotify playlist: {remainder_spotify}")

    # matches = find_matches(remainder_spotify, mytracklist_df_modif)
    # match_idx = 0
    # # Print or process matches
    # for match in matches:
    #     match_idx += 1
    #     print(f"Match found between:\n"
    #           f" - DF1: {match['Track 1']}\n"
    #           f" - DF2: {match['Track 2']}\n")

    # print(f"{match_idx} Matches")

    # Create new DataFrames with only one combined column
    spotify_library_combined_df = pd.DataFrame({
        "Track and Artist": spotify_library_df_modif["Track name"] + spotify_library_df_modif["Artist name"]
    })

    mytracklist_combined_df = pd.DataFrame({
        "Track and Artist": mytracklist_df_modif["Track name"] + mytracklist_df_modif["Artist name"]
    })

    temptracklist_combined_df = pd.DataFrame({
        "Track and Artist": temptracklist_df_modif["Track name"] + temptracklist_df_modif["Artist name"]
    })

    # Print to verify (optional)
    print(spotify_library_combined_df.head())
    print(mytracklist_combined_df.head())
    print(temptracklist_combined_df.head())

    test_1 = pd.merge(
        spotify_library_combined_df[['Track and Artist']],
        mytracklist_combined_df[['Track and Artist']],
        on='Track and Artist',
        how='inner'  # 'inner' will return only matching rows
    )

    print(test_1)

    matches = find_matches(spotify_library_combined_df,
                           mytracklist_combined_df)
    match_idx = 0
    # Print or process matches
    for match in matches:
        match_idx += 1
        print(f"Match found between:\n"
              f" - DF1: {match['Track 1']}\n"
              f" - DF2: {match['Track 2']}\n")

    print(f"{match_idx} Matches")


# https://medium.com/@felixpratama242/scraping-spotify-playlist-using-python-and-selenium-17e0175f2db2

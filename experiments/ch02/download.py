import os
import sys
from urllib.parse import urlparse
import pandas as pd
import itertools
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


classes = ["cat", "fish"]
set_types = ["train", "test", "val"]
max_workers = 20
failed_downloads = []


def download_image(url, klass, data_type):
    basename = os.path.basename(urlparse(url).path)
    filename = f"{data_type}/{klass}/{basename}"

    if os.path.exists(filename):
        return

    try:
        response = requests.get(url=url, timeout=(5.0, 10.0))
        if response.status_code == 200:
            with open(filename, "wb") as out_file:
                out_file.write(response.content)
        else:
            raise Exception(f"HTTP status {response.status_code}")
    except Exception as e:
        failed_downloads.append((url, klass, data_type, str(e)))


def prepare_directories():
    for set_type, klass in itertools.product(set_types, classes):
        os.makedirs(f"./{set_type}/{klass}", exist_ok=True)


def save_failed_downloads():
    if failed_downloads:
        df = pd.DataFrame(failed_downloads, columns=["url", "class", "type", "error"])
        df.to_csv("failed_downloads.csv", index=False)
        print(f"Saved {len(failed_downloads)} failed downloads to failed_downloads.csv")


def main():
    if not os.path.exists("./images.csv"):
        print("images.csv not found. Please run the script to generate it.")
        sys.exit(1)

    prepare_directories()
    images_df = pd.read_csv("./images.csv")

    print(f"Downloading {len(images_df)} images using {max_workers} threads...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(download_image, row["url"], row["class"], row["type"])
            for _, row in images_df.iterrows()
        ]

        for _ in tqdm(as_completed(futures), total=len(futures), desc="Downloading"):
            pass

    save_failed_downloads()
    print("Download completed.")


if __name__ == "__main__":
    main()

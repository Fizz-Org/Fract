def fetch_package(cache_dir, source_url, package_data):
    """Download the package and call the sha256 check."""

    import os, requests
    
    # Import tqdm with error handling.
    try:
        from tqdm import tqdm
    except:
        print("\x1b[31mError while loading tqdm, perhaps you didn't install it?\nTo install it, run \x1b[33mpip install tqdm\x1b[31m.\x1b[1m")
        exit(1)

    location = source_url + "/" + package_data["path"]
    filepath = cache_dir + "/" + package_data["filename"]

    # Check cache for already downloaded files.
    if os.path.exists(filepath):
        print("\x1b[32mFile found in cache, no need to download.\x1b[0m")
        return filepath

    # Download with progress bar.
    print("Downloading: " + location)
    try:
        r =  requests.get(location, stream=True)
        r.raise_for_status()
        with open(filepath, "wb") as f, tqdm(
                    total=int(r.headers.get('content-length', 0)), 
                    unit='B', 
                    unit_scale=True, 
                    desc=filepath
                ) as pbar:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
    except Exception as e:
        print("\x1b[31mError ocurred while downloading package:\x1b[0m ", e)
        exit(1)

    # Check sha256 hashes.
    check_sha256(filepath, package_data["sha256"])

    return filepath

def check_sha256(filepath, sha256):
    """Check the sha256 hash to make sure there is no corruption."""

    # Importing hashlib with error handling.
    try:
        import hashlib
    except:
        print("\x1b[31mError while loading hashlib, perhaps you didn't install it?\nTo install it, run \x1b[33mpip install hashlib\x1b[31m.\x1b[1m")
        exit(1)

    # Generate sha256 for downloaded file.
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
    except Exception as e:
        print("Unable to verify that there is no corruption:", e)
        if input("Proceed anyways? [Y/n] ").lower() == "n":
            os.remove(filepath)
            exit(1)
        return False

    # Compare hashes.
    computed_hash = sha256_hash.hexdigest()
    if computed_hash != sha256:
        print(f"Anti-corruption check failed:\nExpected: {sha256}\nRecieved: {computed_hash}")
        if input("Proceed anyways? [Y/n] ") == "n":
            print("Deleting package...")
            os.remove(filepath)
            exit(1)
        return False
    return True

#!/usr/bin/env python3

# === Please note that these might change... ===
head_server = "https://fract.fast-blast.uk"
# ==============================================

import os

class downloader:
    """Fetches the .deb package and saves it to the cache for the rest of the program to use."""
    def __init__(self, package, version=None, cache_folder=os.path.expanduser("~/.cache/fract"), head_server=head_server):
        self.package = package
        self.cache_folder = cache_folder
        self.head_server = head_server
        parts = package.split("/")
        self.source = parts[0]
        self.package_name = "/".join(parts[1:])
        self.version = version

        print("Connecting to main server...")
        source_name, self.source_server = self.get_source()

        print("Connecting to source server...")
        self.data_version, self.package_data = self.get_pkgdata()
        
        print("Getting package location...")
        self.location_fetcher = self.get_location(self)
        if self.data_version == 1:
            self.location, self.sha256, self.filename = self.location_fetcher.v1()

        print("Fetching package...")
        self.package_fetcher = self.fetch_package(self)
        if self.data_version == 1:
            self.package_path = self.package_fetcher.v1()

    def get_source(self):
        import requests

        try:
            r = requests.get(self.head_server+"/index.json")
        except Exception as e:
            print("Could not connect to server:", e)
            exit(1)

        data = r.json()
        
        try:
            name = data[self.source]["name"]
            mirror = data[self.source]["mirror"]
        except:
            print("Source not found.")
            exit(1)

        print("Source found:", name)

        return name, mirror

    def get_pkgdata(self):
        import requests

        try:
            r = requests.get(self.source_server+"/data.json")
        except Exception as e:
            print("Could not connect to mirror:", e)
            exit(1)

        data = r.json()
        if data["schema_version"] == 1:
            try:
                packages_data = data["packages"]
            except:
                print("Data from source not properly formated.")
                exit(1)
            print("Packages data from source found...")

            try:
                package_data = packages_data[self.package_name]
            except:
                print(f"Package \"{self.package_name}\" not found.")
                exit(1)
            print("Package found, loading data...")

            try:
                name = package_data["name"]
                latest_version = package_data["latest"]
                versions_data = package_data["versions"]
                description = package_data["description"]
            except:
                print("Invalid package data structure...")
                exit(1)
            print("Package data received successfully...")
            return 1, {
                    "name": name,
                    "latest_version": latest_version,
                    "versions_data": versions_data,
                    "description": description}

        elif data["schema_version"] == 2:
            try:
                packages_data = data["packages"]
                package_data = packages_data[self.package_name]
                name = package_data["name"]
                latest_version = package_data["latest"]
                version = self.version or latest_version
                version_data = versions[version]
                versions_data = package_data[versions]
                import platform
                arch = platform.machine()
                if arch in versions_data:
                    versions_data = versions_data[arch]
                elif "any" in versions_data:
                    versions_data = versions_data["any"]
                else:
                    print("Architecture not availlable...")
                    exit(1)
                description = package_data["description"]
            except Exception:
                print("Invalid schema v2 structure.")
                exit(1)

            return 2, {
                "name": name,
                "latest_version": latest_version,
                "versions_data": versions_data,
                "description": description
            }

    class get_location:
        def __init__(self, outer):
            self.outer = outer

        def v1(self):
            package_data = self.outer.package_data
            version = self.outer.version or package_data["latest_version"]
            source_server = self.outer.source_server
            versions = package_data["versions_data"]

            try:
                data = versions[version]
                path = data["path"]
                sha256 = data["sha256"]
                filename = data["filename"]
            except:
                print("Invalid versions data structure.")
                exit(1)

            location = source_server + "/" + path

            return location, sha256, filename

    class fetch_package:
        def __init__(self, outer):
            self.outer = outer

        def check_sha256(self, filepath, sha256):
            import hashlib

            sha256_hash = hashlib.sha256()
            try:
                with open(filepath, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        sha256_hash.update(chunk)
            except Exception as e:
                print("Unable to verify that there is no corruption:", e)
                if input("Proceed anyways? [Y/n] ") == "n":
                    os.remove(filepath)
                    exit(1)
                return False

            computed_hash = sha256_hash.hexdigest()
            if computed_hash != sha256:
                print(f"Anti-corruption check failed:\nExpected: {sha256}\nRecieved: {computed_hash}")
                if input("Proceed anyways? [Y/n] ") == "n":
                    print("Deleting package...")
                    os.remove(filepath)
                    exit(1)
                return False
            return True
        
        def v1(self):
            import requests
            try:
                from tqdm import tqdm
            except:
                class tqdm:
                    def __init__(self, *args, **kwargs):
                        pass
                    def __enter__(self):
                        return self
                    def __exit__(self, exc_type, exc_val, exc_tb):
                        pass
                    def update(self, n):
                        pass

            location = self.outer.location
            sha256 = self.outer.sha256
            cache_dir = self.outer.cache_folder
            filepath = cache_dir + "/" + self.outer.filename

            if os.path.exists(filepath):
                print("File found in cache, no need to fetch...")
                return filepath

            print("Downloading:", location)
            try:
                r = requests.get(location, stream=True)
                r.raise_for_status()
                with open(filepath, "wb") as f, tqdm(
                    total=int(r.headers.get('content-length', 0)), 
                    unit='B', 
                    unit_scale=True, 
                    desc=self.outer.filename
                ) as pbar:

                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            except Exception as e:
                print("Error downloading package:", e)
                exit(1)

            print("Checking for corruptions...")
            if not self.check_sha256(filepath, sha256):
                print("Warning: Proceeding despite failed integrity check.")

            print(f"Successfully downloaded package to \"{filepath}\"...")
            return filepath

def check_package(package):
    if not package:
        print("Must specify package.")
        exit(1)

def installer(filepath):
    if input("Install the package? [Y/n] ") == "n":
        return False
    
    import subprocess
    try:
        subprocess.run(["sudo", "dpkg", "-i", filepath], check=True)
    except Exception as e:
        print("dpkg failed to install:", e)
        exit(1)

    return True

# Main guard.
if __name__ == "__main__":
    # Argument Parser
    import argparse
    parser = argparse.ArgumentParser(
            prog="Fract",
            description="The Fizz app store/package manager.",
            epilog="https://github.com/fizz-org")
    parser.add_argument("-S", "--install", dest="install", action='store_true', help="Download and install a package.")
    parser.add_argument("-D", "--download", dest="download", action='store_true', help="Download a package.")
    parser.add_argument("-d", "--devmode", dest="devmode", action='store_true', help="Turns on developer mode.")
    parser.add_argument("-R", "--remove", dest="remove", action="store_true", help="Removes a package.")
    parser.add_argument("package", nargs="?", help="The package name: <source>/<further path and name>.")
    parser.add_argument("-v", "--version", dest="version", help="Choose witch version you want.")
    args = parser.parse_args()
    
    # Devmode setup:
    devmode = args.devmode
    if devmode:
        print("Entering in developer mode...")
        cache_folder = "cache"
    else:
        cache_folder = os.path.expanduser("~/.cache/fract")
    os.makedirs(cache_folder, exist_ok=True)

    if args.install:
        check_package(args.package)
        dl = downloader(args.package, cache_folder=cache_folder, version=args.version)

        if installer(cache_folder + "/" + dl.filename):
            print("Installation completed successfuly.")
            exit(0)
        else:
            print("Installation cancelled...")
            exit(1)
    elif args.download:
        import shutil

        check_package(args.package)
        dl = downloader(args.package, cache_folder=cache_folder)
        
        deb_path = dl.package_path
        target_path = os.path.join(os.getcwd(), dl.filename)
        
        try:
            shutil.copy2(deb_path, target_path)
            print("Package file can be found at:", target_path)
        except Exception as e:
            print("Failed to copy package to current working dirrectory:", e)
            exit(1)

    elif args.remove:
        package_name = args.package

        if "/" in package_name:
            print("Do not use source for removing.")
            exit(1)

        print(f"Uninstalling '{package_name}' from system...")
        try:
            import subprocess
            subprocess.run(["sudo", "dpkg", "-r", package_name], check=True)
            print(f"Successfully uninstalled '{package_name}'.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to uninstall '{package_name}':", e)

print("Run with the -h tag for help.")

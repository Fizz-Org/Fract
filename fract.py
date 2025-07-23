#!/usr/bin/env python3

# === Please note that these might change... ===
head_server = "https://fract.fast-blast.uk"
# ==============================================

import os

class downloader:
    """Fetches the .deb package and saves it to the cache for the rest of the program to use."""
    def __init__(self, package, cache_folder=os.path.expanduser("~/.cache/fract"), head_server=head_server):
        self.package = package
        self.cache_folder = cache_folder
        self.head_server = head_server
        self.source = package.split(os.sep)[0]
        self.package_name = os.sep.join(package.split(os.sep)[1:])

        print("Connecting to main server...")
        source_name, self.source_server = self.get_mirror()

        print("Connecting to source server...")
        self.data_version, self.package_data = self.get_pkgdata()

        if self.data_version == 1:
            location = get_location.v1()

    def get_mirror(self):
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
            print("Package data recieved successfully...")
            return 1, {
                    "name": name,
                    "latest_version": latest_version,
                    "versions_data": versions_data,
                    "description": description}
        else:
            print("Unknown data structure at mirror data.")
            exit(1)

    class get_location:
        def __init__(self, data):
            pass
            

# Main guard.
if __name__ == "__main__":
    # Argument Parser
    import argparse
    parser = argparse.ArgumentParser(
            prog="Fract",
            description="The Fizz app store/package manager.",
            epilog="https://github.com/fizz-org")
    parser.add_argument("-S", "--install", dest="install", action='store_true')
    parser.add_argument("-D", "--download", dest="download", action='store_true')
    parser.add_argument("-d", "--devmode", dest="devmode", action='store_true')
    parser.add_argument("package", nargs="?")
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
        dl = downloader(args.package, cache_folder=cache_folder)
        # dpkg code.
    elif args.download:
        dl = downloader(args.package, cache_folder=cache_folder)
        # fetch from cache to working directory

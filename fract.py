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
        
        self.location_fetcher = self.get_location(self)
        if self.data_version == 1:
            self.location, self.sha256 = self.location_fetcher.v1()

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
            except:
                print("Invalid versions data structure.")
                exit(1)

            location = source_server + "/" + path

            return location, sha256

def check_package(package):
    if not package:
        print("Must specify package.")
        exit(1)

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
    parser.add_argument("-v", "--version", dest="version")
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
        # dpkg code.
    elif args.download:
        check_package(args.package)
        dl = downloader(args.package, cache_folder=cache_folder)
        # fetch from cache to working directory

def install(filepath):
    """Install a .deb file."""

    # Verify installation.
    if input("Install the package? [Y/n] ").lower() == "n":
        print("Aborting installation...")
        exit()

    import subprocess as sp

    # Attempt installation.
    try:
        sp.run(["sudo", "dpkg", "-i", filepath], check=True)
    except Exception as e:
        print(f"\x1b[31mdpkg failed to install due to:\x1b[0m {e}")
        exit(1)

    print("\x1b[32mInstallation success.\x1b[0m")

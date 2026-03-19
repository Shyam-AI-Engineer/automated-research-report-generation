import importlib.metadata
import re

REQUIREMENTS_PATH = "requirements.txt"

def get_installed_version(pkg_name):
    try:
        return importlib.metadata.version(pkg_name)
    except importlib.metadata.PackageNotFoundError:
        return None

def normalize_package_name(pkg_line):
    """Handles editable installs, extras, and version stripping."""
    pkg_line = pkg_line.strip()
    if pkg_line.startswith("-e") or pkg_line.startswith("--"):
        return None  # Ignore editable installs or options
    pkg_name = re.split(r"[=<>!]", pkg_line)[0].strip()
    return pkg_name
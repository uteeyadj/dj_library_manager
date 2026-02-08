import json
import urllib.request
from importlib.metadata import version, PackageNotFoundError
from rich.console import Console
from rich.text import Text

console = Console()

PYPI_URL = "https://pypi.org/pypi/dj-library-manager/json"

def check_for_updates():
    try:
        # Get installed version
        try:
            installed = version("dj-library-manager")
        except PackageNotFoundError:
            return  # Not installed via pip

        # Fetch PyPI version
        with urllib.request.urlopen(PYPI_URL, timeout=2) as response:
            data = json.loads(response.read().decode())
            latest = data["info"]["version"]

        if installed != latest:
            console.print(
                Text(
                    f"Update available: {installed} → {latest}\n"
                    f"Run: pip install --upgrade dj-library-manager",
                    style="bold yellow",
                )
            )

    except Exception:
        # Silent fail — no internet, PyPI down, etc.
        pass

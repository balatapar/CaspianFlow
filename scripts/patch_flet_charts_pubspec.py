from pathlib import Path
import importlib.metadata


OVERRIDE_BLOCK = """dependency_overrides:
  vector_math: ^2.2.0
  collection: ^1.19.0
"""


def patch_pubspec(pubspec: Path) -> None:
    text = pubspec.read_text()

    if "../../../../../../../packages/flet" in text:
        print(f"Patching flet path reference in {pubspec}")
        text = text.replace(
            "    path: ../../../../../../../packages/flet",
            "    version: ^0.86.5",
        )

    if "dev_dependencies:" in text and "dependency_overrides:" not in text:
        print(f"Adding version overrides to {pubspec}")
        text = text.replace(
            "dev_dependencies:",
            OVERRIDE_BLOCK + "dev_dependencies:",
            1,
        )

    pubspec.write_text(text)
    print(f"Patched {pubspec}:\n{pubspec.read_text()}")


def patch_site_packages() -> None:
    base = importlib.metadata.distribution("flet-charts").locate_file("")
    pubspec = Path(base) / "flutter" / "flet_charts" / "pubspec.yaml"
    if pubspec.exists():
        patch_pubspec(pubspec)
    else:
        print(f"flet-charts pubspec not found at {pubspec}")


def main() -> None:
    patch_site_packages()


if __name__ == "__main__":
    main()

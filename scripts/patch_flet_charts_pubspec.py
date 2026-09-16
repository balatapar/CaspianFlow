from pathlib import Path
import importlib.metadata


def main() -> None:
    base = importlib.metadata.distribution("flet-charts").locate_file("")
    pubspec = Path(base) / "flutter" / "flet_charts" / "pubspec.yaml"
    print(f"Patching {pubspec}")
    text = pubspec.read_text()
    text = text.replace(
        "    path: ../../../../../../../packages/flet",
        "    version: ^0.86.5",
    )
    pubspec.write_text(text)
    print("Patched pubspec.yaml:")
    print(pubspec.read_text())


if __name__ == "__main__":
    main()

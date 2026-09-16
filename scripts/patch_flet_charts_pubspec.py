from pathlib import Path


def main() -> None:
    base = Path.cwd() / "build"
    if not base.exists():
        print(f"build directory not found: {base}")
        return

    pubspecs = list(base.rglob("pubspec.yaml"))
    if not pubspecs:
        print("No pubspec.yaml found under build/")
        return

    for pubspec in pubspecs:
        text = pubspec.read_text()
        if "../../../../../../../packages/flet" in text:
            print(f"Patching {pubspec}")
            text = text.replace(
                "    path: ../../../../../../../packages/flet",
                "    version: ^0.86.5",
            )
            pubspec.write_text(text)
            print("Patched content:")
            print(pubspec.read_text())
        else:
            print(f"Skipping {pubspec} (already patched or not affected)")


if __name__ == "__main__":
    main()

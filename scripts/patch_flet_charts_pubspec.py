from pathlib import Path


OVERRIDE_BLOCK = """dependency_overrides:
  vector_math: ^2.2.0
"""


def is_root_pubspec(text: str) -> bool:
    return "dev_dependencies:" in text or "flutter_test:" in text


def patch_pubspec(pubspec: Path) -> None:
    text = pubspec.read_text()

    if "../../../../../../../packages/flet" in text:
        print(f"Patching flet path reference in {pubspec}")
        text = text.replace(
            "    path: ../../../../../../../packages/flet",
            "    version: ^0.86.5",
        )

    if is_root_pubspec(text) and "dependency_overrides:" not in text:
        print(f"Adding vector_math override to {pubspec}")
        if "dev_dependencies:" in text:
            text = text.replace(
                "dev_dependencies:",
                OVERRIDE_BLOCK + "dev_dependencies:",
                1,
            )
        else:
            text = text.rstrip() + "\n" + OVERRIDE_BLOCK

    pubspec.write_text(text)
    print(f"Patched {pubspec}:\n{pubspec.read_text()}")


def main() -> None:
    base = Path.cwd() / "build"
    if not base.exists():
        print(f"build directory not found: {base}")
        return

    pubspecs = sorted(base.rglob("pubspec.yaml"))
    if not pubspecs:
        print("No pubspec.yaml found under build/")
        return

    # Only patch the root app pubspec (the one that is a Flutter app, not a package)
    root_pubspecs = [p for p in pubspecs if is_root_pubspec(p.read_text())]
    targets = root_pubspecs if root_pubspecs else pubspecs

    for pubspec in targets:
        try:
            patch_pubspec(pubspec)
        except Exception as e:
            print(f"Error patching {pubspec}: {e}")


if __name__ == "__main__":
    main()

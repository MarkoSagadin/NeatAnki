import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def build_assets(project_root: Path = PROJECT_ROOT) -> None:
    """Build frontend assets and copy html templates into src/nanki/assets/.

    Can be run standalone during development:
        python build_assets.py
    """
    frontend_dir = project_root / "frontend"
    dist_dir = frontend_dir / "dist"
    html_templates_dir = project_root / "html_templates"
    assets_dir = project_root / "src" / "nanki" / "assets"

    # Step 0: Delete and create an empty assets dir
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
    assets_dir.mkdir(parents=True)

    sass_files = [str(x) for x in frontend_dir.glob(pattern="src/themes/*.sass")]

    # Step 1: Build frontend assets
    subprocess.run(  # noqa: S603 - Input is known
        ["/usr/bin/bun", "build_theme.js", *sass_files],
        cwd=str(frontend_dir),
        check=True,
    )

    # Step 2: Copy built assets into assets/
    shutil.copytree(str(dist_dir), str(assets_dir / "dist"), dirs_exist_ok=True)

    # Step 3: Copy html templates into assets/
    shutil.copytree(
        str(html_templates_dir),
        str(assets_dir / "html_templates"),
        dirs_exist_ok=True,
    )


if __name__ == "__main__":
    build_assets()

# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller recipe for the portable Windows one-folder application."""

from pathlib import Path


PROJECT_ROOT = Path(SPEC).resolve().parent
SOURCE_ROOT = PROJECT_ROOT / "src"
CONFIG_ROOT = SOURCE_ROOT / "phase_annotator" / "config"

# List release-critical resources explicitly. A new packaged procedure should
# require an intentional recipe change and will be verified after the build.
ontology_data = [
    (str(CONFIG_ROOT / "default_appendectomy.json"), "phase_annotator/config"),
    (
        str(CONFIG_ROOT / "cholec80_cholecystectomy.json"),
        "phase_annotator/config",
    ),
]

analysis = Analysis(
    [str(SOURCE_ROOT / "phase_annotator" / "__main__.py")],
    pathex=[str(SOURCE_ROOT)],
    binaries=[],
    datas=ontology_data,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="PhaseAnnotator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

application = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="PhaseAnnotator",
)

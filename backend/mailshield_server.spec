# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

project_root = Path(SPECPATH).resolve().parent if 'SPECPATH' in globals() else Path('.').resolve()
if not (project_root / 'ml' / 'artifacts').exists():
    project_root = Path('.').resolve()

block_cipher = None

hidden_imports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespans',
    'uvicorn.lifespans.on',
    'uvicorn.lifespans.off',
    'fastapi',
    'pydantic',
    'pydantic_settings',
    'sqlalchemy',
    'sqlalchemy.sql.default_comparator',
    'sqlite3',
    'bcrypt',
    'jwt',
    'joblib',
    'sklearn',
    'sklearn.utils._typedefs',
    'sklearn.neighbors._typedefs',
    'sklearn.tree._utils',
    'sklearn.linear_model',
    'sklearn.naive_bayes',
    'sklearn.svm',
    'sklearn.calibration',
    'sklearn.feature_extraction.text',
    'sklearn.metrics',
    'numpy',
    'scipy',
    'scipy.special',
    'scipy.linalg',
    'pandas',
    'mailshield_ml',
    'mailshield_ml.dataset',
    'mailshield_ml.models',
    'mailshield_ml.pipeline',
    'mailshield_ml.explainability',
    'mailshield_ml.evaluation',
    'mailshield_ml.language',
    'mailshield_ml.phishing_risk',
    'mailshield_ml.multilingual_features',
    'cryptography',
    'cryptography.hazmat.primitives.ciphers.aead',
    'cryptography.hazmat.primitives.kdf.hkdf',
    'cffi',
]

artifacts_path = str(project_root / 'ml' / 'artifacts')
data_path = str(project_root / 'ml' / 'data')
datas = [
    (artifacts_path, 'ml/artifacts'),
    (data_path, 'ml/data'),
]

a = Analysis(
    [str(project_root / 'backend' / 'server_entry.py')],
    pathex=[str(project_root), str(project_root / 'backend'), str(project_root / 'ml' / 'src')],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PIL', 'torch', 'tensorflow'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mailshield_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='mailshield_server',
)

# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for ATC Management System.
Bundles the entire Django project into a single portable folder.
"""
import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

PROJECT_DIR = os.path.abspath('.')

# Collect ALL Django submodules (templates, locale, etc.)
django_hiddenimports = collect_submodules('django')

# Our app modules
app_hiddenimports = (
    collect_submodules('core') +
    collect_submodules('factory') +
    collect_submodules('depot') +
    collect_submodules('expenses') +
    collect_submodules('finance') +
    collect_submodules('atc_management')
)

all_hiddenimports = django_hiddenimports + app_hiddenimports + [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.template.defaulttags',
    'django.template.defaultfilters',
    'django.template.loader_tags',
    'django.templatetags.static',
    'django.templatetags.i18n',
]

# Collect Django's data files (templates, locale, etc.)
django_datas = collect_data_files('django', include_py_files=True)

# Our project files to bundle
project_datas = [
    # Templates
    (os.path.join(PROJECT_DIR, 'templates'), 'templates'),
    # Static files
    (os.path.join(PROJECT_DIR, 'static'), 'static'),
    # App directories (need migrations, management commands, templatetags)
    (os.path.join(PROJECT_DIR, 'core'), 'core'),
    (os.path.join(PROJECT_DIR, 'factory'), 'factory'),
    (os.path.join(PROJECT_DIR, 'depot'), 'depot'),
    (os.path.join(PROJECT_DIR, 'expenses'), 'expenses'),
    (os.path.join(PROJECT_DIR, 'finance'), 'finance'),
    (os.path.join(PROJECT_DIR, 'atc_management'), 'atc_management'),
]

all_datas = django_datas + project_datas

a = Analysis(
    ['launcher.py'],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', '_tkinter', 'matplotlib', 'numpy', 'scipy',
        'PIL', 'Pillow', 'pytest', 'unittest',
    ],
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
    name='ATC_Management_System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console to show server logs
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ATC_Management_System',
)

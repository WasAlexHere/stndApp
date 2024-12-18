from setuptools import setup

APP = ["app.py"]
DATA_FILES = [
    "main.png",
    "up.png",
    "down.png",
    "trophy.png",
    "edit.png",
    "rest.png",
    "fail.png",
    "success.png"
]
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleShortVersionString': '1.4.0',
        'LSUIElement': True,
    },
    'packages': ['rumps'],
}

setup(
    app=APP,
    name='StndApp',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=OPTIONS['packages']
)

# python setup.py py2app
from setuptools import find_packages, setup

with open("README.md", "r") as README:
    long_description = README.read()

setup(
    name="subtoaudio",
    packages=['subtoaudiotes'],
    version="0.1",
    license="MPL 2.0",
    description="Generate audio or speech from any subtitle file",
    author="Bagas Nugroho Santoso",
    author_email="bagassantoso71@gmail.com",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/bnsantoso/",
    install_requires=["TTS","pydub","librosa"],
    keywords=["subtitle", "tts", "text to audio", "subtitle to audio", "subtitle to speech"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
)
    
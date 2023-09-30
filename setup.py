from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as readme_file:
    README = readme_file.read()

setup(
    name="subtoaudio",
    packages=find_packages(exclude=[]),
    version="0.1.5",
    license="MPL 2.0",
    description="Subtitle to Audio, generate audio or speech from any subtitle file",
    author="Bagas NS",
    author_email="bagassantoso71@gmail.com",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/bnsantoso/",
    install_requires=["pydub","librosa","ffmpeg-python"],
    keywords=["subtitle", "tts", "text to audio", "subtitle to audio", "subtitle to speech",],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
)
    

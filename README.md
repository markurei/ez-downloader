
# EZ Downloadrer

A utility to easily download games from specific sites.

## Getting Started

### Download

Check the releases.

### Installation

Extract all contents of release .rar and open the .exe file.

### Using the application

Paste a game URL and set the save directory then click proceed.


### Uninstallation

No need. Just delete the files.

### Dependencies

Created using
* Python 3.11 (or above) with Tkinter support enabled
* Windows 11

Used modules
* pyinstaller
* customtkinter
* BeautifulSoup
* Pypdl

### Build binary manually

Prepare a Windows environment with Python and Tkinter installed and all module dependencies installed using `pip`.
1. Execute below command in a Linux environment terminal:
```
pyinstaller --onefile --windowed --name EZDownloader --icon=src/app.ico --noconsole main.py
```

## Authors

Contributors and contact info

👤 **markurei**

* Github: [@markurei](https://github.com/markurei)
* Email: deckofalltrades@gmail.com

## Version History

🆕 2.0

* Now with GUI support using Tkinter!

  
## License

This project is licensed under the MIT License.


## Acknowledgments

This is a very basic Python application and is made possible by these awesome repos

* [pyinstaller](https://github.com/pyinstaller/pyinstaller)
* [customtkinter](https://github.com/TomSchimansky/CustomTkinter)
* [pypdl](https://github.com/mjishnu/pypdl)
* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
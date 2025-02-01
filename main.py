import requests
from bs4 import BeautifulSoup
from pypdl import Pypdl
from tkinter import Tk
from tkinter.filedialog import askdirectory
import os
import time
import shutil 

# Defines
file_hoster = "https://fuckingfast.co"
target_url = ""
repack_size = "Unavailable"
downloader_instance = None
path = ""
all_links = []
dl_links = []
skip_optional = False

def getDownloadFileSize(size_results):
    size_bytes = float(0.0)
    if len(size_results) > 0:
        if size_results[1].string.split(" ")[1] != "":
            size = size_results[1].string.split(" ")[1]
            if "MB" in size:
                size_bytes = float(size.replace("MB",""))
            elif "KB" in size:
                size_bytes = float(size.replace("KB","")) * 1024
    return round(size_bytes, 1)

def getLocalFileSize(file_path):
    file_stats = os.stat(file_path)
    return round(file_stats.st_size / (1024 * 1024), 1)

def getTotalDownloadSize(data):
    size = repack_size
    all_text = data.get_text().splitlines()
    for text in all_text:
        if "Repack Size" in text:
            size = text.replace("Repack Size: ", "").replace("from ","").replace(" [Selective Download]", "")
    return size

def getFreeDiscSpace(chosen_path):
    free_space = "Unavailable"
    space = shutil.disk_usage(chosen_path).free
    if space > 1024:
        space = space / 1024
        free_space = f"{round(space, 2)} KB"
        if space > 1024:
            space = space / 1024
            free_space = f"{round(space, 2)} MB"
            if space > 1024:
                space = space / 1024
                free_space = f"{round(space, 2)} GB"
    return free_space

def verifyAllDownloadedFiles(path,reference_data):
    err = 0
    for index, data in enumerate(reference_data):
        save_path = f"{path}/{data["file_name"]}"

        if os.path.isfile(save_path):
            # Compare local file size vs download size
            if float(data["size_bytes"]) != 0.0 and float(getLocalFileSize(save_path)) >= float(data["size_bytes"]):
                print('\033[32m'+"[✓]", end="")
                print('\033[39m', end=" ")
                print(f"{index+1:03d}: {data["file_name"]} is OK!")
            else:
                print('\033[31m'+"[x]", end="")
                print('\033[39m', end=" ")
                print(f"{index+1:03d}: {data["file_name"]} is corrupted!")
                print(f"    Downloaded: {getLocalFileSize(save_path)}MB / {data["size_bytes"]}MB")
                err = 1
        else:
            print('\033[31m'+"[x]", end="")
            print('\033[39m', end=" ")
            print(f"{index+1:03d}: {data["file_name"]} is missing!")
            print(f"    Download size: {data["size_bytes"]}MB")
    
    if err == 0:
        printBrightCyan("\nSince game updates are downloaded separately,")
        printBrightCyan("please check back the game page if there are \nupdates available and download it manually!")
        printGreen("\nAll downloads have completed!\n")
    else:
        printRed("\nSome files are corrupted or missing!")
        printRed("Please run the app again to redownload corrupted or missing files\n")

def printGreen(text):
    print('\033[32m' + text)
    print('\033[39m', end="")

def printRed(text):
    print('\033[31m' + text)
    print('\033[39m', end="")

def printYellow(text):
    print('\033[33m' + text)
    print('\033[39m', end="")

def printViolet(text):
    print('\033[35m' + text)
    print('\033[39m', end="")

def printBrightCyan(text):
    print('\033[96m' + text)
    print('\033[39m', end="")

def main():
    try:
        printViolet("\n╔════════════════════════╗\n║ EZ Downloader by Mark  ║\n╚════════════════════════╝")
        print("\n\nWhere to save the files?")
        path = askdirectory(title='Select Folder')
        if path == "":
            printRed("\nError: No folder selected!")
            input("\nPress [Enter] to exit ")
            os._exit(0)
        print("Saving files to",end=" ")
        printYellow(path)

        print("\nEnter or Paste the URL (right-click): ")
        print('\033[33m', end="")
        target_url = input()
        print('\033[39m', end="")
        if target_url == "":
            printRed("Error: No URL entered!")
            input("\nPress [Enter] to exit ")
            os._exit(0)

        print("\nSkip optional language/mod/textures pack/video files? [Y/N]: ")
        print('\033[33m', end="")
        while(True):
            print("\033[K", end="\r")
            tmp = input()            
            if(tmp.capitalize() == "Y"):
                skip_optional = True
                break
            elif(tmp.capitalize() == "N"):
                skip_optional = False
                break
            else:
                print("\033[A", end="\r")
                continue
        print('\033[39m', end="")

        # Send a GET request to the URL
        print("\n• Checking available links...")
        response = requests.get(target_url)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get repack size
        repack_size = getTotalDownloadSize(soup)

        # Find all elements with a specific tag
        links = soup.find_all('a')

        # Get all links
        for link in links:
            if file_hoster in link.get('href'):
                if skip_optional:
                    if "fg-optional-bonus" in link.text or "fg-selective-bonus" in link.text:
                        pass
                    elif "fg-optional" in link.text or "fg-selective" in link.text:
                        continue
                all_links.append({
                    "file_name": link.text,
                    "url": link.get('href')
                })

        if not all_links:
            printRed(f"\nError: No {file_hoster} links were found!")
            input("\nPress [Enter] to exit ")
            os._exit(0)

        # Get the actual DL links
        printGreen("OK!")
        print("\n• Getting all direct links from host...")
        for links in all_links:
            response = requests.get(links["url"])

            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.select_one("script:-soup-contains('window.open')").string
            size_results = soup.find_all('span')

            for link in results.splitlines():
                if file_hoster in link:
                    dl_links.append({
                        "file_name": links["file_name"],
                        "direct_url": link.replace("        window.open(\"", "").replace("\")", ""),
                        "size_bytes": getDownloadFileSize(size_results)
                    })
                    print(f"{len(dl_links)} / {len(all_links)} ({round((len(dl_links) / len(all_links)) * 100 , 1)}%)",end='\r')

        if not dl_links:
            printRed("\nError: No direct links were found!")
            input("\nPress [Enter] to exit ")
            os._exit(0)

        verifyAllDownloadedFiles(path, dl_links)
        exit()

        printGreen("\nOK!")
        printViolet("\nDownload Information")
        print(f"File Hoster: {file_hoster}\nNumber of Files: ", end="")
        printBrightCyan(f"{len(dl_links)}")
        print("Repack Size: ", end="")
        printBrightCyan(f"{repack_size}")
        print("Free Space: ", end="")
        printBrightCyan(f"{getFreeDiscSpace(path)}")
        printYellow("Make sure you have enough free space!")
        choice = input("\nEnter [Y] to proceed: ")
        if choice.capitalize() == 'Y':
            printViolet("\n\nStarting Downloads")
        else:
            print("Closing application...")
            input("\nPress [Enter] to exit ")
            os._exit(0)

        # Start downloading
        downloader_instance = Pypdl(allow_reuse=True)
        for index, dl_link in enumerate(dl_links):
            save_path = f"{path}/{dl_link["file_name"]}"
            if os.path.isfile(save_path):
                # Compare local file size vs download size
                if float(dl_link["size_bytes"]) != 0.0 and float(getLocalFileSize(save_path)) >= float(dl_link["size_bytes"]):
                    print('\033[32m'+"[✓]", end="")
                    print('\033[39m', end=" ")
                    print(f"{index+1:03d}: {dl_link["file_name"]} already exist. Skipping...")
                    continue
            printYellow(f"\n{index+1:03d}: {dl_link["file_name"]}")
            print(f"Download size: ", end="")
            printBrightCyan(f"{dl_link["size_bytes"]}MB")
            print('\033[31m'+"[x]", end="")
            print('\033[39m', end=" ")
            print("Close the app to stop the download")
            downloader_instance.start(
                url=dl_link["direct_url"],
                file_path=save_path,
                display=True, 
                block=True,
                clear_terminal=False
            )
            print("Finishing up...")
            time.sleep(10)
            printGreen("Download completed!")
        downloader_instance.shutdown()
        printViolet("\n\nDownload Verification")
        verifyAllDownloadedFiles(path, dl_links)
        input("\nPress [Enter] to exit ")
        os._exit(0)
    except Exception as e:
        printRed("\nSomething went wrong!")
        printRed(f"Error message: {repr(e)}")
        input("\nPress [Enter] to exit ")
        os._exit(0)

main()

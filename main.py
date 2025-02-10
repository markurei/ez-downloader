import os
import time
import shutil
import requests
import tkinter
import customtkinter
from pypdl import Pypdl
from threading import Thread
from functools import partial
from bs4 import BeautifulSoup
from tkinter.filedialog import askdirectory

APP_WIDTH=695
APP_HEIGHT=310
DLPAGE_WIDTH=960
DLPAGE_HEIGHT=570
APP_ICON="src/app.ico"
LOADING_ICON="src/loading.ico"
ERROR_ICON="src/error.ico"
VERSION="v2.0"
NAME="EZDownloader by Mark"
MAIN_FONT_SIZE=18
SUB_FONT_SIZE=16
MINI_FONT_SIZE=12
FONT_STYLE="Segoe UI"
BUTTON_FONT_STYLE="Segoe UI Bold"
FILE_HOSTERS=["FuckingFast.co"]

file_hoster = "https://fuckingfast.co"
all_links = []
dl_links = []
remaining_dl_index = []
game_name = ""
game_info = ""
checkbox_var_list = []
checkbox_widget_list = []
dl_label_list = []
total_dl_size = float(0.0)
second_screen_widgets = []
onToggleEnable = True

customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("src/app-theme.json")
app = customtkinter.CTk()
save_directory=customtkinter.StringVar()
game_url = customtkinter.StringVar()
links_obtained = customtkinter.StringVar()

def onClosePrompt():
    toplevel.destroy()
    all_links.clear()

def onRefreshClick():
    print("Refresh")
    verifyAllDownloadedFiles(dl_links)
    downloaded_size = float(0.0)
    path_t = save_directory.get()
    color = "#707070"
    for index, dl_link in enumerate(dl_links):
        if index in remaining_dl_index:
            state = tkinter.DISABLED
            text = "COMPLETED"
            color = "#4DA1A9"
            downloaded_size = downloaded_size + dl_link["size_mb"]
        else:
            state = tkinter.NORMAL
            text = f"{dl_link["size_mb"]} MB"
            if os.path.isfile(f"{path_t}/{dl_link["file_name"]}"):
                text = "CORRUPTED"
                color = "#EC5E5E"
            else:
                text = f"{dl_link["size_mb"]} MB"
                color = "#707070"       

        checkbox_widget_list[index].configure(state=state)
        dl_label_list[index].configure(text=text)
        dl_label_list[index].configure(text_color=color)
    second_screen_widgets[5].configure(text=f"Free Space: {getFreeDiscSpace()} | Downloaded: {downloaded_size} MB / {round(total_dl_size,2)} MB ({len(remaining_dl_index)}/{len(dl_links)})")

def getFreeDiscSpace():
    free_space = "Unavailable"
    space = shutil.disk_usage(save_directory.get()).free
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

def onAllDownloadFinish(event):
    verifyAllDownloadedFiles(dl_links)
    for index, dl_link in enumerate(dl_links):
        if index in remaining_dl_index:
            state = tkinter.DISABLED
        else:
            state = tkinter.NORMAL
        checkbox_widget_list[index].configure(state=state)
    second_screen_widgets[4].configure(state="normal")
    second_screen_widgets[4].configure(text="START DOWNLOAD")
    second_screen_widgets[6].configure(state="normal")
    second_screen_widgets[7].configure(state="normal")

def onOneDownloadFinish(event):
    verifyAllDownloadedFiles(dl_links)
    downloaded_size = float(0.0)
    path_t = save_directory.get()
    color = "#707070"
    for index, dl_link in enumerate(dl_links):
        value = checkbox_var_list[index].get()
        if index in remaining_dl_index:
            text = "COMPLETED"
            color = "#4DA1A9"
            downloaded_size = downloaded_size + dl_link["size_mb"]
            value = "off"
        else:
            text = f"{dl_link["size_mb"]} MB"
            if os.path.isfile(f"{path_t}/{dl_link["file_name"]}"):
                text = "CORRUPTED"
                color = "#EC5E5E"
            else:
                text = f"{dl_link["size_mb"]} MB"
                color = "#707070"            
        
        checkbox_var_list[index].set(value=value)
        dl_label_list[index].configure(text=text)
        dl_label_list[index].configure(text_color=color)
    second_screen_widgets[5].configure(text=f"Free Space: {getFreeDiscSpace()} | Downloaded: {downloaded_size} MB / {round(total_dl_size,2)} MB ({len(remaining_dl_index)}/{len(dl_links)})")

def onOtainedAllLinksComplete(event):
    app.unbind('<<ThreadFinished>>')
    invokeDownloadPage()

def threadedDownload(download_object,second_screen_widgets,root):
    try:
        downloader_instance = Pypdl(allow_reuse=True)
        for index, dl_link in enumerate(download_object):
            second_screen_widgets[1].configure(text=dl_link["file_name"])
            second_screen_widgets[2].configure(text="Downloading...")
            second_screen_widgets[3].configure(text=f"0 MB / {dl_link["size_mb"]} MB")
            save_path = f"{save_directory.get()}/{dl_link["file_name"]}"
            future = downloader_instance.start(
                url=dl_link["direct_url"],
                file_path=save_path,
                display=False,
                block=False
            )
            while not downloader_instance.completed:
                if downloader_instance.speed:
                    second_screen_widgets[2].configure(text=f"{round(downloader_instance.speed,2)} MB/s")
                if downloader_instance.current_size:
                    total_download = round(downloader_instance.current_size / (1024 * 1024),1)
                    second_screen_widgets[3].configure(text=f"{total_download} MB / {dl_link["size_mb"]} MB")
                    second_screen_widgets[0].set(float(total_download / dl_link["size_mb"]))                
                time.sleep(0.5)
            if len(downloader_instance.failed) > 0:
                print("Error download")
                 # TODO: handle error case
                second_screen_widgets[2].configure(text="Error in downloading...")
                time.sleep(2)
            elif downloader_instance.completed:
                second_screen_widgets[0].set(1)
                second_screen_widgets[2].configure(text="Finalizing...")
                second_screen_widgets[3].configure(text=f"{dl_link["size_mb"]} MB / {dl_link["size_mb"]} MB")
                time.sleep(5)
            root.event_generate('<<DownloadFinished>>')
            second_screen_widgets[2].configure(text="")
            second_screen_widgets[0].set(0)
        downloader_instance.shutdown()
        second_screen_widgets[3].configure(text="")
        second_screen_widgets[1].configure(text="No ongoing downloads")
    except Exception as e:
        # TODO: handle error case
        print(f"Error message: {repr(e)}")
        root.event_generate('<<DownloadFinished>>')
        time.sleep(0.5)

    root.event_generate('<<AllDownloadFinished>>')

def onStartDwonload():
    download_list = []

    for index, checkbox in enumerate(checkbox_widget_list):
        if checkbox.get() == "on":
            download_list.append(dl_links[index])        

    if len(download_list) > 0:
        for index, checkbox in enumerate(checkbox_widget_list):
            checkbox.configure(state="disabled")

        second_screen_widgets[4].configure(state="disabled")
        second_screen_widgets[4].configure(text="DOWNLOAD STARTED")
        second_screen_widgets[6].configure(state="disabled")
        second_screen_widgets[7].configure(state="disabled")
        
        # Start downloading
        thread = Thread(target = threadedDownload, args=[download_list,second_screen_widgets,dlPage], daemon=True)
        thread.start()
    else:
        print("No items to download")

def getLocalFileSize(file_path):
    file_stats = os.stat(file_path)
    return round(file_stats.st_size / (1024 * 1024), 1)

def verifyAllDownloadedFiles(reference_data):
    err = 0
    remaining_dl_index.clear()
    for index, data in enumerate(reference_data):
        save_path = f"{save_directory.get()}/{data["file_name"]}"

        if os.path.isfile(save_path):
            # Compare local file size vs download size
            if float(data["size_mb"]) != 0.0 and float(getLocalFileSize(save_path)) >= float(data["size_mb"]):
                # print(f"{index+1:03d}: {data["file_name"]} is OK!")
                remaining_dl_index.append(index)
            else:
                # print(f"{index+1:03d}: {data["file_name"]} is corrupted!")
                # print(f"    Downloaded: {getLocalFileSize(save_path)}MB / {data["size_mb"]}MB")
                err = 1
        else:
            print(f"{index+1:03d}: {data["file_name"]} is missing!")
            # print(f"    Download size: {data["size_mb"]}MB")
    
    if err == 0:
        print("\nAll downloads have completed!\n")
    else:
        print("\nSome files are corrupted or missing!\n")

def onToggleButtonClick():
    global onToggleEnable
    for checkbox in checkbox_widget_list:
        if checkbox.cget("state") == tkinter.NORMAL:
            if onToggleEnable:                
                checkbox.deselect()
            else:
                checkbox.select()
    onToggleEnable = not onToggleEnable    

def getDownloadFileSize(size_results):
    size_mb = float(0.0)
    if len(size_results) > 0:
        if size_results[1].string.split(" ")[1] != "":
            size = size_results[1].string.split(" ")[1]
            if "MB" in size:
                size_mb = float(size.replace("MB",""))
            elif "KB" in size:
                size_mb = float(size.replace("KB","")) * 1024
    return round(size_mb, 1)

def getAllLinks(progressBar, caller, root):
    print("Starting thread")
    try:
        # Send a GET request to the URL
        response = requests.get(game_url.get())

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get game name
        global game_name
        name_container = soup.find("h3")
        game_name = name_container.find('strong').text.strip()

        # Get game info
        global game_info
        game_info_container = soup.find("p")
        game_info = game_info_container.text.strip().split("\n\n")[0]

        # Find all elements with a specific tag
        links_container = soup.find_all('li')
        index = 0
        for i, link in enumerate(links_container):
            if "Filehoster: FuckingFast" in link.text:
                index = i
                break
        links = links_container[index].find_all('a')

        # Get all links
        for link in links:
            if file_hoster in link.get('href'):
                all_links.append({
                    "file_name": link.text,
                    "url": link.get('href')
                })

        if not all_links:
            time.sleep(3)
            showErrorPopup(caller, "Error: No supported links are found!")
            return
        
        progressBar.stop()
        progressBar.configure(mode="determinate")
        progressBar.set(0)
        
        # Get the actual DL links
        for links in all_links:
            response = requests.get(links["url"])

            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.select_one("script:-soup-contains('window.open')").string
            size_results = soup.find_all('span')

            for link in results.splitlines():
                if file_hoster in link:
                    size_t = getDownloadFileSize(size_results)
                    dl_links.append({
                        "file_name": links["file_name"],
                        "direct_url": link.replace("        window.open(\"", "").replace("\")", ""),
                        "size_mb": size_t
                    })
                    global total_dl_size
                    total_dl_size = total_dl_size + size_t
                    try:
                        progressBar.set(len(dl_links) / len(all_links))
                        links_obtained.set(f"{len(dl_links)} / {len(all_links)}")
                    except:
                        pass
            time.sleep(0.5)

        if not dl_links:
            time.sleep(3)
            showErrorPopup(caller, "Error: No supported links are found!")
            return

        if len(dl_links) != len(all_links):
            dl_links.clear()
            return
        
        verifyAllDownloadedFiles(dl_links)
        
        time.sleep(1.5)
        caller.destroy()
        root.event_generate('<<ThreadFinished>>')
    except Exception as e:
        print(f"Error message: {repr(e)}")
        time.sleep(3)
        showErrorPopup(caller, f"{repr(e)[:35]}")
        

def showErrorPopup(caller,message):
    if caller is not None:
        caller.destroy()
    notification = customtkinter.CTkToplevel(app)
    x = app.winfo_x()
    y = app.winfo_y()
    notification.geometry('%dx%d+%d+%d' % (350, 135, x+170, y+98))
    notification.resizable(0,0)
    notification.after(250, lambda: notification.iconbitmap(ERROR_ICON))
    notification.title("")

    loading_URL = customtkinter.CTkLabel(notification, text=message, fg_color="transparent",font=(FONT_STYLE,SUB_FONT_SIZE), justify="center", wraplength=300)
    loading_URL.pack(pady=(25,0))
    button_back = customtkinter.CTkButton(notification, text="BACK", command=(lambda: notification.destroy()), width=156, height=42, font=(BUTTON_FONT_STYLE,MAIN_FONT_SIZE))
    button_back.pack(pady=(20,0))

    notification.transient(master=app)
    notification.grab_set()

def showLoadingforGettingLinks():
    global toplevel
    toplevel = customtkinter.CTkToplevel(app)
    x = app.winfo_x()
    y = app.winfo_y()
    toplevel.geometry('%dx%d+%d+%d' % (480, 126, x+107, y+98))
    toplevel.resizable(0,0)
    toplevel.after(250, lambda: toplevel.iconbitmap(LOADING_ICON))
    toplevel.title("")
    links_obtained.set("")
    loading_URL = customtkinter.CTkLabel(toplevel, text="Getting all direct links...", fg_color="transparent",font=(FONT_STYLE,SUB_FONT_SIZE))
    loading_URL.grid(row=0,column=0,sticky="W",padx=(28,0), pady=(25,2))
    progressbar = customtkinter.CTkProgressBar(toplevel, orientation="horizontal", width=423, height=23, corner_radius=0, mode="indeterminate")
    progressbar.grid(row=1,column=0,sticky="W",padx=(28,0), pady=(2,0))
    label_count = customtkinter.CTkLabel(toplevel, textvariable=links_obtained, fg_color="transparent",font=(FONT_STYLE,MINI_FONT_SIZE))
    label_count.grid(row=2,column=0,sticky="E",padx=(0,0), pady=(1,0))

    progressbar.start()

    toplevel.protocol("WM_DELETE_WINDOW", onClosePrompt)
    toplevel.transient(master=app)
    toplevel.grab_set()

    linksThread = Thread(target = getAllLinks, args=[progressbar, toplevel, app], daemon=True)
    linksThread.start()
    
def onBrowse():
    app.focus()
    save_directory.set(askdirectory(title='Select save directory'))

def onProceed():
    url = game_url.get()
    directory = save_directory.get()

    if url == "" or directory == "":
        showErrorPopup(None, "No URL and save directory selected!")
    else:
        showLoadingforGettingLinks()

def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)

def invokeDownloadPage():
    app.destroy()
    global dlPage
    dlPage = customtkinter.CTk()
    dlPage.geometry(f"{DLPAGE_WIDTH}x{DLPAGE_HEIGHT}")
    dlPage.resizable(0,0)
    dlPage.title(f"{NAME} {VERSION}")
    dlPage.iconbitmap(APP_ICON)

    dlPage.rowconfigure(index=1,weight=1)

    label_1 = customtkinter.CTkLabel(dlPage, text=game_name[:108], fg_color="transparent",font=(BUTTON_FONT_STYLE,SUB_FONT_SIZE))
    label_1.grid(row=0,column=0, columnspan=3,sticky="W", padx=(28,0), pady=(24,2))

    label_2 = customtkinter.CTkLabel(dlPage, text=game_info[:330], fg_color="transparent",font=(FONT_STYLE,SUB_FONT_SIZE),wraplength=210, justify="left")
    label_2.grid(row=1,column=0, sticky="NW", padx=(28,0), pady=(15, 0))

    label_sd = customtkinter.CTkLabel(dlPage, text=f"Saving to: {save_directory.get()}", fg_color="transparent",font=(FONT_STYLE,SUB_FONT_SIZE),wraplength=210, justify="left")
    label_sd.grid(row=1,column=0, sticky="SW", padx=(28,0))

    scrollable_frame = customtkinter.CTkScrollableFrame(dlPage, width=610, height=326, label_font=(FONT_STYLE,SUB_FONT_SIZE), label_text="Select files to download")
    scrollable_frame.columnconfigure(index=0,weight=1)
    scrollable_frame.grid(row=1, column=1, columnspan=2, padx=(28,0), pady=(15, 0))

    progressbar = customtkinter.CTkProgressBar(dlPage, orientation="horizontal", width=636, height=23, corner_radius=0, mode="determinate")
    progressbar.grid(row=3,column=0, columnspan=2, sticky="W",padx=(28,0), pady=(30,0))
    progressbar.set(0)
    second_screen_widgets.append(progressbar)

    label_4 = customtkinter.CTkLabel(dlPage, text=f"No ongoing downloads", fg_color="transparent",font=(FONT_STYLE,SUB_FONT_SIZE),wraplength=400, justify="left")
    label_4.grid(row=4,column=0,columnspan=2,rowspan=2, sticky="NW", padx=(28,0), pady=(5, 0))
    second_screen_widgets.append(label_4)

    label_6 = customtkinter.CTkLabel(dlPage, text="", fg_color="transparent",font=(FONT_STYLE,SUB_FONT_SIZE))
    label_6.grid(row=4,column=1, sticky="E", padx=(28,0), pady=(5, 0))

    label_7 = customtkinter.CTkLabel(dlPage, text="", fg_color="transparent",font=(FONT_STYLE,SUB_FONT_SIZE))
    label_7.grid(row=5,column=1, sticky="E", padx=(28,0), pady=(0, 16))
    second_screen_widgets.append(label_7)
    second_screen_widgets.append(label_6)

    button_proceed = customtkinter.CTkButton(dlPage, text="START DOWNLOAD", command=onStartDwonload, width=241, height=42, font=(BUTTON_FONT_STYLE,MAIN_FONT_SIZE), fg_color="#2E5077", hover_color="#233D5B")
    button_proceed.grid(row=3, column=2, rowspan=3, sticky="E", pady=(30,0), padx=(28,0))
    second_screen_widgets.append(button_proceed)
    
    downloaded_size = float(0.0)
    path_t = save_directory.get()
    color = "#707070"
    for index, dl_link in enumerate(dl_links):
        # text = f"{getLocalFileSize(f"{path_t}/{dl_link["file_name"]}")} / {dl_link["size_mb"]} MB"      
        if index in remaining_dl_index:
            state = tkinter.DISABLED
            text = "COMPLETED"
            color = "#4DA1A9"
            downloaded_size = downloaded_size + dl_link["size_mb"]
            value = "off"
        else:
            state = tkinter.NORMAL
            value = "on"
            if os.path.isfile(f"{path_t}/{dl_link["file_name"]}"):
                text = "CORRUPTED"
                color = "#EC5E5E"
            else:
                text = f"{dl_link["size_mb"]} MB"
                color = "#707070"

        check_var_t = customtkinter.StringVar(dlPage,value=value)
        checkbox_t = customtkinter.CTkCheckBox(scrollable_frame, text=dl_link["file_name"][:85],variable=check_var_t, onvalue="on", offvalue="off",font=(FONT_STYLE,MINI_FONT_SIZE), checkbox_width=16, checkbox_height=16,state=state)
        checkbox_t.grid(row=index, column=0,sticky="W",padx=(2,0), pady=(2, 0))
        label_t = customtkinter.CTkLabel(scrollable_frame, text=text, fg_color="transparent",font=(FONT_STYLE,MINI_FONT_SIZE),text_color=color)
        label_t.grid(row=index, column=1, sticky="E",padx=(0,2), pady=(2, 0))
        
        checkbox_var_list.append(check_var_t)
        dl_label_list.append(label_t)
        checkbox_widget_list.append(checkbox_t)

    label_3 = customtkinter.CTkLabel(dlPage, text=f"Free Space: {getFreeDiscSpace()} | Downloaded: {downloaded_size} MB / {round(total_dl_size,2)} MB ({len(remaining_dl_index)}/{len(dl_links)})", fg_color="transparent",font=(FONT_STYLE,MINI_FONT_SIZE))
    label_3.grid(row=2,column=1, columnspan=2, sticky="E", padx=(0,0), pady=(2, 0))
    second_screen_widgets.append(label_3)

    button_toggle = customtkinter.CTkButton(dlPage, text=" Toggle all ", command=onToggleButtonClick, width=80, height=25, font=(BUTTON_FONT_STYLE,MINI_FONT_SIZE))
    button_toggle.grid(row=2, column=1,sticky="W",padx=(28,0), pady=(2, 0))
    second_screen_widgets.append(button_toggle)

    button_refresh = customtkinter.CTkButton(dlPage, text=" Refresh list ", command=onRefreshClick, width=80, height=25, font=(BUTTON_FONT_STYLE,MINI_FONT_SIZE))
    button_refresh.grid(row=2, column=1,sticky="W",padx=(120,0), pady=(2, 0))
    second_screen_widgets.append(button_refresh)    

    dlPage.bind('<<DownloadFinished>>',onOneDownloadFinish)
    dlPage.bind('<<AllDownloadFinished>>',onAllDownloadFinish)

    dlPage.mainloop()

def main():
    app.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
    app.resizable(0,0)
    app.title(f"{NAME} {VERSION}")
    app.iconbitmap(APP_ICON)

    entry_URL = customtkinter.CTkEntry(app,textvariable=game_url, placeholder_text="Enter or Paste the URL", width=612, height=42,font=(FONT_STYLE,MAIN_FONT_SIZE))
    entry_URL.grid(row=0,column=0,padx=(41,41), pady=(30,2))
    label_URL = customtkinter.CTkLabel(app, text="Enter the link of the main page of the game", fg_color="transparent",font=(FONT_STYLE,SUB_FONT_SIZE))
    label_URL.grid(row=1,column=0,sticky = "W", padx=(41,0), pady=(0,30))

    entry_directory = customtkinter.CTkEntry(app, width=447, textvariable=save_directory, height=42,font=(FONT_STYLE,MAIN_FONT_SIZE),state="disabled")
    entry_directory.grid(row=2,column=0,sticky = "W", padx=(41,0), pady=(0,2))
    label_directory = customtkinter.CTkLabel(app, text="The directory where the downloads will be saved", fg_color="transparent",font=(FONT_STYLE,SUB_FONT_SIZE))
    label_directory.grid(row=3,column=0,sticky = "W", padx=(41,0), pady=(0,30))
    button_browse = customtkinter.CTkButton(app, text="BROWSE", command=onBrowse, width=156, height=42, font=(BUTTON_FONT_STYLE,MAIN_FONT_SIZE))
    button_browse.grid(row=2, column=0, sticky = "E", padx=(0,41), pady=(0,2))

    optionmenu = customtkinter.CTkOptionMenu(app, values=FILE_HOSTERS,command=optionmenu_callback, width=178, height=33, font=(FONT_STYLE,SUB_FONT_SIZE))
    optionmenu.set(FILE_HOSTERS[0])
    optionmenu.grid(row=4, column=0, sticky = "W", padx=(41,0))
    button_proceed = customtkinter.CTkButton(app, text="PROCEED", command=onProceed, width=156, height=42, font=(BUTTON_FONT_STYLE,MAIN_FONT_SIZE), fg_color="#2E5077", hover_color="#233D5B")
    button_proceed.grid(row=4, column=0, sticky = "E", padx=(0,41))

    app.bind('<<ThreadFinished>>',onOtainedAllLinksComplete)

    app.mainloop()

main()
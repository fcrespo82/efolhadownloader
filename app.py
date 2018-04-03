#!.venv/bin/python
#coding: utf-8

'GUI for efolhadownloader'

import tkinter as tk
import tkinter.ttk as ttk
from threading import Thread
from download import download


class App(tk.Frame):
    'GUI for efolhadownloader'

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand=True)
        self.create_widgets()

    def create_widgets(self):
        'Create interface widgets'
        self.download = ttk.Button(self, text="Download dos demonstrativos",
                                   command=self.button_command)
        self.download.pack(side="top")
        self.progress = ttk.Progressbar(
            self, orient='horizontal', mode='indeterminate')
        self.progress.pack(side="top")
        self.quit = ttk.Button(self, text="QUIT",
                               command=self.master.destroy)
        self.quit.pack(side="bottom")

    def button_command(self):
        'Download files'
        self.progress.start(20)
        thread = Thread(target=download)
        thread.start()
        self.master.after(50, self.check_download, thread)

    def check_download(self, thread):
        'Check if download have finished'
        if thread.is_alive():
            # self.progress.step(1)
            self.master.after(50, self.check_download, thread)
        else:
            self.progress.stop()


def main():
    'Main function'
    root = tk.Tk()
    app = App(root)
    app.mainloop()


if __name__ == '__main__':
    main()

import os
import tkinter as tk
from pnadcontinua.gui.frames import (
    HomeFrame, MicrodataFrame, AggregationsFrame, TutorialFrame, VariablesFrame
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.window_size = 530

        self.title("PNAD Contínua")

        x_position = int((self.screen_width - self.window_size) / 2)
        y_position = int((self.screen_height - self.window_size) / 2)

        self.geometry(f"{self.window_size}x{self.window_size}+{x_position}+{y_position}")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))

        # Creation of the frames
        self.home_frame = HomeFrame(self)
        self.microdata_frame = MicrodataFrame(self)
        self.aggregations_frame = AggregationsFrame(self)
        self.variables_frame = VariablesFrame(self)
        self.tutorial_frame = TutorialFrame(self)

        # Place the frames on the window
        self.home_frame.grid(row=0, column=0, sticky="nsew")
        self.microdata_frame.grid(row=0, column=0, sticky="nsew")
        self.aggregations_frame.grid(row=0, column=0, sticky="nsew")
        self.variables_frame.grid(row=0, column=0, sticky="nsew")
        self.tutorial_frame.grid(row=0, column=0, sticky="nsew")
        # Display the home frame
        self.show_frame(self.home_frame)

    def show_frame(self, frame):
        frame.tkraise()


def main():
    app = App()
    app.mainloop()

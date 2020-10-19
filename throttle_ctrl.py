import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import sys
import json
import os

import pygame
from SimConnect import *
import numpy as np
import matplotlib.pyplot as plt

from ToolTip import CreateToolTip, ToolTip

sm = SimConnect()
aq = AircraftRequests(sm, _time = 0)
ae = AircraftEvents(sm)


class AxisSlider(ttk.Frame):
    def __init__(self, master, index):
        super().__init__(master, border = 2, relief = tk.RAISED)
        self._index = index
        self.label = ttk.Label(self, text = f"Axis modifier {index}", font = ("Helvetica", 11, "bold"))
        self.label.grid(row = 0, column = 0) # Main

        self._frm_select_simaxis = ttk.Frame(self)
        self._frm_select_simaxis.grid(row = 1, column = 0, sticky = "w") # Main

        self._label_simaxis = ttk.Label(self._frm_select_simaxis, text = "Simulator throttle axis:")
        self._label_simaxis.grid(row = 0, column = 0, sticky = "w")

        self._frm_simaxis_choices = ttk.Frame(self._frm_select_simaxis,
                                              border = 2, relief = tk.RAISED)
        self._simaxis_choices = {0, 1, 2, 3, 4, 5, 6}
        self.dropvar = tk.IntVar(self, value = 1)
        self._simaxis_dropdown = ttk.OptionMenu(self._frm_simaxis_choices,
                                                self.dropvar,
                                                *self._simaxis_choices)
        self._frm_simaxis_choices.grid(row = 0, column = 2,
                                       padx = 5, pady = 5,
                                       sticky = "w")
        self._simaxis_dropdown.pack(anchor = "w")

        self._btn_update_throttle_pos = ttk.Button(self._frm_select_simaxis,
                                                   text = "Get current throttle position",
                                                   command = self.update_value)
        self._btn_update_throttle_pos.grid(row = 0, column = 3, padx = 5)

        self._frm_throttle_bar = ttk.Frame(self)
        self._frm_throttle_bar.grid(row = 2, column = 0, sticky = "w") # Main
        self._sim_throttle_bar = ttk.Progressbar(self._frm_throttle_bar,
                                                 orient = tk.HORIZONTAL,
                                                 length = 200,
                                                 mode = "determinate")
        self._sim_throttle_bar.grid(row = 0, column = 0, sticky = "w")
        self._sim_throttle_value = 0
        self._lbl_sim_throttle = ttk.Label(self._frm_throttle_bar, text = "00.00%", width = 10)
        self._lbl_sim_throttle.grid(row = 0, column = 1, padx = 5, sticky = "w")


        self._frm_select_joyaxis = ttk.Frame(self)
        self._frm_select_joyaxis.grid(row = 3, column = 0, sticky = "sw") # Main
        self.rowconfigure(3, minsize = 42)

        self._label_joyaxis = ttk.Label(self._frm_select_joyaxis, text = "Joystick axis:")
        self._label_joyaxis.grid(row = 0, column = 0, sticky = "w")

        self.reverse = tk.IntVar(self, 1)
        self._checkbutton_reverse = ttk.Checkbutton(self._frm_select_joyaxis,
                                                    text = "Invert axis",
                                                    variable = self.reverse)
        self._checkbutton_reverse.grid(row = 0, column = 2, padx = 5, sticky = "w")

        self.sameaxis_reverser = tk.IntVar(self, 0)
        self._checkbutton_reverser = ttk.Checkbutton(self._frm_select_joyaxis,
                                                     text = "Reverser on same axis",
                                                     variable = self.sameaxis_reverser)
        self._checkbutton_reverser.grid(row = 0, column = 3, sticky = "w")

        self._btn_mrev = ttk.Button(self._frm_select_joyaxis,
                                    text = "Set max rev.",
                                    command = self.set_max_rev)
        self._btn_mrev.grid(row = 0, column = 4, sticky = "w", padx = 5)

        self._frm_joystick_choices = ttk.Frame(self._frm_select_joyaxis,
                                               border = 2, relief = tk.RAISED)
        self._joyaxis_choices = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}
        self.dropvar_joy = tk.IntVar(self, value = 1)
        self._joyaxis_dropdown = ttk.OptionMenu(self._frm_joystick_choices,
                                                self.dropvar_joy,
                                                *self._joyaxis_choices)
        self._frm_joystick_choices.grid(row = 0, column = 1,
                                        padx = 5, pady = 5,
                                        sticky = "w")
        self._joyaxis_dropdown.pack(anchor = "w")

        self._frm_axis_bar = ttk.Frame(self)
        self._frm_axis_bar.grid(row = 4, column = 0, sticky = "w") # Main
        self._joy_axis_bar = ttk.Progressbar(self._frm_axis_bar,
                                             orient = tk.HORIZONTAL,
                                             length = 200,
                                             mode = "determinate")
        self._joy_axis_bar.grid(row = 0, column = 0)
        self._lbl_axis_pos = ttk.Label(self._frm_axis_bar, text = "Raw: ", width = 10)
        self._lbl_axis_pos.grid(row = 0, column = 1, padx = 5, sticky = "w")

        self._frm_calibrate_btns = ttk.Frame(self)
        self._frm_calibrate_btns.grid(row = 5, column = 0, pady = 3, sticky = "w") # Main

        self._btn_idle = ttk.Button(self._frm_calibrate_btns,
                                    text = "Set idle",
                                    command = self.set_idle)
        self._btn_idle.grid(row = 0, column = 0)
        CreateToolTip(self._btn_idle,
                      "Set the position for the idle detent on your joystick")

        self._btn_clmb = ttk.Button(self._frm_calibrate_btns,
                                    text = "Set climb",
                                    command = self.set_climb)
        self._btn_clmb.grid(row = 0, column = 1)
        CreateToolTip(self._btn_clmb,
                      "Set the position for the climb detent on your joystick")

        self._btn_flex = ttk.Button(self._frm_calibrate_btns,
                                    text = "Set flex/MCT",
                                    command = self.set_flex)
        self._btn_flex.grid(row = 0, column = 2)
        CreateToolTip(self._btn_flex,
                      "Set the position for the Flex/MCT detent on your joystick")

        self._btn_toga = ttk.Button(self._frm_calibrate_btns,
                                    text = "Set TO/GA",
                                    command = self.set_toga)
        self._btn_toga.grid(row = 0, column = 3)
        CreateToolTip(self._btn_toga,
                      "Set the position for the TO/GA detent on your joystick")

        self._bth_plot = ttk.Button(self._frm_calibrate_btns,
                                    text = "Plot graph",
                                    command = self.plot_throttle)
        self._bth_plot.grid(row = 0, column = 4)

        self._sim_detents = {"max_reverse": -20, "idle": 0, "climb": 89, "flex": 95, "toga": 100}
        self._detents = {"max_reverse": -2, "idle": -1, "climb": 0.78, "flex": 0.9, "toga": 1}
        self._raw = 0
        self._output = 0

    def set_idle(self):
        self._detents["idle"] = self._raw

    def set_climb(self):
        self._detents["climb"] = self._raw

    def set_flex(self):
        self._detents["flex"] = self._raw

    def set_toga(self):
        self._detents["toga"] = self._raw

    def set_max_rev(self):
        self._detents["max_reverse"] = self._raw

    def load_settings(self,
                      detents_dict,
                      sim_detents_dict,
                      reverse,
                      sameaxis_reverser,
                      selected_simaxis,
                      selected_joyaxis):
        self._detents = detents_dict
        self._sim_detents = sim_detents_dict
        self.reverse.set(reverse)
        self.sameaxis_reverser.set(sameaxis_reverser)
        self.dropvar.set(selected_simaxis)
        self.dropvar_joy.set(selected_joyaxis)

    def get_settings(self):
        return [self._detents,
                self._sim_detents,
                self.reverse.get(),
                self.sameaxis_reverser.get(),
                self.dropvar.get(),
                self.dropvar_joy.get()]

    def update_value(self):
        value = aq.get(self.throttle_simvar)
        if value != -999999:
            self._sim_throttle_value = value
            self._sim_throttle_bar["value"] = value
            self._lbl_sim_throttle["text"] = f"{value:5.2f}%"

    def update_joyaxis(self, val):
        self._lbl_axis_pos["text"] = f"Raw: {val:5.2f}"
        if self.reverse.get():
            val = -val
        self._raw = val

        val = self.get_out_throttle(val)
        self._joy_axis_bar["value"] = val

    def set_sim_throttle(self, throttle = None):
        index = int(self.dropvar.get())
        if throttle is None:
            throttle = float(self._joy_axis_bar["value"])

        aq.set(f"GENERAL_ENG_THROTTLE_LEVER_POSITION:{index}", throttle)

    def get_out_throttle(self, val):
        mrev = self._detents["max_reverse"]
        idle = self._detents["idle"]
        clmb = self._detents["climb"]
        flex = self._detents["flex"]
        toga = self._detents["toga"]

        revr_val = min(max(1 - (val - mrev)/(idle - mrev), 0), 1)
        clmb_val = min(max((val - idle)/(clmb - idle), 0), 1)
        flex_val = min(max((val - clmb)/(flex - clmb), 0), 1)
        toga_val = min(max((val - flex)/(toga - flex), 0), 1)

        sim_revr = self._sim_detents["max_reverse"]
        sim_clmb = self._sim_detents["climb"]
        sim_flex = self._sim_detents["flex"]
        sim_toga = self._sim_detents["toga"]

        revr_contrib = revr_val*sim_revr
        clmb_contrib = clmb_val*sim_clmb
        flex_contrib = flex_val*(sim_flex - sim_clmb)
        toga_contrib = toga_val*(sim_toga - sim_flex)

        total = (clmb_contrib + flex_contrib + toga_contrib)
        if self.sameaxis_reverser.get():
            total += revr_contrib

        return total

    @property
    def throttle_simvar(self):
        index = int(self.dropvar.get())
        return f"GENERAL_ENG_THROTTLE_LEVER_POSITION:{index}"

    def plot_throttle(self):
        idle = self._detents["idle"]
        toga = self._detents["toga"]

        targets = np.linspace(idle, toga, 1000)
        thrust = []

        for target in targets:
            thrust.append(self.get_out_throttle(target))
        
        plt.plot(targets, thrust)
        plt.xlabel("Joystick in")
        plt.ylabel("Simulator throttle/thrust")
        plt.show()


class Window:
    def __init__(self):
        pygame.init()
        self.root = tk.Tk()
        self.root.title("SC Throttle Config")
        self.root.iconbitmap(os.path.join(os.getcwd(), "icon.ico"))
        self.axes = []
        self.running = False
        frm_top_buttons = ttk.Frame(self.root)
        frm_top_buttons.pack(padx = 2, pady = 2)
        btn_add_axis = ttk.Button(frm_top_buttons, text = "Add new axis", width = 20,
                                  command = self.add_new_axis)
        btn_add_axis.grid(row = 0, column = 0, padx = 2)

        self.btn_run = ttk.Button(frm_top_buttons, text = "Activate", width = 10,
                                  command = self.toggle_running)
        self.btn_run.grid(row = 0, column = 1)

        self.btn_run = ttk.Button(frm_top_buttons, text = "Save settings", width = 20,
                                  command = self.save_settings)
        self.btn_run.grid(row = 0, column = 3)

        if(pygame.joystick.get_count() < 1):
            print("Please connect a joystick.")
            sys.exit()
        else:
            joy0 = pygame.joystick.Joystick(0)
            joy0.init()

        self.load_settings()

        self.root.after(5, self.after_loop)
        self.root.mainloop()

    def toggle_running(self):
        if self.running:
            self.running = False
            self.btn_run["text"] = "Activate"
        else:
            self.running = True
            self.btn_run["text"] = "Stop"

    def add_new_axis(self):
        new_axis = AxisSlider(self.root, len(self.axes) + 1)
        new_axis.pack(padx = 2, pady = 2)

        self.axes.append(new_axis)

        ideal_height = len(self.axes)*184 + 29
        ideal_width = 442

        self.root.minsize(ideal_width, ideal_height)
        self.root.maxsize(ideal_width, ideal_height)

    def save_settings(self):
        settings_list = []

        for axis in self.axes:
            settings_list.append(axis.get_settings())
        
        with open(os.path.join(os.getcwd(), "settings.json"), "w") as outfile:
            json.dump(settings_list, outfile, indent = 2)

    def load_settings(self):
        path = os.path.join(os.getcwd(), "settings.json")
        if not os.path.isfile(path):
            return
        
        with open(path, "r") as infile:
            settings_list = json.load(infile)

        for item in settings_list:
            self.add_new_axis()
            self.axes[-1].load_settings(item[0], item[1], item[2],
                                        item[3], item[4], item[5])

    def after_loop(self):
        events = pygame.event.get()
        for event in events:
            if hasattr(event, "axis"):
                for axis in self.axes:
                    if event.axis == int(axis.dropvar_joy.get() - 1):
                        axis.update_joyaxis(event.value)
                        if self.running:
                            axis.set_sim_throttle()    

        self.root.after(5, self.after_loop)


if __name__ == "__main__":
    window = Window()
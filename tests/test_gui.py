import unittest
import os
import shutil
from Qcircuits.src._gui import GuiWindow
import inspect
import tkinter as tk

class GuiTestingHandler(unittest.TestCase):

    def close_gui(self):
        while True:
            try:
                self.gui.master.destroy()
            except tk.TclError:
                # The gui is no longer open
                return

    

class ManualTesting(GuiTestingHandler):

    def get_netlist_filename(self):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        calling_function_name = calframe[2][3]
        filename = os.path.join(\
            os.path.dirname(__file__),\
            ".gui_testing_files",\
            calling_function_name+\
            "_netlist.txt")
        return filename

    def write_netlist_file(self,contents):
        filename = self.get_netlist_filename()
        with open(filename,'w') as netlist_file:
            netlist_file.write(contents)
        return filename

    def read_netlist_file(self):
        with open(self.get_netlist_filename(),'r') as netlist_file:
            contents = netlist_file.read()
        return contents


class AutomaticTesting(GuiTestingHandler):

    def launch_gui_testing(self,exclude = None, force_build = False):
        self.set_folder_name()
        self.set_file_names()
        self.exclude = exclude
        self.force_build = force_build

        if not self.already_built():
            self.gui_build_test()

        self.run_events()

        with open(self.final_expected,'r') as f:
            final_expected = f.read()
        with open(self.final_after_events,'r') as f:
            final_after_events = f.read()
            
        self.assertEqual(final_expected,final_after_events)

    def set_file_names(self):
        self.init = os.path.join(self.folder,'initial_netlist.txt')
        self.events = os.path.join(self.folder,'events.txt')
        self.final_expected = os.path.join(self.folder,'final_netlist.txt')
        self.final_after_events = os.path.join(self.folder,'final_after_events_netlist.txt')

    def set_folder_name(self):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        calling_function_name = calframe[2][3]
                
        self.folder = os.path.join(\
            os.path.dirname(__file__),\
            ".gui_testing_files",\
            calling_function_name)

    def run_events(self):

        shutil.copyfile(self.init,self.final_after_events)
        self.gui = GuiWindow(self.final_after_events, _unittesting = True)
        with open(self.events,'r') as f:
            lines = f.readlines()
            for l in lines:
                self.gui.canvas.focus_force()
                exec('self.gui.canvas.event_generate('+l+')', globals(), locals())
        self.close_gui()

    def gui_build_test(self):

        print("Build initial circuit")
        GuiWindow(self.init)
        shutil.copyfile(self.init,self.final_expected)
        print("Build final circuit")
        GuiWindow(self.final_expected, _track_events_to = self.events)

        self.remove_exluded_events()

    def remove_exluded_events(self):
        if self.exclude is not None:
            temp = os.path.join(folder,'temp.txt')
            shutil.copyfile(self.events,temp)
            with open(self.events,'w') as to_write:
                with open(temp,'r') as to_read:
                    lines = to_read.readlines()
                    for l in lines:
                        wr = True
                        for e in exclude:
                            if e in l:
                                wr = False
                        if wr:
                            to_write.write(l)
            os.remove(temp)

    def already_built(self):
        try:
            os.mkdir(self.folder)
            return False
        except FileExistsError:
            pass
        
        for filename in [self.init,self.final_expected,self.events]:
            try:
                with open(filename,'r'):
                    pass
            except FileNotFoundError:
                return False 

        if self.force_build:
            for filename in [self.init,self.final_expected,self.events,self.final_after_events]:
                try:
                    os.remove(filename)
                except FileNotFoundError:
                    pass 
            return False
            
        return True


class TestOpening(ManualTesting):

    def test_if_opening_blank_test_throws_error(self):
        filename = self.write_netlist_file('')
        self.gui = GuiWindow(filename, _unittesting = True)
        self.close_gui()
        self.assertEqual('',self.read_netlist_file())

class TestMovingComponentsAround(AutomaticTesting):

    def test_moving_capacitor_horizontally(self):
        self.launch_gui_testing()

    def test_rotating_capacitor(self):
        self.launch_gui_testing()

    def test_rotating_ground(self):
        self.launch_gui_testing()


    def test_moving_capacitor_twice(self):
        self.launch_gui_testing()

    def test_moving_parallel_RLCJG(self):
        self.launch_gui_testing()

if __name__ == "__main__":
    unittest.main()
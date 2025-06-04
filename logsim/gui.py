"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        # initialise simulation variables
        self.devices = devices
        self.monitors = monitors

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a all trace signals
        j = 0
        for key in self.monitors.monitors_dictionary:
            trace = self.monitors.monitors_dictionary[key]
            GL.glColor3f(0.0, 0.0, 1.0)
            GL.glBegin(GL.GL_LINE_STRIP)
            for i in range(len(trace)):
                x = (i*20) + 10
                x_next = ((i+1)*20) + 10
                y = int(trace[i])
                if y % 2 == 0:
                    y = 75 + j * 50
                else:
                    y = 100 + j * 50
                GL.glVertex2f(x, y)
                GL.glVertex2f(x_next, y)
            GL.glEnd()
            j += 1
        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()



    def on_paint(self, event):

        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))



class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_HELP_COMMANDS, 'Help')
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&Menu")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.output_text = wx.StaticText(self, wx.ID_ANY, "",style=wx.TE_READONLY| wx.TE_MULTILINE)
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)
        
        #Initial simulation variables
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network
        self.cycles_completed = 0 
        self.cycles = 0

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        # add text under the run button
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        side_sizer.Add(self.text_box, 1, wx.ALL, 5)
        side_sizer.Add(self.output_text, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_HELP_COMMANDS:
            self.display_help()

        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Team 1\n2025",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        spin_value = self.spin.GetValue()
        self.run_command(str(spin_value))

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text = self.text_box.GetValue().split()

        if len(text) == 0:
            self.empty_input()
        elif len(text) == 1:
            if text[0] == "h":
                self.help_command()
            elif text[0] == "q":
                self.Close(True)
            else:
                self.invalid_command()
        elif len(text) == 2:
            if text[0] == "m":
                self.monitor_command(text[1])
            elif text[0] == "z":
                self.zap_command(text[1])
            elif text[0] == "r":
                self.run_command(text[1])
            elif text[0] == "c":
                self.continue_command(text[1])
            else:
                self.invalid_command()    
        elif len(text) == 3:
            if text[0] == "s":
                self.switch_command(text[1], text[2])
            else:
                self.invalid_command()
        else:
            self.invalid_command()




    def help_command(self):
        """Display the help text in a message box."""
        with open("Help.txt", "r") as file:
            help_text = file.read()
        self.output_text.SetLabel("")
        wx.MessageBox(help_text, "Help", wx.ICON_INFORMATION | wx.OK)

    def monitor_command(self, text):
        """Set the specified monitor."""
        monitor = self.read_signal_name(text)
        print(monitor)
        if monitor is None:
            self.invalid_device_id()
            return
        else:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                self.successful_command()
            else:
                self.unsuccessful_command()
        self.run_command(str(self.cycles))
    

    def zap_command(self, text):
        """Remove the specified monitor."""
        monitor = self.read_signal_name(text)
        if monitor is None:
            self.invalid_device_id()
        else:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                self.successful_command()
            else:
                self.unsuccessful_command()
        self.run_command(str(self.cycles))
    
    def run_command(self, N):
        """Run the simulation from scratch."""
        if not(N.isdigit()):
            self.invalid_cycles()
            return
        N = int(N)
        self.cycles = N
        self.cycles_completed = 0 
        self.monitors.reset_monitors()
        self.devices.cold_startup()
        if self.run_network(N):
                self.cycles_completed += N
    
    def run_network(self, N):
        """Run the network for N cycles and draw the signal traces.

        Return True if succesful.
        """

        for _ in range(N):
            if self.network.execute_network():
                self.monitors.record_signals()
        monitors_dictionary = self.monitors.monitors_dictionary
        trace_count = len(monitors_dictionary)
        trace_length = len(next(iter(monitors_dictionary.values()), []))
        print(monitors_dictionary)
        self.canvas.render('')
        self.successful_command()
        return True


    def continue_command(self, N):
        """Continue the simulation for N more cycles."""
        if not(N.isdigit()):
            self.invalid_cycles()
            return
        N = int(N)
        self.cycles += N
        if self.run_network(N):
            self.cycles_completed += N

    def switch_command(self, device, new_value):
        """Set the specified switch to the specified signal level."""
        switch_id = self.read_name(device)
        if switch_id is not None:
            if new_value == "0" or new_value == "1":
                switch_state = int(new_value)
                if self.devices.set_switch(switch_id, switch_state):
                    self.successful_command()
                    return 
        self.unsuccessful_command()







 

    def read_name(self, text):
        """Return the name ID of the current string if valid.

        Return None if the current string is not a valid name string.
        """
        name_string = text.split(".")[0] 
        if name_string is None :
            self.invalid_device_id()
            return None
        elif not(name_string[0].isalpha()):
            self.invalid_device_id()
            return None
        else:
            name_id = self.names.query(name_string)
        if name_id is None:
            self.invalid_device_id()
            return None
        return name_id

    def read_signal_name(self,text):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        name_string = text.split(".")
        name_id = self.read_name(text) # Already checked for validity
        if name_id is None:
            return None
        if len(name_string) == 1:
            return [name_id, None]
        if len(name_string) != 2:
            self.invalid_device_id()
            return None
        port_id = name_string[1]
        if port_id is None:
            self.invalid_port_id()
            return
        return [name_id, port_id]

    def read_value(self, text):
        """Return the value of the current signal.

        Return None if the value is invalid.
        """
        if text.isdigit():
            return int(text)
        elif text.lower() in ["true", "false"]:
            return text.lower() == "true"
        else:
            self.invalid_value()
            return None









    def invalid_command(self):
        """Display an error message for invalid input."""
        self.output_text.SetLabel("Invalid command. Enter 'h' for help.")

    def invalid_cycles(self):
        """Display an error message for invalid cycle input."""
        self.output_text.SetLabel("Number of cycles must be an integer. Enter 'h' for help.")

    def invalid_device_id(self):
        """Display an error message for invalid device ID."""
        self.output_text.SetLabel("Invalid device ID. Enter 'h' for help.")
    
    def invalid_port_id(self):
        """Display an error message for invalid port ID."""
        self.output_text.SetLabel("Invalid port ID. Enter 'h' for help.")

    def invalid_value(self):
        """Display an error message for invalid value."""
        self.output_text.SetLabel("Invalid value. Enter 'h' for help.")
    
    def empty_input(self):
        """Display an error message for empty input."""
        self.output_text.SetLabel("No command entered. Enter 'h' for help.")

    def successful_command(self):
        """Display a success message."""
        self.output_text.SetLabel("Command executed successfully.")
    
    def unsuccessful_command(self):
        """Display an error message for unsuccessful command."""
        self.output_text.SetLabel("Command execution failed. Enter 'h' for help.")

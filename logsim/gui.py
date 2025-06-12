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
import gettext
from functools import partial
from wx.lib.scrolledpanel import ScrolledPanel

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

    def __init__(self, parent, devices, monitors, names, h_scroll  = None, v_scroll = None):
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
        self.names = names
        self.devices = devices
        self.monitors = monitors

        self.h_scroll = h_scroll
        self.v_scroll = v_scroll

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetVirtualSize((800, 600))  # initial virtual size


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

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x,self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)
        GL.glMatrixMode(GL.GL_MODELVIEW)

        size = self.GetClientSize()
        width = size.width
        height = size.height
      
        padding_x = 50
        padding_y = 30
        num_signals = len(self.monitors.monitors_dictionary)
        trace_length = max((len(v) for v in self.monitors.monitors_dictionary.values()), default=1)
        avg_height = int((height - 2*padding_y) / num_signals)
        signal_height = max(avg_height, 60)
        x_step = 80 #int((width - 2*padding_x) / max(trace_length, 1)) if trace_length <= 30 else 80
        trace_width = padding_x * 2 + trace_length * x_step
        trace_height = padding_y * 2 + num_signals * signal_height
        scroll_x_range = max(trace_width, width)
        scroll_y_range = max(trace_height, height)


        min_pan_y = min(0, height - trace_height)
        self.pan_y = max(min_pan_y, min(0, self.pan_y))

        parent = self.GetParent()
        if hasattr(parent, 'h_scroll'):
            parent.h_scroll.SetScrollbar(-self.pan_x, width, scroll_x_range, width)
        if self.v_scroll:
            current_scroll = -int(self.pan_y)
            current_scroll = max(0, min(current_scroll, scroll_y_range - height))  # ensure safe value

            if not hasattr(self, 'last_scroll_y_range') or self.last_scroll_y_range != scroll_y_range:
                self.v_scroll.SetScrollbar(current_scroll, height, scroll_y_range, height)
                self.last_scroll_y_range = scroll_y_range
            else:
                self.v_scroll.SetThumbPosition(current_scroll)

        # Draw a all trace signals
        j = 0
        for key in self.monitors.monitors_dictionary:
            trace = self.monitors.monitors_dictionary[key]
            GL.glColor3f(0.0, 0.0, 1.0)
            GL.glBegin(GL.GL_LINE_STRIP)

            y_base = height - padding_y - (j + 0) * signal_height - 50
            y_high = y_base + 20

            for i, sig in enumerate(trace):
                x = padding_x + i * x_step
                x_next = padding_x+ (i + 1) * x_step
                y = int(sig)
                if y == 0:
                    y = y_base
                else:
                    y = y_high
                GL.glVertex2f(x, y)
                GL.glVertex2f(x_next, y)
                print(x_next)
            GL.glEnd()

            # Draw time axis below trace
            GL.glColor3f(0.6, 0.6, 0.6)
            axis_y = y_base - 5
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(padding_x, axis_y)
            GL.glVertex2f(x_next, axis_y)
            GL.glEnd()

            # Draw ticks and labels
            for i in range(len(trace)+1):
                tick_x = padding_x + i * x_step
                GL.glBegin(GL.GL_LINES)
                GL.glVertex2f(tick_x, axis_y - 3)
                GL.glVertex2f(tick_x, axis_y + 3)
                GL.glEnd()
                self.render_text(str(i), tick_x - 5, axis_y - 15)


            # Draw device name to the left of trace
            name = self.names.get_name_string(key[0])
            pin = self.names.get_name_string(key[1]) if key[1] is not None else None
            label = f"{name}.{pin}" if pin is not None else str(name)
            self.render_text(label, 5, y_base + 5)

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
        self.render()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False
        self.Refresh()     # Trigger repaint
        event.Skip()
        

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
            text = "".join([_("Mouse button pressed at: "), str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join([_("Mouse button released at: "), str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join([_("Mouse left canvas at: "), str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            
            '''self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join([_("Mouse dragged to: "), str(event.GetX()),
                            ", ", str(event.GetY()), _(". Pan is now: "),
                            str(self.pan_x), ", ", str(self.pan_y)])'''
        if event.GetWheelRotation() < 0:
            '''self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join([_("Negative mouse wheel rotation. Zoom is now: "),
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join([_("Positive mouse wheel rotation. Zoom is now: "),
                            str(self.zoom)])
        if text:
            self.render()
        else:
            self.Refresh()  # triggers the paint event'''

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

    help_command(self): Display the help text in a message box.

    monitor_command(self, text): Set the specified monitor.

    zap_command(self, text): Remove the specified monitor.

    run_command(self, N): Run the simulation from scratch.

    run_network(self, N): Run the network for N cycles and draw the signal
    traces.

    continue_command(self, N): Continue the simulation for N more cycles.

    switch_command(self, device, new_value): Set the specified switch to the
    specified signal level.

    read_name(self, text): Return the name ID of the current string if valid.

    read_signal_name(self, text): Return the device and port IDs of the current
    signal name.

    read_value(self, text): Return the value of the current signal.

    invalid_command(self): Display an error message for invalid input.

    invalid_cycles(self): Display an error message for invalid cycle input.

    invalid_device_id(self): Display an error message for invalid device ID.

    invalid_port_id(self): Display an error message for invalid port ID.

    invalid_value(self): Display an error message for invalid value.

    empty_input(self): Display an error message for empty input.

    successful_command(self): Display a success message.

    unsuccessful_command(self): Display an error message for unsuccessful
    command.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, _("&About"))
        fileMenu.Append(wx.ID_HELP_COMMANDS, _('Help'))
        fileMenu.Append(wx.ID_EXIT, _("&Exit"))
        menuBar.Append(fileMenu, _("&Menu"))
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        #self.canvas_scroll = wx.ScrolledWindow(self, style=wx.VSCROLL| wx.HSCROLL)
        #self.canvas_scroll.SetScrollRate(10, 10)
        #self.canvas_scroll.SetupScrolling()
         # Set minimum size for scrolling
        #canvas_sizer = wx.BoxSizer(wx.VERTICAL)
        #canvas_sizer.Add(self.canvas, 1, wx.EXPAND)
        #self.canvas_scroll.SetSizer(canvas_sizer)

        canvas_area = wx.BoxSizer(wx.VERTICAL)
        h_scrollbar = wx.ScrollBar(self, style=wx.SB_HORIZONTAL)
        v_scrollbar = wx.ScrollBar(self, style=wx.SB_VERTICAL)

        

        self.h_scroll = h_scrollbar
        self.v_scroll = v_scrollbar
        self.canvas = MyGLCanvas(self, devices, monitors, names, self.h_scroll, self.v_scroll)

        canvas_area.Add(self.canvas, 1, wx.EXPAND)
        canvas_area.Add(h_scrollbar, 0, wx.EXPAND)

        self.h_scroll.SetScrollbar(0, 100, 1000, 100)
        self.v_scroll.SetScrollbar(0, 100, 1000, 100)

        self.h_scroll.Bind(wx.EVT_SCROLL, self.on_h_scroll)
        self.v_scroll.Bind(wx.EVT_SCROLL, self.on_v_scroll)
        self.last_scroll_y_range = None



        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, _("Cycles"))
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, _("Run"))
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
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.side_sizer = wx.BoxSizer(wx.VERTICAL)
        

        self.main_sizer.Add(canvas_area, 5, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(v_scrollbar,0,wx.EXPAND)
        self.main_sizer.Add(self.side_sizer, 1, wx.ALL, 5)
        
        #self.device_scroll = wx.ScrolledWindow(self, style=wx.VSCROLL)
        #self.device_scroll.SetScrollRate(5, 5)
        self.device_scroll = ScrolledPanel(self, style=wx.VSCROLL)
        self.device_scroll.SetupScrolling()

        self.device_button_sizer = wx.BoxSizer(wx.VERTICAL)
        self.device_scroll.SetSizer(self.device_button_sizer)



        


        self.side_sizer.Add(self.text, 1, wx.TOP, 10)
        self.side_sizer.Add(self.spin, 1, wx.ALL, 5)
        self.side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        self.side_sizer.Add(self.text_box, 1, wx.ALL, 5)
        self.side_sizer.Add(self.output_text, 1, wx.EXPAND | wx.ALL, 5)
        #self.side_sizer.Add(self.device_scroll, 1, wx.EXPAND | wx.ALL, 5)
        self.device_scroll.SetMinSize((150, 450))  # or whatever minimum height you want
        self.side_sizer.Add(self.device_scroll, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizeHints(600, 680)
        self.SetSizer(self.main_sizer)
        
        self.run_network(10)  # Run the network for 10 cycles on startup
        self.invalid_command()  # Set initial output text
        self.output_text.SetLabel("软件 Программное обеспечение برمجة")
        self.populate_side_sizer()
        
        self.Layout()
        self.Maximize()
        self.Fit()
        self.Refresh()
        self.Centre()
        self.GetSizer().Fit(self)

        #add buttons to the side sizer for every monitored and non-monitored device allowing the user to monitor or unmonitor the device
        # the user can also switch the device state if it is a switch
    # Clear the side_sizer first (optional, for refreshes)

        

        # Bind the close event to the on_close method
        #self.Bind(wx.EVT_CLOSE, self.on_close)
    def on_h_scroll(self, event):
        pos = self.h_scroll.GetThumbPosition()
        self.canvas.pan_x = -pos
        self.canvas.init = False
        self.canvas.Refresh()

    def on_v_scroll(self, event):
        pos = self.v_scroll.GetThumbPosition()
        max_scroll = self.v_scroll.GetRange() - self.v_scroll.GetThumbSize()
        pos = max(0, min(pos, max_scroll))  # strict clamp
        self.canvas.pan_y = pos
        self.canvas.init = False
        self.canvas.Refresh()



    def populate_side_sizer(self):
        # Clear only the dynamic button section
        self.device_scroll.Freeze()
        self.device_button_sizer.Clear(delete_windows=True)

        monitored_list, non_monitored_list = self.monitors.get_signal_names()

        # --- Monitored Devices ---
        monitored_title = wx.StaticText(self.device_scroll, label=_("Monitored Devices"))
        monitored_title.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.device_button_sizer.Add(monitored_title, 0, wx.ALL, 5)

        for device_name in monitored_list:
            device_id = self.names.query(device_name)
            device = self.devices.get_device(device_id)
            #if device_id is not None:
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self.device_scroll, label=device_name)
            hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
            unmonitor_btn = wx.Button(self.device_scroll, wx.ID_ANY, label=_("Unmonitor"))
            #unmonitor_btn.SetBackgroundColour(wx.Colour(200, 0, 0))
            unmonitor_btn.Bind(wx.EVT_BUTTON, partial(self.on_unmonitor_click, device_name))
            hbox.Add(unmonitor_btn, 0, wx.RIGHT, 5)
            if device and device.device_kind == self.devices.SWITCH:
                flip_btn = wx.Button(self.device_scroll, wx.ID_ANY, label=_("Flip Switch"))
                flip_btn.Bind(wx.EVT_BUTTON, partial(self.on_flip_click, device_name))
                hbox.Add(flip_btn, 0, wx.RIGHT, 5)
            self.device_button_sizer.Add(hbox, 0, wx.ALL | wx.EXPAND, 5)
            

        # --- Unmonitored Section Title ---
        unmonitored_title = wx.StaticText(self.device_scroll, label=_("Unmonitored Devices"))
        unmonitored_title.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.device_button_sizer.Add(unmonitored_title, 0, wx.TOP | wx.ALL, 10)

        for device_name in non_monitored_list:
            device_id = self.names.query(device_name)
            device = self.devices.get_device(device_id)

            hbox = wx.BoxSizer(wx.HORIZONTAL)

            # Device name label
            label = wx.StaticText(self.device_scroll, label=device_name)
            hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

            # Monitor button
            monitor_btn = wx.Button(self.device_scroll, wx.ID_ANY, label=_("Monitor"))
            monitor_btn.Bind(wx.EVT_BUTTON, partial(self.on_monitor_click, device_name))
            hbox.Add(monitor_btn, 0, wx.RIGHT, 5)

            # Optional: Flip Switch button
            if device and device.device_kind == self.devices.SWITCH:
                flip_btn = wx.Button(self.device_scroll, wx.ID_ANY, label=_("Flip Switch"))
                flip_btn.Bind(wx.EVT_BUTTON, partial(self.on_flip_click, device_name))
                hbox.Add(flip_btn, 0, wx.RIGHT, 5)

            self.device_button_sizer.Add(hbox, 0, wx.ALL | wx.EXPAND, 5)
        
        self.device_scroll.Layout()
        self.device_scroll.FitInside()
        self.device_scroll.Thaw()
        


    def on_unmonitor_click(self, device_name, event):
        self.zap_command(device_name)
        self.populate_side_sizer()

    def on_flip_click(self, device_name, event):
        self.canvas.Freeze()
        self.monitor_command(device_name)
        self.toggle_switch(device_name)
        self.zap_command(device_name)
        self.populate_side_sizer()
        self.canvas.Thaw()

    def on_monitor_click(self, device_name, event):
        self.monitor_command(device_name)
        self.populate_side_sizer()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_HELP_COMMANDS:
            self.help_command()

        if Id == wx.ID_ABOUT:
            wx.MessageBox(_("Logic Simulator\nCreated by Team 1\n2025"),
                          _("About Logsim"), wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render()

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


    def toggle_switch(self, device_name):
        """Toggle the state of the specified switch."""
        device_id = self.read_name(device_name)
        current_value = str(self.monitors.get_monitor_signal(device_id, None))
        new_value = "0" if current_value == "1" else "1"
        self.switch_command(device_name, new_value)
        self.populate_side_sizer()  # Refresh the side sizer to reflect changes


    def help_command(self):
        """Display the help text in a message box."""
        with open("Help.txt", "r") as file:
            help_text = file.read()
        self.output_text.SetLabel("")
        wx.MessageBox(help_text, _("Help"), wx.ICON_INFORMATION | wx.OK)

    def monitor_command(self, text):
        """Set the specified monitor."""
        monitor = self.read_signal_name(text)
        if monitor is None:
            self.invalid_device_id()
            return
        else:
            [device, port] = monitor
            if port is not None:
                [port] = self.names.lookup([port])
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                self.successful_command()
                self.populate_side_sizer()  # Refresh the side sizer to reflect changes
                self.continue_command("0")
            else:
                self.unsuccessful_command()  
            

    def zap_command(self, text):
        """Remove the specified monitor."""
        monitor = self.read_signal_name(text)
        if monitor is None:
            self.invalid_device_id()
        else:
            [device, port] = monitor
            if port is not None:
                [port]=self.names.lookup([port])
            if self.monitors.remove_monitor(device, port):
                self.successful_command()
                self.populate_side_sizer()
            else:
                self.unsuccessful_command()
        self.continue_command("0")
    
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
        self.canvas.render()
        self.successful_command()

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
        self.output_text.SetLabel(_("Invalid command.\n Enter 'h' for help."))

    def invalid_cycles(self):
        """Display an error message for invalid cycle input."""
        self.output_text.SetLabel(_("Invalid Number of cycles.\n Enter 'h' for help."))

    def invalid_device_id(self):
        """Display an error message for invalid device ID."""
        self.output_text.SetLabel(_("Invalid device ID.\n Enter 'h' for help."))
    
    def invalid_port_id(self):
        """Display an error message for invalid port ID."""
        self.output_text.SetLabel(_("Invalid port ID.\n Enter 'h' for help."))

    def invalid_value(self):
        """Display an error message for invalid value."""
        self.output_text.SetLabel(_("Invalid value.\n Enter 'h' for help."))
    
    def empty_input(self):
        """Display an error message for empty input."""
        self.output_text.SetLabel(_("No command entered.\n Enter 'h' for help."))

    def successful_command(self):
        """Display a success message."""
        self.output_text.SetLabel(_("Command executed successfully."))
    
    def unsuccessful_command(self):
        """Display an error message for unsuccessful command."""
        self.output_text.SetLabel(_("Command execution failed.\n Enter 'h' for help."))

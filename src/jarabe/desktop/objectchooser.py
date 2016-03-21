# Only for Journal Rethink prototype
from gettext import gettext as _
import logging

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Wnck

from sugar3.graphics import style
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbutton import ToolButton


from jarabe.desktop.activitieslist import ActivitiesList

class ObjectChooser(Gtk.Window):

    #__gtype_name__ = 'ObjectChooser'

    __gsignals__ = {
        'response': (GObject.SignalFlags.RUN_FIRST, None, ([int])),
    }

    def __init__(self):
        logging.debug('In the Object Chooser class init hehehe')
        Gtk.Window.__init__(self)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_border_width(style.LINE_WIDTH)
        self.set_has_resize_grip(False)
 
        self.add_events(Gdk.EventMask.VISIBILITY_NOTIFY_MASK)
        self.connect('delete-event', self.__delete_event_cb)
        #self.connect('visibility-notify-event',
        #             self.__visibility_notify_event_cb)
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0,0,0))
        screen = Wnck.Screen.get_default()
        screen.connect('window-closed', self.__window_closed_cb)

        
        vbox = Gtk.VBox()
        self.add(vbox)
        vbox.show()

        title_box = TitleBox()
        #title_box.connect('volume-changed', self.__volume_changed_cb)
        title_box.close_button.connect('clicked',
                                       self.__close_button_clicked_cb)
        title_box.set_size_request(-1, style.GRID_CELL_SIZE)
        vbox.pack_start(title_box, False, True, 0)
        title_box.show()

        self._list_view = ActivitiesList()
        vbox.pack_start(self._list_view, True, True, 0)
        self._list_view.show()

        width = Gdk.Screen.width() - style.GRID_CELL_SIZE * 5
        height = Gdk.Screen.height() - style.GRID_CELL_SIZE * 3
        self.set_size_request(width, height)
        self.show()
        logging.debug('In the Object Chooser class init ended hehehe')

    #def __realize_cb(self, chooser, parent):
     #   self.get_window().set_transient_for(parent)

    def __window_closed_cb(self, screen, window):
        #if window.get_xid() == parent.get_xid():
            self.destroy()

    def __delete_event_cb(self, chooser, event):
        self.emit('response', Gtk.ResponseType.DELETE_EVENT)

    def __close_button_clicked_cb(self, button):
        self.emit('response', Gtk.ResponseType.DELETE_EVENT)
        self.destroy()


class TitleBox(ToolbarBox):
    #__gtype_name__ = 'TitleBox'

    def __init__(self):
        #VolumesToolbar.__init__(self)
        ToolbarBox.__init__(self)
        label = Gtk.Label()
        title = _('Choose an object')
        
        label.set_markup('<b>%s</b>' % title)
        label.set_alignment(0, 0.5)
        self._add_widget(label, expand=True)

        self.close_button = ToolButton(icon_name='dialog-cancel')
        self.close_button.set_tooltip(_('Close'))
        self.toolbar.insert(self.close_button, -1)
        self.close_button.show()


    def _add_widget(self, widget, expand=False):
        tool_item = Gtk.ToolItem()
        tool_item.set_expand(expand)

        tool_item.add(widget)
        widget.show()

        self.toolbar.insert(tool_item, -1)
        tool_item.show()






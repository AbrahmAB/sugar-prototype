# Copyright (C) 2013, Gonzalo Odiard
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
import time
from gettext import gettext as _

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GLib
#Prototype code starts ---
from sugar3 import profile
from sugar3.graphics.palettewindow import TreeViewInvoker
from gi.repository import Gdk
from jarabe.journal import misc
from jarabe.journal import journalwindow
from sugar3.graphics.icon import Icon, CellRendererIcon
from jarabe.journal.palettes import ObjectPalette
#Prottype code ends ---
from jarabe.journal.iconmodel import IconModel
from sugar3.graphics.icon import Icon
from jarabe.journal import model
from sugar3.graphics.objectchooser import get_preview_pixbuf
from sugar3.graphics import style
from sugar3.activity.activity import PREVIEW_SIZE

#Prototype code starts ---

class PreviewFavoriteRenderer(CellRendererIcon):

    #__gtype_name__ = 'JournalCellRendererFavorite'

    def __init__(self):
        CellRendererIcon.__init__(self)

        self.props.width = style.GRID_CELL_SIZE
        self.props.height = style.GRID_CELL_SIZE
        self.props.size = style.SMALL_ICON_SIZE
        self.props.icon_name = 'emblem-favorite'
        self.props.sensitive = False

        
#Prototype code ends ---
     

class PreviewRenderer(Gtk.CellRendererPixbuf):

    def __init__(self, **kwds):
        Gtk.CellRendererPixbuf.__init__(self, **kwds)
        self._preview_data = None

    def set_preview_data(self, data):
        self._preview_data = data

    def do_render(self, cr, widget, background_area, cell_area, flags):
        self.props.pixbuf = get_preview_pixbuf(self._preview_data)
        Gtk.CellRendererPixbuf.do_render(self, cr, widget, background_area,
                                         cell_area, flags)

    def do_get_size(self, widget, cell_area):
        x_offset, y_offset, width, height = Gtk.CellRendererPixbuf.do_get_size(
            self, widget, cell_area)
        width = PREVIEW_SIZE[0]
        height = PREVIEW_SIZE[1]
        return (x_offset, y_offset, width, height)


class PreviewIconView(Gtk.IconView):
    __gsignals__ = {
        'detail-clicked': (GObject.SignalFlags.RUN_FIRST, None,
                           ([object])),
        'volume-error': (GObject.SignalFlags.RUN_FIRST, None,
                         ([str, str])),
    }

    def __init__(self, title_col, preview_col, fav_col, journalactivity):
        Gtk.IconView.__init__(self)

        self._preview_col = preview_col
        self._title_col = title_col
        self._fav_col = fav_col
        self.set_spacing(3)
        #Prototype code starts ---
        self._journalactivity = journalactivity
        self._palette_invoker = TreeViewInvoker()
        self._palette_invoker.attach_treeview(self)
        #_favorite_renderer = PreviewFavoriteRenderer()
        #_favorite_renderer.set_alignment(0.5, 0.5)
        #self.pack_start(_favorite_renderer, False)
        #self.set_cell_data_func(_favorite_renderer,
        #                        self._favorite_data_func, None)
        #Prototype code ends ---
        _favorite_renderer = PreviewFavoriteRenderer()
        _favorite_renderer.set_alignment(0.5, 0.5)
        self.pack_start(_favorite_renderer, False)
        self.set_cell_data_func(_favorite_renderer,
                                self._favorite_data_func, None)

        _preview_renderer = PreviewRenderer()
        _preview_renderer.set_alignment(0.5, 0.5)
        self.pack_start(_preview_renderer, False)
        self.set_cell_data_func(_preview_renderer,
                                self._preview_data_func, None)

        _title_renderer = Gtk.CellRendererText()
        #Prototype code starts ---
        _title_renderer.props.ellipsize = style.ELLIPSIZE_MODE_DEFAULT
        _title_renderer.props.ellipsize_set = True
        #Prototype code ends ---
        _title_renderer.set_alignment(0.5, 0.5)
        self.pack_start(_title_renderer, True)
        self.set_cell_data_func(_title_renderer,
                                self._title_data_func, None)

    #Prototype code starts ---
    def _favorite_data_func(self, view, cell, store, i, data):
        favorite = store.get_value(i, self._fav_col)
        logging.debug('face off %r',favorite)
        if favorite:
            logging.debug('face off')
            cell.props.xo_color = profile.get_color()
        else:
            cell.props.xo_color = None

    #Prototype code ends ---
    def _preview_data_func(self, view, cell, store, i, data):
        preview_data = store.get_value(i, self._preview_col)
        cell.set_preview_data(preview_data)

    def _title_data_func(self, view, cell, store, i, data):
        title = store.get_value(i, self._title_col)
        cell.props.markup = title

    def create_palette(self, path):
        logging.debug('Pallete will be created')
        #path = self.get_cursor()
        metadata_item = self.get_model().get_metadata(path)
        logging.debug('Path for palette is %r', metadata_item['title'])
        palette = ObjectPalette(self._journalactivity, metadata_item, detail = True)
        palette.connect('detail-clicked', self.__detail_clicked_cb)
        palette.connect('volume-error', self.__volume_error_cb)
        return palette

    def get_palette_invoker(self):
        return self._palette_invoker

    palette_invoker = GObject.property(type = object, getter = get_palette_invoker)

    def _scroll_start_cb(self, event):
        self._invoker.detach()

    def _scroll_end_cb(self, event):
        self._invoker.attach_treeview(self)

    def __detail_clicked_cb(self, palette, uid):
        self.emit('detail-clicked', uid)

    def __volume_error_cb(self, palette, message, severity):
        self.emit('volume-error', message, severity)

    def __del__(self):
        self._invoker.detach()



class IconView(Gtk.Bin):
    __gtype_name__ = 'JournalBaseIconView'

    __gsignals__ = {
        'clear-clicked': (GObject.SignalFlags.RUN_FIRST, None, ([])),
        'entry-activated': (GObject.SignalFlags.RUN_FIRST,
                            None, ([str])),
        'detail-clicked': (GObject.SignalFlags.RUN_FIRST, None,
                           ([object])),
        'volume-error': (GObject.SignalFlags.RUN_FIRST, None,
                         ([str, str])),
    
    }

    def __init__(self, toolbar, journalactivity):
        self._query = {}
        self._model = None
        self._progress_bar = None
        self._last_progress_bar_pulse = None
        self._scroll_position = 0.
        self._toolbar = toolbar
        self._journalactivity = journalactivity
        Gtk.Bin.__init__(self)
        #print "heyy instance creattion"
        self.connect('map', self.__map_cb)
        self.connect('unrealize', self.__unrealize_cb)
        self.connect('destroy', self.__destroy_cb)

        self._scrolled_window = Gtk.ScrolledWindow()
        self._scrolled_window.set_policy(Gtk.PolicyType.NEVER,
                                         Gtk.PolicyType.AUTOMATIC)
        self.add(self._scrolled_window)
        self._scrolled_window.show()

        self.icon_view = PreviewIconView(IconModel.COLUMN_TITLE,
                                         IconModel.COLUMN_PREVIEW,
                                         IconModel.COLUMN_FAVORITE,
                                         self._journalactivity)
        self.icon_view.connect('item-activated', self.__item_activated_cb)
        self.icon_view.connect('detail-clicked', self.__detail_clicked_cb)
        self.icon_view.connect('volume-error', self.__volume_error_cb)
        self.icon_view.connect('button-release-event',
                               self.__button_release_event_cb)

        self._scrolled_window.add(self.icon_view)
        self.icon_view.show()

        # Auto-update stuff
        self._fully_obscured = True
        self._dirty = False
        self._refresh_idle_handler = None

        model.created.connect(self.__model_created_cb)
        model.updated.connect(self.__model_updated_cb)
        model.deleted.connect(self.__model_deleted_cb)

    def __button_release_event_cb(self, icon_view, event):
        if event.button ==  Gdk.BUTTON_PRIMARY:
            logging.debug('Activity resumes!')
            path = icon_view.get_path_at_pos(int(event.x), int(event.y))
            if path is None:
                return False
            uid = icon_view.get_model()[path][IconModel.COLUMN_UID]
            metadata_item = icon_view.get_model().get_metadata(path)
            misc.resume(metadata_item,
                        alert_window=journalwindow.get_journal_window())
            
            self.emit('entry-activated', uid)
            return False
        elif event.button == Gdk.BUTTON_SECONDARY:
            return False

    def __item_activated_cb(self, icon_view, path):
        uid = icon_view.get_model()[path][IconModel.COLUMN_UID]
        self.emit('entry-activated', uid)

    def _thumb_data_func(self, view, cell, store, i, data):
        preview_data = store.get_value(i, IconModel.COLUMN_PREVIEW)
        cell.props.pixbuf = get_preview_pixbuf(preview_data)

    def __model_created_cb(self, sender, signal, object_id):
        if self._is_new_item_visible(object_id):
            self._set_dirty()

    def __model_updated_cb(self, sender, signal, object_id):
        #Prototype code starts ---
        #print "Is updated here in icon"
        #Prototype code ends ---

        if self._is_new_item_visible(object_id):
            self._set_dirty()

    def __model_deleted_cb(self, sender, signal, object_id):
        if self._is_new_item_visible(object_id):
            self._set_dirty()

    def _is_new_item_visible(self, object_id):
        """Check if the created item is part of the currently selected view"""
        if self._query['mountpoints'] == ['/']:
            return not object_id.startswith('/')
        else:
            return object_id.startswith(self._query['mountpoints'][0])

    def do_size_allocate(self, allocation):
        self.set_allocation(allocation)
        self.get_child().size_allocate(allocation)

    def __detail_clicked_cb(self, palette, uid):
        self.emit('detail-clicked', uid)

    def __volume_error_cb(self, palette, message, severity):
        self.emit('volume-error', message, severity)

    def __destroy_cb(self, widget):
        if self._model is not None:
            self._model.stop()

    def update_with_query(self, query_dict):
        if 'order_by' not in query_dict:
            query_dict['order_by'] = ['+timestamp']
        self._query = query_dict
        self.refresh()

    def refresh(self):
        logging.debug('IconView.refresh query %r', self._query)
        self._stop_progress_bar()

        if self._model is not None:
            self._model.stop()
        self._dirty = False

        self._model = IconModel(self._query)
        self._model.connect('ready', self.__model_ready_cb)
        self._model.connect('progress', self.__model_progress_cb)
        self._model.setup()

    def __model_ready_cb(self, tree_model):
        self._stop_progress_bar()

        self._scroll_position = self.icon_view.props.vadjustment.props.value
        logging.debug('IconView.__model_ready_cb %r', self._scroll_position)

        # Cannot set it up earlier because will try to access the model
        # and it needs to be ready.
        self.icon_view.set_model(self._model)

        self.icon_view.props.vadjustment.props.value = self._scroll_position
        self.icon_view.props.vadjustment.value_changed()

        if len(tree_model) == 0:
            documents_path = model.get_documents_path()
            if self._is_query_empty():
                if self._query['mountpoints'] == ['/']:
                    self._show_message(_('Your Journal is empty'))
                elif documents_path and self._query['mountpoints'] == \
                        [documents_path]:
                    self._show_message(_('Your documents folder is empty'))
                else:
                    self._show_message(_('The device is empty'))
            else:
                self._show_message(
                    _('No matching entries'),
                    show_clear_query=self._toolbar.is_filter_changed())
        else:
            self._clear_message()

    def __map_cb(self, widget):
        logging.debug('IconView.__map_cb %r', self._scroll_position)
        self.icon_view.props.vadjustment.props.value = self._scroll_position
        self.icon_view.props.vadjustment.value_changed()
        #Prototyp code starts ---
        self.set_is_visible(True)
        #Prototyp code ends ---

    def __unrealize_cb(self, widget):
        self._scroll_position = self.icon_view.props.vadjustment.props.value
        # logging.debug('IconView.__map_cb %r', self._scroll_position)
        #Prototyp code starts ---
        logging.debug('IconView.__unrealize_cb %r', self._scroll_position)
        self.set_is_visible(False)
        #Prototyp code ends ---

    def _is_query_empty(self):
        # FIXME: This is a hack, we shouldn't have to update this every time
        # a new search term is added.
        return not (self._query.get('query') or self._query.get('mime_type') or
                    self._query.get('keep') or self._query.get('mtime') or
                    self._query.get('activity'))

    def __model_progress_cb(self, tree_model):
        if self._progress_bar is None:
            self._start_progress_bar()

        if time.time() - self._last_progress_bar_pulse > 0.05:
            self._progress_bar.pulse()
            self._last_progress_bar_pulse = time.time()

    def _start_progress_bar(self):
        alignment = Gtk.Alignment.new(xalign=0.5, yalign=0.5,
                                      xscale=0.5, yscale=0)
        self.remove(self.get_child())
        self.add(alignment)
        alignment.show()

        self._progress_bar = Gtk.ProgressBar()
        self._progress_bar.props.pulse_step = 0.01
        self._last_progress_bar_pulse = time.time()
        alignment.add(self._progress_bar)
        self._progress_bar.show()

    def _stop_progress_bar(self):
        if self._progress_bar is None:
            return
        self.remove(self.get_child())
        self.add(self._scrolled_window)
        self._progress_bar = None

    def _show_message(self, message, show_clear_query=False):
        self.remove(self.get_child())

        background_box = Gtk.EventBox()
        background_box.modify_bg(Gtk.StateType.NORMAL,
                                 style.COLOR_WHITE.get_gdk_color())
        self.add(background_box)

        alignment = Gtk.Alignment.new(0.5, 0.5, 0.1, 0.1)
        background_box.add(alignment)

        box = Gtk.VBox()
        alignment.add(box)

        icon = Icon(pixel_size=style.LARGE_ICON_SIZE,
                    icon_name='activity-journal',
                    stroke_color=style.COLOR_BUTTON_GREY.get_svg(),
                    fill_color=style.COLOR_TRANSPARENT.get_svg())
        box.pack_start(icon, expand=True, fill=False, padding=0)

        label = Gtk.Label()
        color = style.COLOR_BUTTON_GREY.get_html()
        label.set_markup('<span weight="bold" color="%s">%s</span>' % (
            color, GLib.markup_escape_text(message)))
        box.pack_start(label, expand=True, fill=False, padding=0)

        if show_clear_query:
            button_box = Gtk.HButtonBox()
            button_box.set_layout(Gtk.ButtonBoxStyle.CENTER)
            box.pack_start(button_box, False, True, 0)
            button_box.show()

            button = Gtk.Button(label=_('Clear search'))
            button.connect('clicked', self.__clear_button_clicked_cb)
            button.props.image = Icon(icon_name='dialog-cancel',
                                      pixel_size=style.SMALL_ICON_SIZE)
            button_box.pack_start(button, expand=True, fill=False, padding=0)

        background_box.show_all()

    def __clear_button_clicked_cb(self, button):
        self.emit('clear-clicked')

    def _clear_message(self):
        if self.get_child() == self._scrolled_window:
            return
        self.remove(self.get_child())
        self.add(self._scrolled_window)
        self._scrolled_window.show()

    def _set_dirty(self):
        if self._fully_obscured:
            #Prototype code starts ---
            print "fully obscured here icon"
            #Prototype code ends ---

            self._dirty = True
        else:
            #Prototype code starts ---
            print "is not obscured here icon"
            #Prototype code ends ---

            self.refresh()

    def set_is_visible(self, visible):
        if visible != self._fully_obscured:
            return
        #Prototyp code starts ---
        logging.debug('canvas_visibility_notify_event_cb icon %r', visible)
        #Prototyp code ends ---
        if visible:
            self._fully_obscured = False
            if self._dirty:
                self.refresh()
        else:
            self._fully_obscured = True

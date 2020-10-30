"""Implementation, widget, and popup classes for file selection dialogs
"""

import py_cui.ui
import py_cui.widgets
import py_cui.popups
import os


class FileDirElem:

    def __init__(self, elem_type, name, fullpath, ascii_icons=False):
        self._type = elem_type
        self._name = name
        self._path = fullpath
        if not ascii_icons:
            self._folder_icon = '\U0001f4c1'
            # Folder icon is two characters, so 
            self._file_icon = '\U0001f5ce' + ' '
        else:
            self._folder_icon = '<DIR>'
            self._file_icon = '     '

    def __str__(self):

        if self._type == 'file':
            return '{} {}'.format(self._file_icon, self._name)
        else:
            return '{} {}'.format(self._folder_icon, self._name)



class FileSelectImplementation(py_cui.ui.MenuImplementation):


    def __init__(self, initial_loc, dialog_type, ascii_icons, logger, limit_extensions = []):
        super().__init__(logger)
        
        self._current_dir = os.path.abspath(initial_loc)
        self._ascii_icons = ascii_icons
        self._dialog_type = dialog_type

        self.refresh_view()
        self._limit_extensions = limit_extensions


    def refresh_view(self):

        if not os.path.exists(self._current_dir):
            raise FileNotFoundError
        else:
            self.clear()
            dirs = []
            files = []
            for item in os.listdir(self._current_dir):
                item_path = os.path.join(self._current_dir, item)
                if os.path.isdir(item_path):
                    dirs.append(FileDirElem('dir', item, item_path, ascii_icons=self._ascii_icons))
                else:
                    files.append(FileDirElem('file', item, item_path, ascii_icons=self._ascii_icons))

            if self._dialog_type == 'openfile':
                self.add_item_list(dirs)
                self.add_item_list(files)
            elif self._dialog_type == 'opendir':
                self.add_item_list(dirs)
            self.set_title(os.path.basename(self._current_dir))


class FileSelectElement(py_cui.ui.UIElement, FileSelectImplementation):

    """A scroll menu popup.

    Allows for popup with several menu items to select from

    Attributes
    ----------
    _command : function
        a function that takes a single string parameter, run when ENTER pressed
    _run_command_if_none : bool
        Runs command even if there are no menu items (passes None)
    """

    def __init__(self, root, initial_dir, dialog_type, ascii_icons, title, color, command, renderer, logger):
        """Initializer for MenuPopup. Uses MenuImplementation as base
        """

        py_cui.ui.UIElement.__init__(self, 0, '', renderer, logger)
        FileSelectImplementation.__init__(self, initial_dir, dialog_type, ascii_icons, logger)
        self._command              = command
        self._parent_dialog        = root
        #self._run_command_if_none  = run_command_if_none


    def get_absolute_start_pos(self):
        """Override of base function. Uses the parent element do compute start position

        Returns
        -------
        start_x, start_y : int, int
            The position in characters in the terminal window to start the Field element
        """

        parent_start_x, parent_start_y = self._parent_dialog.get_start_position()
        start_x = (parent_start_x + 3 + self._parent_dialog._padx)
        start_y = (parent_start_y + self._parent_dialog._pady + 3)
        return start_x, start_y


    def get_absolute_stop_pos(self):
        """Override of base function. Uses the parent element do compute stop position

        Returns
        -------
        stop_x, stop_y : int, int
            The position in characters in the terminal window to stop the Field element
        """

        parent_stop_x, parent_stop_y = self._parent_dialog.get_stop_position()
        stop_x = (parent_stop_x - 3 - self._parent_dialog._padx)
        stop_y = (parent_stop_y - self._parent_dialog._pady - 7)
        return stop_x, stop_y


    def _handle_key_press(self, key_pressed):
        """Override of base handle key press function

        Enter key runs command, Escape key closes menu

        Parameters
        ----------
        key_pressed : int
            key code of key pressed
        """

        super()._handle_key_press(key_pressed)
        if key_pressed == py_cui.keys.KEY_ENTER:
            self._current_dir = os.path.join(self.get()._path)
            self.refresh_view()

        if key_pressed == py_cui.keys.KEY_UP_ARROW:
            self._scroll_up()
        if key_pressed == py_cui.keys.KEY_DOWN_ARROW:
            viewport_height = self._height - (2 * self._pady) - 3
            self._scroll_down(viewport_height)


    def _draw(self):
        """Overrides base class draw function
        """

        self._renderer.set_color_mode(self._color)
        self._renderer.draw_border(self)
        self._renderer.set_color_rules([])
        counter = self._pady + 1
        line_counter = 0
        for line in self._view_items:
            if line_counter < self._top_view:
                line_counter = line_counter + 1
            else:
                if counter >= self._height - self._pady - 1:
                    break
                if line_counter == self.get_selected_item_index():
                    self._renderer.draw_text(self, line, self._start_y + counter, selected=True)
                else:
                    self._renderer.draw_text(self, line, self._start_y + counter)
                counter = counter + 1
                line_counter = line_counter + 1
        self._renderer.unset_color_mode(self._color)
        self._renderer.reset_cursor(self)


class FileNameInput(py_cui.ui.UIElement, py_cui.ui.TextBoxImplementation):

    def __init__(self, parent_dialog, title, renderer, logger):
        """Initializer for the FormFieldElement class
        """

        self._parent_dialog = parent_dialog
        py_cui.ui.UIElement.__init__(self, 0, title, renderer, logger)
        py_cui.ui.TextBoxImplementation.__init__(self, title, False, logger)
        self._help_text = 'Press Tab to move to the next field, or Enter to submit.'
        self._padx = 0
        self._pady = 0
        self._selected = False
        self.update_height_width()


    def get_absolute_start_pos(self):
        """Override of base function. Uses the parent element do compute start position

        Returns
        -------
        start_x, start_y : int, int
            The position in characters in the terminal window to start the Field element
        """

        parent_start_x, _ = self._parent_dialog.get_start_position()
        _, parent_stop_y = self._parent_dialog.get_stop_position()
        start_x = (parent_start_x + 4 + self._parent_dialog._padx)
        start_y = (parent_stop_y - self._parent_dialog._pady - 7)
        return start_x, start_y


    def get_absolute_stop_pos(self):
        """Override of base function. Uses the parent element do compute stop position

        Returns
        -------
        stop_x, stop_y : int, int
            The position in characters in the terminal window to stop the Field element
        """

        parent_width, parent_height = self._parent_dialog.get_absolute_dimensions()
        parent_stop_x, parent_stop_y = self._parent_dialog.get_stop_position()
        stop_x = (parent_stop_x - 4 - int(5 * parent_width / 7))
        stop_y = (parent_stop_y - self._parent_dialog._pady - 2)
        return stop_x, stop_y



    def update_height_width(self):
        """Override of base class. Updates text field variables for form field
        """

        super().update_height_width()
        padx, pady              = self.get_padding()
        start_x, start_y        = self.get_start_position()
        height, width           = self.get_absolute_dimensions()
        self._cursor_text_pos   = 0
        self._cursor_x          = start_x + 2 + padx
        self._cursor_max_left   = self._cursor_x
        self._cursor_max_right  = start_x + width - 1 - pady
        self._cursor_y          = start_y + int(height / 2) + 1
        self._viewport_width    = self._cursor_max_right - self._cursor_max_left


    def _handle_key_press(self, key_pressed):
        """Handles text input for the field. Called by parent
        """

        if key_pressed == py_cui.keys.KEY_LEFT_ARROW:
            self._move_left()
        elif key_pressed == py_cui.keys.KEY_RIGHT_ARROW:
            self._move_right()
        elif key_pressed == py_cui.keys.KEY_BACKSPACE:
            self._erase_char()
        elif key_pressed == py_cui.keys.KEY_DELETE:
            self._delete_char()
        elif key_pressed == py_cui.keys.KEY_HOME:
            self._jump_to_start()
        elif key_pressed == py_cui.keys.KEY_END:
            self._jump_to_end()
        elif key_pressed > 31 and key_pressed < 128:
            self._insert_char(key_pressed)


    def _draw(self):
        """Draw function for the field. Called from parent. Essentially the same as a TextboxPopup
        """

        self._renderer.set_color_mode(self._parent_dialog._color)
        self._renderer.set_color_rules([])
        self._renderer.draw_text(self, self._title, self._cursor_y - 2, bordered=False, selected=self._selected)
        self._renderer.draw_border(self, fill=False, with_title=False)
        render_text = self._text
        if len(self._text) >self._viewport_width:
            end = len(self._text) - (self._viewport_width)
            if self._cursor_text_pos < end:
                render_text = self._text[self._cursor_text_pos:self._cursor_text_pos + (self._viewport_width)]
            else:
                render_text = self._text[end:]

        self._renderer.draw_text(self, render_text, self._cursor_y, selected=self._selected)

        if self._selected:
            self._renderer.draw_cursor(self._cursor_y, self._cursor_x)
        else:
            self._renderer.reset_cursor(self, fill=False)
        self._renderer.unset_color_mode(self._color)


class FileDialogButton(py_cui.ui.UIElement):


    def __init__(self, parent_dialog, statusbar_msg, command, button_num, *args):
        """Initializer for Button Widget
        """

        super().__init__(*args)
        self._parent_dialog = parent_dialog
        self.set_color(py_cui.MAGENTA_ON_BLACK)
        self.set_help_text(statusbar_msg)
        self.command = command
        self._button_num = button_num


    def get_absolute_start_pos(self):
        """Override of base function. Uses the parent element do compute start position

        Returns
        -------
        start_x, start_y : int, int
            The position in characters in the terminal window to start the Field element
        """

        parent_start_x, _ = self._parent_dialog.get_start_position()
        _, parent_stop_y = self._parent_dialog.get_stop_position()
        start_x = (parent_start_x + 3 + self._parent_dialog._padx)
        start_y = (parent_stop_y - self._parent_dialog._pady - 5)
        return start_x, start_y


    def get_absolute_stop_pos(self):
        """Override of base function. Uses the parent element do compute stop position

        Returns
        -------
        stop_x, stop_y : int, int
            The position in characters in the terminal window to stop the Field element
        """

        parent_stop_x, parent_stop_y = self._parent_dialog.get_stop_position()
        stop_x = (parent_stop_x - 3 - self._parent_dialog._padx)
        stop_y = (parent_stop_y - self._parent_dialog._pady - 1)
        return stop_x, stop_y


    def _handle_key_press(self, key_pressed):
        """Override of base class, adds ENTER listener that runs the button's command

        Parameters
        ----------
        key_pressed : int
            Key code of pressed key
        """

        super()._handle_key_press(key_pressed)
        if key_pressed == py_cui.keys.KEY_ENTER:
            if self.command is not None:
                ret = self.command()
            return ret


    def _draw(self):
        """Override of base class draw function
        """

        super()._draw()
        self._renderer.set_color_mode(self.get_color())
        self._renderer.draw_border(self, with_title=False)
        button_text_y_pos = self._start_y + int(self._height / 2)
        self._renderer.draw_text(self, self._title, button_text_y_pos, centered=True, selected=self._selected)
        self._renderer.reset_cursor(self)
        self._renderer.unset_color_mode(self.get_color())

class InternalFileDialogErrorPopup:

    def __init__(self):
        pass


class FileDialogPopup(py_cui.popups.Popup):

    def __init__(self, root, initial_dir, title, dialog_type, ascii_icons, limit_extensions, color, renderer, logger):


        py_cui.popups.Popup.__init__(self, root, title, '', color, renderer, logger)
        #FileDialogImplementation.__init__(self, self._form_fields, required_fields, logger)
        self._filename_input = FileNameInput(self, 'Path', renderer, logger)
        self._file_dir_select = FileSelectElement(self, initial_dir, dialog_type, ascii_icons, title, color, None, renderer, logger)
        self._submit_button = FileDialogButton(self, 'Submit', self._submit_action, 1, '', 'Submit', renderer, logger)
        self._cancel_button = FileDialogButton(self, 'Cancel', self._root.close_popup, 2, '', 'Cancel', renderer, logger)
        self._internal_popup = None
        self.update_height_width()
        self._file_dir_select.set_selected(True)


    def _submit_action(self):
        pass


    def get_absolute_start_pos(self):
        """Override of base class, computes position based on root dimensions
        
        Returns
        -------
        start_x, start_y : int
            The coords of the upper-left corner of the popup
        """

        root_height, root_width = self._root.get_absolute_size()

        
        form_start_x = int(root_width / 6)
        
        form_start_y = int(root_height / 8)

        return form_start_x, form_start_y


    def get_absolute_stop_pos(self):
        """Override of base class, computes position based on root dimensions
        
        Returns
        -------
        stop_x, stop_y : int
            The coords of the lower-right corner of the popup
        """

        root_height, root_width = self._root.get_absolute_size()
        
        form_stop_x = int(5 * root_width / 6)
        
        form_stop_y = int(7 * root_height / 8)
        return form_stop_x, form_stop_y


    def update_height_width(self):
        """Override of base class function

        Also updates all form field elements in the form
        """

        super().update_height_width()
        try:
            self._file_dir_select.update_height_width()
            self._filename_input.update_height_width()
            self._submit_button.update_height_width()
            self._cancel_button.update_height_width()
        except AttributeError:
            pass


    def _handle_key_press(self, key_pressed):
        """Override of base class. Here, we handle tabs, enters, and escapes

        All other key presses are passed to the currently selected field element

        Parameters
        ----------
        key_pressed : int
            Key code of pressed key
        """

        if self._internal_popup is None:
            if key_pressed == py_cui.keys.KEY_TAB:
                if self._file_dir_select.is_selected():
                    self._form_fields[self.get_selected_form_index()].set_selected(False)
                    self.jump_to_next_field()
                    self._form_fields[self.get_selected_form_index()].set_selected(True)
                else:
                    self._form_fields[self.get_selected_form_index()].set_selected(False)
                    self.jump_to_next_field()
                    self._form_fields[self.get_selected_form_index()].set_selected(True)
            elif self._filename_input.is_selected() and key_pressed == py_cui.keys.KEY_ENTER:
                valid, err_msg = self.is_submission_valid()
                if valid:
                    self._root.close_popup()
                    self._on_submit_action(self.get())
                else:
                    self._internal_popup = InternalFormPopup(self,
                                                             self._root, 
                                                             err_msg, 
                                                             'Required fields: {}'.format(str(self._required_fields)),
                                                             py_cui.YELLOW_ON_BLACK, 
                                                             self._renderer, 
                                                             self._logger)
            elif key_pressed == py_cui.keys.KEY_ESCAPE:
                self._root.close_popup()
            else:
                if self._file_dir_select.is_selected():
                    self._file_dir_select._handle_key_press(key_pressed)
                elif self._filename_input.is_selected():
                    self._filename_input._handle_key_press(key_pressed)

        else:
            self._internal_popup._handle_key_press(key_pressed)


    def _handle_mouse_press(self, x, y):
        """Override of base class function

        Simply enters the appropriate field when mouse is pressed on it

        Parameters
        ----------
        x, y : int, int
            Coordinates of the mouse press
        """

        super()._handle_mouse_press(x, y)
        if self._file_dir_select._contains_position(x, y):
            self._filename_input.set_selected(False)
            self._file_dir_select.set_selected(True)
            self._file_dir_select._handle_mouse_press(x, y)
            
        elif self._filename_input._contains_position(x, y):
            self._filename_input.set_selected(True)
            self._file_dir_select.set_selected(False)
            self._filename_input._handle_mouse_press(x, y)
            


    def _draw(self):
        """Override of base class.
        
        Here, we only draw a border, and then the individual form elements
        """

        self._renderer.set_color_mode(self._color)
        self._renderer.set_color_rules([])
        self._renderer.draw_border(self)

        self._file_dir_select._draw()
        self._filename_input._draw()
        #self._submit_button._draw()
        #self._cancel_button._draw()

        if self._internal_popup is not None:
            self._internal_popup._draw()

#class FileDialogWidget
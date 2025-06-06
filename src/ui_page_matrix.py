''' Library providing program pages class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

_INITIAL_SUB_PAGE = const(0)

import main_loops as ml
from ui_pages import Page
from ui_blocks import TitleBar, MatrixCell, TextRow
from constants import EMPTY_OPTIONS_BLANK, TRIGGERS, TRIGGERS_SHORT, TRIGGERS_LONG, MULTI_LAYOUTS, LAYOUT_OPTIONS, TRIGGER_OPTIONS_SHORT

_NONE                    = const(-1)

_ENCODER_VAL             = const(1)

# _BUTTON_EVENT_PRESS      = const(1)
_BUTTON_EVENT_LONG_PRESS = const(2)

_MATRIX_ROWS             = const(8)
_MATRIX_COLUMNS          = const(8)

_TITLE_BAR_H             = const(14)
_SUB_PAGE_W              = const(204)
_TEXT_ROW_Y              = const(163)
_TEXT_ROW_H              = const(13)

_BACK_COLOR              = const(0xAA29) # 0x29AA dark purple blue
_FORE_COLOR              = const(0xD9CD) # 0xCDD9 light purple grey

_ALIGN_CENTRE            = const(1)

_SUB_PAGES               = const(1)
_SELECT_SUB_PAGE         = const(-1)
_FIRST_MATRIX_CELL       = const(0)

_POP_UP_SELECT           = const(1)
_POP_UP_CONFIRM          = const(3)
_POP_UP_MESSAGE          = const(4)
_POP_UP_MATRIX           = const(7)

_CONFIRM_REPLACE_CELL    = const(131) # must be last confirm ID

_DEFAULT_LAYOUT          = const(2)
_LAYOUT_ROWS_COL         = const(1)
_LAYOUT_COLS_COL         = const(2)
_LAYOUT_MAP_COL          = const(3)
_LAYOUT_MAP_COLS         = const(4)

class PageMatrix(Page):
    '''program page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, _SUB_PAGES, visible)
        self.sub_page = _INITIAL_SUB_PAGE
        self.row = 0
        self.column = 0
        self.active_cell = _NONE
        self.page_is_built = False
        self._build_page()

    def draw(self) -> None:
        '''draw whole page; called by self.restore, ui._callback_*, Page*._load and Page*._callback_*'''
        ml.ui.display.rect(0, _TITLE_BAR_H, _SUB_PAGE_W, _TEXT_ROW_Y - _TITLE_BAR_H, _BACK_COLOR, True) # type: ignore (temporary)
        super().draw()

    def program_change(self, update_only: bool) -> None:
        '''update page after program change; called by ui.program_change'''
        if self.visible:
            self._load()
        else:
            blocks = self.blocks
            if (selected_block := self.selected_block[self.sub_page]) != 0:
                blocks[selected_block].update(False, False)
                blocks[0].update(True, False)

    def encoder(self, encoder_id: int, value: int, page_select_mode: bool) -> bool:
        '''process encoder input at page level (ui.process_encoder > Page.encoder/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if page_select_mode:
            if len(self.sub_pages_blocks) > 1:
                self.callback_input(_SELECT_SUB_PAGE, value)
            return False
        if len(blocks := self.blocks) == 0:
            return False
        if encoder_id == _ENCODER_VAL: # left-right
            row = self.row
            self.column = (col := value)
        else: # encoder_id == _ENCODER_NAV # up-down
            self.row = (row := value)
            col = self.column
        new_selected_block = row * _MATRIX_COLUMNS + col
        if new_selected_block == (selected_block := self.selected_block[(sub_page := self.sub_page)]):
            return False
        blocks[selected_block].update(False)
        self.selected_block[sub_page] = new_selected_block
        blocks[new_selected_block].update(True)
        self._set_text_row()
        return True

    def button_sel_opt(self, press_state: int) -> bool:
        '''process select button press at page level; called by ui.process_user_input'''
        selected_block = self.selected_block[self.sub_page]
        if selected_block >= _FIRST_MATRIX_CELL and press_state == _BUTTON_EVENT_LONG_PRESS:
            ml.ui.pop_ups[_POP_UP_SELECT].open(self, selected_block, 'insert multipad layout:', LAYOUT_OPTIONS, _DEFAULT_LAYOUT,
                                               self._callback_select)
            return True
        return self.blocks[selected_block].button_sel_opt()

    def process_user_input(self, id: int, value: int|str = _NONE, button_del: bool = False, button_sel_opt: bool = False) -> bool:
        '''process user input at page level (ui.set_user_input_tuple > ui.user_input_tuple > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        value = int(value)
        sub_page = self.sub_page
        if id == _SELECT_SUB_PAGE:
            if button_del or button_sel_opt or value == _NONE or value == sub_page:
                return False
            self._set_sub_page(value)
            self._load()
            return True
        if button_del:
            if id >= _FIRST_MATRIX_CELL:
                row, col = divmod(id - _FIRST_MATRIX_CELL, _MATRIX_COLUMNS)
                if ml.router.trigger_matrix[row][col] == _NONE:
                    return False
                ml.ui.pop_ups[_POP_UP_CONFIRM].open(self, id, 'clear?', self._callback_confirm)
        elif button_sel_opt:
            if id >= _FIRST_MATRIX_CELL:
                row, col = divmod(id - _FIRST_MATRIX_CELL, _MATRIX_COLUMNS)
                _router = ml.router
                trigger = _router.trigger_matrix[row][col]
                zone = _router.trigger_zones[row][col]
                ml.ui.pop_ups[_POP_UP_MATRIX].open(self, id, trigger, zone, self._callback_matrix)
        return True

    def midi_learn(self, port: int, channel: int, trigger: int, zone: int, note: int, program: int, cc: int, cc_value: int) -> bool:
        '''process midi learn input, save settings and reload options; called by ui.process_midi_learn_data'''
        block = self.selected_block[(sub_page := self.sub_page)]
        if trigger == _NONE:
            return True
        else: # matrix cell
            _router = ml.router
            trigger_matrix = _router.trigger_matrix
            trigger_zones = _router.trigger_zones
            zones = TRIGGERS[trigger][2][0]
            triggers = TRIGGER_OPTIONS_SHORT
            n = 0
            for i in range(_MATRIX_ROWS):
                for j in range(_MATRIX_COLUMNS):
                    if trigger_matrix[i][j] == trigger:
                        if (zone_changed := trigger_zones[i][j] != zone):
                            trigger_zones[i][j] = zone
                            _router.input_zone = zone
                        blocks = self.blocks
                        new_selection_block = blocks[(new_selection := _FIRST_MATRIX_CELL + n)]
                        if (selected_block := self.selected_block[sub_page]) != (new_selection):
                            blocks[selected_block].update(False, False)
                            self.selected_block[sub_page] = new_selection
                            new_selection_block.update(True, False)
                        elif not zone_changed:
                            return True
                        new_selection_block.set_values(trigger, f'{triggers[trigger + 1]}{zones[zone]}')
                        ml.ui.set_trigger(trigger, zone)
                        return True
                    n +=1
            current_block = self.blocks[block]
            current_block.set_selection(zone, trigger + 1)
            current_block.draw()
            return True

    def _build_page(self) -> None:
        '''build page (without drawing it); called by self.__init__ and self._build_sub_page'''
        if (sub_page := self.sub_page) is None or self.page_is_built:
            return
        self.page_is_built = True
        _build_sub_page = self._build_sub_page
        sub_pages_title_bars = self.sub_pages_title_bars
        sub_pages_blocks = self.sub_pages_blocks
        sub_pages_empty_blocks = self.sub_pages_empty_blocks
        sub_pages_text_rows = self.sub_pages_text_rows
        title_bar, blocks, empty_blocks, text_row = _build_sub_page()
        sub_pages_title_bars.append(title_bar)
        sub_pages_blocks.append(blocks)
        sub_pages_empty_blocks.append(empty_blocks)
        sub_pages_text_rows.append(text_row)
        self._set_sub_page(sub_page)

    def _build_sub_page(self) -> tuple:
        '''build sub-page (without drawing it); called by self._build_page'''
        if not self.page_is_built:
            self._build_page()
            return None, [], []
        blocks = []
        empty_blocks = []
        selected_block = self.selected_block[self.sub_page]
        _callback_input = self.callback_input
        title_bar = TitleBar('trigger matrix', 1, _SUB_PAGES)
        n = 0
        for i in range(_MATRIX_ROWS):
            for j in range(_MATRIX_COLUMNS):
                blocks.append(MatrixCell(_FIRST_MATRIX_CELL + n, i, j, selected_block == _FIRST_MATRIX_CELL + n,
                                            callback_func=_callback_input))
                n += 1
        text_row = TextRow(_TEXT_ROW_Y, _TEXT_ROW_H, _BACK_COLOR, _FORE_COLOR, _ALIGN_CENTRE)
        return title_bar, blocks, empty_blocks, text_row

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change, Page*.process_user_input
        and PageProgram.set_trigger'''
        redraw &= ml.ui.active_pop_up is None
        self._set_matrix_page_options()
        if redraw:
            self._set_text_row(redraw=False)
            self.draw()

    def _initiate_nav_encoder(self, value: int = 0) -> None:
        '''initiate navigation encoder to select blocks; called by self._draw and self.set_page_encoders'''
        _ui = ml.ui
        _ui.encoder_nav.set(self.row, _MATRIX_ROWS - 1)
        _ui.encoder_val.set(self.column, _MATRIX_COLUMNS - 1)

    def _set_text_row(self, value: int|None = None, redraw: bool = True) -> None:
        '''draw text row with long description of currently selected block; called by self.encoder and self._load'''
        selection = self.selected_block[self.sub_page]
        if selection >= _FIRST_MATRIX_CELL:
            row, col = divmod(selection - _FIRST_MATRIX_CELL, _MATRIX_COLUMNS)
            _router = ml.router
            if (trigger := _router.trigger_matrix[row][col]) == _NONE:
                text = 'assign trigger'
            else:
                trigger_long_name = TRIGGERS_LONG[trigger]
                zone_name = TRIGGERS[trigger][2][1][_router.trigger_zones[row][col]]
                text = trigger_long_name if zone_name == '' else f'{trigger_long_name}: {zone_name}'
        self.text_row.set_text(text, redraw) # type: ignore

    def _set_matrix_page_options(self) -> None:
        '''load and set options and value to program name block on matrix sub-page; called by self._load'''
        _router = ml.router
        self._set_matrix_options(False)

    def _set_matrix_options(self, redraw: bool = True) -> None:
        '''load and set options and values to matrix cells on matrix sub-page; called by self.process_user_input,
        self._set_matrix_page_options and self._callback_confirm'''

        def check_straight(dv: int, dh: int) -> bool:
            nonlocal v_pos, h_pos
            if row + dv >= 0 and row + dv < _MATRIX_ROWS and col + dh >= 0 and col + dh < _MATRIX_COLUMNS:
                return trigger_matrix[(v_pos := row + dv)][(h_pos := col + dh)] != _NONE
            return False

        def check_diagonal(dv: int, dh: int) -> bool:
            nonlocal v_pos, h_pos
            reverse = dv < 0 and dh > 0 # up-right
            if not reverse and dh < 0 or reverse and dv < 0:
                min_d = -1
                step = -1
            else:
                min_d = 1
                step = 1
            max_d = dv if reverse else dh
            for d in range(min_d, max_d, step):
                if reverse:
                    v = row + d
                    h = col + dh
                else:
                    v = row + dv
                    h = col - dv
                if v >= 0 and v < _MATRIX_ROWS and h >= 0 and h < _MATRIX_COLUMNS:
                    if trigger_matrix[(v_pos := v)][(h_pos := h)] != _NONE:
                        return True
                if reverse:
                    v = row + dv
                    h = col - dv
                else:
                    v = row + d
                    h = col + dh
                if v >= 0 and v < _MATRIX_ROWS and h >= 0 and h < _MATRIX_COLUMNS:
                    if trigger_matrix[(v_pos := v)][(h_pos := h)] != _NONE:
                        return True
            # corner
            v = row + dv
            h = col + dh
            if v >= 0 and v < _MATRIX_ROWS and h >= 0 and h < _MATRIX_COLUMNS:
                return trigger_matrix[(v_pos := v)][(h_pos := h)] != _NONE
            return False
        # find active cell (i.e. cell with selected trigger) if unknown and if necessary change the selected trigger to one which is mapped
        _router = ml.router
        trigger_matrix = _router.trigger_matrix
        triggers_short = TRIGGERS_SHORT
        new_trigger = (current_trigger := _router.input_trigger)
        found = (active_cell := self.active_cell) != _NONE
        while self.active_cell == _NONE:
            n = 0
            for i in range(_MATRIX_ROWS):
                for j in range(_MATRIX_COLUMNS):
                    if trigger_matrix[i][j] == new_trigger:
                        self.active_cell = n
                        found = True
                        break
                    n += 1
            if found:
                break
            else:
                new_trigger += 1
                if new_trigger == len(triggers_short): # jump to beginning of list if last item is reached
                    new_trigger = 0
                if new_trigger == current_trigger:
                    new_trigger = _NONE
                    break
        if found:
            if active_cell != self.active_cell:
                _router.input_trigger = new_trigger
            # if the cell with the active trigger is cleared: select the closest one
            if active_cell != _NONE:
                row, col = divmod(active_cell, _MATRIX_COLUMNS)
                if trigger_matrix[row][col] == _NONE:
                    found = False
                    v_pos = _NONE
                    h_pos = _NONE
                    r = 1
                    while row - r >= 0 and col - r >= 0 and row + r < _MATRIX_ROWS and col + r < _MATRIX_COLUMNS:
                        if check_straight(0, -r):  # check left
                            found = True
                            break
                        if check_straight(-r, 0):  # check up
                            found = True
                            break
                        if check_diagonal(-r, -r): # check left-up
                            found = True
                            break
                        if check_straight(0, r):   # check right
                            found = True
                            break
                        if check_diagonal(r, -r):  # check up-right
                            found = True
                            break
                        if check_straight(r, 0):   # check down
                            found = True
                            break
                        if check_diagonal(r, -r):  # check left-down
                            found = True
                            break
                        if check_diagonal(r, r):   # check right-down
                            found = True
                            break
                        r += 1
                    if found:
                        self.active_cell = _FIRST_MATRIX_CELL + v_pos * _MATRIX_COLUMNS + h_pos
                        _router.input_trigger = trigger_matrix[v_pos][h_pos]
        # set trigger options
        trigger_defs = TRIGGERS
        trigger_zones = _router.trigger_zones
        blocks = self.blocks
        triggers = TRIGGER_OPTIONS_SHORT
        n = 0
        for i in range(_MATRIX_ROWS):
            for j in range(_MATRIX_COLUMNS):
                if (trigger := trigger_matrix[i][j]) == _NONE:
                    zones = EMPTY_OPTIONS_BLANK
                    zone = 0
                else:
                    zones = trigger_defs[trigger][2][0]
                    zone = trigger_zones[i][j]
                blocks[_FIRST_MATRIX_CELL + n].set_values(trigger, f'{triggers[trigger + 1]}{zones[zone]}', False)
                n += 1
        if redraw:
            for i in range(_MATRIX_ROWS * _MATRIX_COLUMNS):
                blocks[_FIRST_MATRIX_CELL + i].draw()

    def _save_matrix_settings(self) -> bool:
        '''save values from cells on the matrix sub-page; called by self._callback_confirm, self._callback_matrix and
        self._assign_multipad'''
        _data = ml.data
        _router = ml.router
        _router.handshake() # request second thread to wait
        router_trigger_matrix = _router.trigger_matrix
        data_trigger_matrix = _data.trigger_matrix
        changed = False
        for i in range(_MATRIX_ROWS):
            for j in range(_MATRIX_COLUMNS):
                if data_trigger_matrix[i][j] != (router_trigger := router_trigger_matrix[i][j]):
                    changed = True
                    data_trigger_matrix[i][j] = router_trigger # type: ignore
        if changed:
            _data.save_data_json_file()
            _router.update(already_waiting=True)
        else:
            _router.resume() # resume second thread
        return changed

    def _callback_confirm(self, caller_id: int, confirm: bool) -> None:
        '''callback for confirm pop-up; called (passed on) by self.process_user_input, self._callback_confirm and self._callback_menu'''
        if not confirm:
            return
        if caller_id >= _CONFIRM_REPLACE_CELL:
            row, col = divmod(caller_id - _CONFIRM_REPLACE_CELL - _FIRST_MATRIX_CELL, _MATRIX_COLUMNS)
            self._assign_multipad(row, col, self.layout_pos)
        elif caller_id >= _FIRST_MATRIX_CELL:
            row, col = divmod(caller_id - _FIRST_MATRIX_CELL, _MATRIX_COLUMNS)
            _router = ml.router
            _router.trigger_matrix[row][col] = -1
            _router.trigger_zones[row][col] = 0
            self._set_matrix_options()
            self._save_matrix_settings()

    def _callback_select(self, caller_id: int, selection: int) -> None:
        '''callback for select pop-up; called (passed on) by self.process_user_input'''
        layouts = MULTI_LAYOUTS
        rows = layouts[(layout_pos := selection * _LAYOUT_MAP_COLS) + _LAYOUT_ROWS_COL]
        cols = layouts[layout_pos + _LAYOUT_COLS_COL]
        row, col = divmod(caller_id - _FIRST_MATRIX_CELL, _MATRIX_COLUMNS)
        if _MATRIX_ROWS - row < rows or _MATRIX_COLUMNS - col < cols: # type: ignore
            ml.ui.pop_ups[_POP_UP_MESSAGE].open(self, f'requires {rows} down /{cols} right')
            return
        map = layouts[layout_pos + _LAYOUT_MAP_COL]
        trigger_matrix = ml.router.trigger_matrix
        triggers_short = TRIGGERS_SHORT
        # blocks = self.blocks
        for layout_row in range(rows): # type: ignore
            for layout_col in range (cols): # type: ignore
                if map[layout_row][layout_col] == _NONE: # type: ignore
                    continue
                if (trigger := trigger_matrix[row + layout_row][col + layout_col]) == _NONE:
                    continue
                if triggers_short[trigger][0] != 'M':
                    self.layout_pos = layout_pos
                    ml.ui.pop_ups[_POP_UP_CONFIRM].open(self, _CONFIRM_REPLACE_CELL + caller_id, 'replace?', self._callback_confirm)
                    return
        self._assign_multipad(row, col, layout_pos)

    def _callback_matrix(self, caller_id: int, trigger: int, zone: int) -> None:
        '''callback for trigger/zone select pop-up; called (passed on) by self.process_user_input'''
        row, col = divmod(caller_id - _FIRST_MATRIX_CELL, _MATRIX_COLUMNS)
        _router = ml.router
        trigger_matrix = _router.trigger_matrix
        trigger_zones = _router.trigger_zones
        _router.trigger_zones[row][col] = zone
        if trigger != trigger_matrix[row][col]:
            trigger_matrix[row][col] = trigger
            trigger_zones[row][col] = 0
            found = False
            for i in range(_MATRIX_ROWS):
                for j in range(_MATRIX_COLUMNS):
                    if i == row and j == col:
                        continue
                    if trigger_matrix[i][j] == trigger:
                        trigger_matrix[i][j] = _NONE
                        trigger_zones[i][j] = 0
                        found = True
                        break
                if found:
                    break
        self._save_matrix_settings()
        ml.ui.set_trigger(trigger, zone)

    def _assign_multipad(self, row, col, layout_pos):
        '''assign multipad layout to matrix; called by self._callback_confirm and self._callback_select'''
        layouts = MULTI_LAYOUTS
        map = layouts[layout_pos + _LAYOUT_MAP_COL]
        trigger_matrix = ml.router.trigger_matrix
        triggers_short = TRIGGERS_SHORT
        for i in range(_MATRIX_ROWS):
            for j in range(_MATRIX_COLUMNS):
                if triggers_short[trigger_matrix[i][j]][0] == 'M':
                    trigger_matrix[i][j] = _NONE
        first_pad = TRIGGERS_SHORT.index('M1')
        for layout_row in range(layouts[layout_pos + _LAYOUT_ROWS_COL]):
            for layout_col in range(layouts[layout_pos + _LAYOUT_COLS_COL]):
                if (trigger := map[layout_row][layout_col]) == _NONE:
                    continue
                trigger_matrix[row + layout_row][col + layout_col] = first_pad + trigger
        self._set_matrix_options()
        self._save_matrix_settings()
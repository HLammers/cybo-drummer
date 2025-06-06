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
from data_types import GenOptions
from ui_pages import Page
from ui_blocks import TitleBar, CheckBoxBlock, SelectBlock, TextBlock, MatrixCell, TextRow, EmptyRow
from constants import DEFAULT_PROGRAM_NAME, EMPTY_OPTIONS_BLANK, EMPTY_OPTIONS_3, EMPTY_OPTIONS_4, TRIGGERS, TRIGGERS_SHORT, TRIGGERS_LONG, \
    CONTEXT_MENU_ITEMS, NOTE_OPTIONS, NOTE_OFF_OPTIONS_W, TRANSIENT_OPTIONS, LAYER_OPTIONS_WO, PC_OPTIONS, BANK_OPTIONS, TEXT_ROWS_PROGRAM

_NONE                  = const(-1)
_NOTE_OFF_OFF          = const(-1)

_ASCII_A               = const(65)

_ENCODER_VAL           = const(1)

_NR_ROUTING_LAYERS     = const(4)
_NR_OUT_PORTS          = const(6)

_TEXT_ROW_Y            = const(163)
_TEXT_ROW_H            = const(13)

_BACK_COLOR            = const(0xAA29) # 0x29AA dark purple blue
_FORE_COLOR            = const(0xD9CD) # 0xCDD9 light purple grey

_ALIGN_CENTRE          = const(1)

_MAX_LABEL_LENGTH      = const(33)

_SUB_PAGES             = const(3)
_SUB_PAGE_MAPPING      = const(0)
_SUB_PAGE_NOTE         = const(1)
_SUB_PAGE_PC           = const(2)
_SELECT_SUB_PAGE       = const(-1)
_NAME                  = const(0)
_INPUT_TRIGGER         = const(1)
_FIRST_OUTPUT_PORT     = const(2)
_FIRST_VOICE           = const(3)
_FIRST_NOTE            = const(2)
_FIRST_NOTE_OFF        = const(3)
_FIRST_TRANSIENT       = const(4)
_FIRST_LAYER           = const(5)
_FIRST_SCALING         = const(6)
_FIRST_PC              = const(0)
_FIRST_BANK_MSB        = const(1)
_FIRST_BANK_LSB        = const(2)

_MAPPING_PORT_COL      = const(0)
_MAPPING_VOICE_COL     = const(1)
_MAPPING_NOTE_COL      = const(2)
_MAPPING_NOTE_OFF_COL  = const(3)
_MAPPING_TRANSIENT_COL = const(4)
_MAPPING_LAYER_COL     = const(5)
_MAPPING_SCALING_COL   = const(6)
_DISPLAY_NOTE_COL      = const(0)
_DISPLAY_NOTE_OFF_COL  = const(1)
_DISPLAY_TRANSIENT_COL = const(2)
_DISPLAY_LAYER_COL     = const(3)
_DISPLAY_SCALING_COL   = const(4)

_POP_UP_TEXT_EDIT      = const(0)
_POP_UP_MENU           = const(2)
_POP_UP_CONFIRM        = const(3)
_POP_UP_PROGRAM        = const(5)
_POP_UP_TRIGGER        = const(6)

_RENAME                = const(0)
_MOVE_BACKWARD         = const(1)
_MOVE_FORWARD          = const(2)
# _MOVE_TO               = const(3)

_CC_BANK_MSB           = const(0x00)
_CC_BANK_LSB           = const(0x20)

class PageProgram(Page):
    '''program page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, _SUB_PAGES, visible)
        self.sub_page = _INITIAL_SUB_PAGE
        self.mapping_settings = [[_NONE, _NONE, _NONE, _NOTE_OFF_OFF, _NONE, 0, True] for _ in range(_NR_ROUTING_LAYERS)]
        self.pc_settings = [[_NONE, _NONE, _NONE] for _ in range(_NR_OUT_PORTS)]
        self.device_options = GenOptions(_NR_OUT_PORTS + 1, first_options=EMPTY_OPTIONS_4, func=self._device_options)
        self.page_is_built = False
        self._build_page()

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
        if super().encoder(encoder_id, value, page_select_mode):
            if encoder_id == _ENCODER_VAL:
                self._set_text_row(value)
            else:
                self._set_text_row()
            return True
        return False

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
        if sub_page == _SUB_PAGE_MAPPING or sub_page == _SUB_PAGE_NOTE:
            if button_del:
                if id == _NAME:
                    ml.ui.pop_ups[_POP_UP_CONFIRM].open(self, _NAME, 'delete?', self._callback_confirm)
            elif button_sel_opt:
                if id == _NAME:
                    ml.ui.pop_ups[_POP_UP_MENU].open(self, CONTEXT_MENU_ITEMS, callback_func=self._callback_menu)
                elif id == _INPUT_TRIGGER:
                    ml.ui.pop_ups[_POP_UP_TRIGGER].open(self, _NONE, self._callback_trigger)
            elif value != _NONE:
                _router = ml.router
                if id == _NAME:
                    if _router.active_program == value:
                        return False
                    if _router.program_changed:
                        ml.ui.save_program(_router.active_bank, value)
                    else:
                        _router.update(program_number=value)
                elif sub_page == _SUB_PAGE_MAPPING:
                    row, col = divmod(id - _FIRST_OUTPUT_PORT, 2)
                    settings = self.mapping_settings
                    settings[row][col] = value - 1 # 0 becomes _NONE
                    if col == _MAPPING_PORT_COL:
                        settings[row][_MAPPING_VOICE_COL] = _NONE
                        settings[row][_MAPPING_NOTE_COL] = _NONE
                        settings[row][_MAPPING_NOTE_OFF_COL] = _NOTE_OFF_OFF
                        settings[row][_MAPPING_TRANSIENT_COL] = _NONE
                        settings[row][_MAPPING_LAYER_COL] = 0
                        settings[row][_MAPPING_SCALING_COL] = True
                    if self._save_mapping_settings():
                        self._set_voice_options()
                else: # sub_page == _SUB_PAGE_NOTE
                    row, col = divmod(id - _FIRST_NOTE, 5)
                    settings = self.mapping_settings
                    if settings[row][_MAPPING_VOICE_COL] == _NONE:
                        return False
                    if col == _DISPLAY_NOTE_COL:
                        settings[row][_MAPPING_NOTE_COL] = value - 1 # 0 becomes _NONE
                    elif col == _DISPLAY_NOTE_OFF_COL:
                        settings[row][_MAPPING_NOTE_OFF_COL] = value - 1 # 0 becomes _NONE
                    elif col == _DISPLAY_TRANSIENT_COL:
                        settings[row][_MAPPING_TRANSIENT_COL] = value - 1 # 0 becomes _NONE
                    elif col == _DISPLAY_LAYER_COL:
                        settings[row][_MAPPING_LAYER_COL] = value
                    else: # col == _DISPLAY_SCALE_COL
                        settings[row][_MAPPING_SCALING_COL] = bool(value)
                    if self._save_mapping_settings():
                        self._set_note_options()
        else: # sub_page == _SUB_PAGE_PC
            if button_del or button_sel_opt or value == _NONE:
                return False
            row, col = divmod(id - _FIRST_PC, 3)
            self.pc_settings[row][col] = value - 1 # 0 becomes _NONE
            self._save_pc_settings()
        return True

    def set_trigger(self) -> None:
        '''set active trigger (triggered by trigger button) at page level; called by ui.set_trigger (also calling router.set_trigger)'''
        sub_page = self.sub_page
        if sub_page == _SUB_PAGE_MAPPING or sub_page == _SUB_PAGE_NOTE:
            self._load()

    def midi_learn(self, port: int, channel: int, trigger: int, zone: int, note: int, program: int, cc: int, cc_value: int) -> bool:
        '''process midi learn input, save settings and reload options; called by ui.process_midi_learn_data'''
        block = self.selected_block[(sub_page := self.sub_page)]
        if sub_page == _SUB_PAGE_MAPPING or sub_page == _SUB_PAGE_NOTE:
            if block == _NAME:
                return False
            elif block == _INPUT_TRIGGER:
                if trigger == _NONE:
                    return False
                trigger_long = TRIGGERS_LONG[trigger]
                zone_name = TRIGGERS[trigger][2][1][zone]
                text = trigger_long if zone_name == '' else f'{trigger_long}   {zone_name}'
                self.blocks[_INPUT_TRIGGER].set_value(text, False)
                ml.ui.set_trigger(trigger, zone)
                return True
            elif sub_page == _SUB_PAGE_NOTE and note != _NONE and block - _FIRST_NOTE % 5 == 0:
                if note == _NONE:
                    return False
                value = note + 1 # _NONE becomes 0
        else: # sub_page == _SUB_PAGE_PC
            if (col := (block - _FIRST_PC) % 3) == 0:
                if program == _NONE:
                    return False
                value = program
            else:
                if cc_value == _NONE or not (col == 1 and cc == _CC_BANK_MSB or col == 2 and cc == _CC_BANK_LSB):
                    return False
                value = cc_value
        return self.blocks[block].set_selection(value)

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
        for i in range(_SUB_PAGES):
            title_bar, blocks, empty_blocks, text_row = _build_sub_page(i)
            sub_pages_title_bars.append(title_bar)
            sub_pages_blocks.append(blocks)
            sub_pages_empty_blocks.append(empty_blocks)
            sub_pages_text_rows.append(text_row)
        self._set_sub_page(sub_page)

    def _build_sub_page(self, sub_page: int) -> tuple:
        '''build sub-page (without drawing it); called by self._build_page'''
        if not self.page_is_built:
            self._build_page()
            return None, [], []
        blocks = []
        empty_blocks = []
        selected_block = self.selected_block[sub_page]
        _callback_input = self.callback_input
        if sub_page == _SUB_PAGE_MAPPING or sub_page == _SUB_PAGE_NOTE:
            if sub_page == _SUB_PAGE_MAPPING:
                title_bar = TitleBar('program: mapping voices', 1, _SUB_PAGES)
            else: # sub_page == _SUB_PAGE_NOTE
                title_bar = TitleBar('program: mapping note', 2, _SUB_PAGES)
            blocks.append(SelectBlock(_NAME, 0, 0, 1, 1, selected_block == _NAME, 'program', callback_func=_callback_input))
            blocks.append(TextBlock(_INPUT_TRIGGER, 1, 0, 1, 1, selected_block == _INPUT_TRIGGER, 'input trigger', add_line=True,
                                    callback_func=_callback_input))
            if sub_page == _SUB_PAGE_MAPPING:
                for i in range(_NR_ROUTING_LAYERS):
                    blocks.append(SelectBlock(_FIRST_OUTPUT_PORT + 2 * i, 2 + i, 0, 1, 2, selected_block == _FIRST_OUTPUT_PORT + 2 * i,
                                              f'{chr(_ASCII_A + i)}: port/device', default_selection=0, callback_func=_callback_input))
                    blocks.append(SelectBlock(_FIRST_VOICE + 2 * i, 2 + i, 1, 1, 2, selected_block == _FIRST_VOICE + 2 * i, 'voice',
                                              callback_func=_callback_input))
            else: # sub_page == _SUB_PAGE_NOTE
                for i in range(_NR_ROUTING_LAYERS):
                    blocks.append(SelectBlock(_FIRST_NOTE + 5 * i, 2 + i, 0, 3, 12, selected_block == _FIRST_NOTE + 5 * i,
                                              default_selection=0, callback_func=_callback_input))
                    blocks.append(SelectBlock(_FIRST_NOTE_OFF + 5 * i, 2 + i, 3, 3, 12, selected_block == _FIRST_NOTE_OFF + 5 * i,
                                              default_selection=0, callback_func=_callback_input))
                    blocks.append(SelectBlock(_FIRST_TRANSIENT + 5 * i, 2 + i, 6, 2, 12, selected_block == _FIRST_TRANSIENT + 5 * i,
                                              default_selection=0, callback_func=_callback_input))
                    blocks.append(SelectBlock(_FIRST_LAYER + 5 * i, 2 + i, 8, 2, 12, selected_block == _FIRST_LAYER + 5 * i,
                                              callback_func=_callback_input))
                    blocks.append(CheckBoxBlock(_FIRST_SCALING + 5 * i, 2 + i, 10, 2, 12, selected_block == _FIRST_SCALING + 5 * i,
                                              default_selection=True, callback_func=_callback_input))
        else: #sub_page == _SUB_PAGE_PC
            title_bar = TitleBar('program: pc/bank select', 3, _SUB_PAGES)
            for i in range(_NR_OUT_PORTS):
                blocks.append(SelectBlock(_FIRST_PC + i, i, 0, 1, 3, selected_block == _FIRST_PC + i, f'p{i + 1}: pc', PC_OPTIONS,
                                          default_selection=0, callback_func=_callback_input))
                blocks.append(SelectBlock(_FIRST_BANK_MSB + 2 * i, i, 1, 1, 3, selected_block == _FIRST_BANK_MSB + 2 * i, 'bank msb',
                                          BANK_OPTIONS, default_selection=0, callback_func=_callback_input))
                blocks.append(SelectBlock(_FIRST_BANK_LSB + 2 * i, i, 2, 1, 3, selected_block == _FIRST_BANK_LSB + 2 * i, 'bank lsb',
                                          BANK_OPTIONS, default_selection=0, callback_func=_callback_input))
        text_row = TextRow(_TEXT_ROW_Y, _TEXT_ROW_H, _BACK_COLOR, _FORE_COLOR, _ALIGN_CENTRE)
        return title_bar, blocks, empty_blocks, text_row

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change, Page*.process_user_input
        and PageProgram.set_trigger'''
        redraw &= ml.ui.active_pop_up is None
        self._set_mapping_options()
        self._set_pc_options()
        if redraw:
            self._set_text_row(redraw=False)
            self.draw()

    def _set_text_row(self, value: int|None = None, redraw: bool = True) -> None:
        '''draw text row with long description of currently selected block; called by self.encoder and self._load'''
        selection = self.selected_block[(sub_page := self.sub_page)]
        if sub_page == _SUB_PAGE_MAPPING:
            if selection == _NAME:
                text = TEXT_ROWS_PROGRAM[_SUB_PAGE_MAPPING][_NAME]
                if ml.router.program_changed:
                    text += ' [not saved]'
            elif selection == _INPUT_TRIGGER:
                text = TEXT_ROWS_PROGRAM[_SUB_PAGE_MAPPING][_INPUT_TRIGGER]
            else:
                row, col = divmod(selection - _FIRST_OUTPUT_PORT, 2)
                text = f'layer {chr(_ASCII_A + row)}: output port/device' if col == 0 else f'layer {chr(_ASCII_A + row)}: output voice'
        elif sub_page == _SUB_PAGE_NOTE:
            if selection == _NAME:
                text = TEXT_ROWS_PROGRAM[_SUB_PAGE_MAPPING][_NAME]
                if ml.router.program_changed:
                    text += ' [not saved]'
            elif selection == _INPUT_TRIGGER:
                text = TEXT_ROWS_PROGRAM[_SUB_PAGE_MAPPING][_INPUT_TRIGGER]
            else:
                settings = self.mapping_settings
                row, col = divmod(selection - _FIRST_NOTE, 5)
                if col == _DISPLAY_TRANSIENT_COL:
                    if value is None:
                        value = settings[row][_MAPPING_TRANSIENT_COL] + 1
                    text = TRANSIENT_OPTIONS[1][value] # type: ignore
                elif col == _DISPLAY_LAYER_COL:
                    if value is None:
                        value = settings[row][_MAPPING_LAYER_COL] + 1
                    text = 'low input velocity' if value == 0 else 'high input velocity'
                elif col == _DISPLAY_SCALING_COL:
                    value = settings[row][_MAPPING_SCALING_COL] if value is None else bool(value)
                    text = 'output velocity range increased' if value else 'output velocity could be limited'
                else:
                    setting = settings[row]
                    port = setting[_MAPPING_PORT_COL] if value is None or col != _MAPPING_PORT_COL else value
                    output_mapping = ml.data.output_mapping
                    if port == _NONE:
                        device = 'n/a'
                        voice = 'n/a'
                    else:
                        voice = setting[_MAPPING_VOICE_COL] if value is None or col != _MAPPING_VOICE_COL else value
                        if (device := output_mapping[2 * port]) == '':
                            device = f'[port {port + 1}]'
                        voice = 'n/a' if voice == _NONE else output_mapping[2 * port + 1]['mapping'][2 * voice]
                    text = f'layer {chr(_ASCII_A + row)}: {device[0:_MAX_LABEL_LENGTH - len(voice) - 11]} - {voice}'
        else: # sub_page == _SUB_PAGE_PC
            row, col = divmod(selection - _FIRST_PC, 3)
            device = ml.data.output_mapping[2 * row]
            if col == 0:
                text = f'port {row + 1}: program change' if device == '' else f'{device[0:_MAX_LABEL_LENGTH - 16]}: program change'
            elif col == 1:
                text = f'port {row + 1}: bank select msb' if device == '' else f'{device[0:_MAX_LABEL_LENGTH - 17]}: bank select msb'
            else:
                text = f'port {row + 1}: bank select lsb' if device == '' else f'{device[0:_MAX_LABEL_LENGTH - 17]}: bank select lsb'
        self.text_row.set_text(text, redraw) # type: ignore

    def _set_mapping_options(self) -> None:
        '''load and set options and values to input blocks on mapping sub-pages; called by self._load'''
        sub_page = self.sub_page
        if not (sub_page == _SUB_PAGE_MAPPING or sub_page == _SUB_PAGE_NOTE):
            return
        self.mapping_settings = (settings := [[_NONE, _NONE, _NONE, _NOTE_OFF_OFF, _NONE, 0, True] for _ in range(_NR_ROUTING_LAYERS)])
        blocks = self.blocks
        _router = ml.router
        blocks[_NAME].set_options(GenOptions(100, func=_router.program_options), ml.router.active_program, redraw=False)
        trigger_long = TRIGGERS_LONG[(input_trigger := _router.input_trigger)]
        zone_name = TRIGGERS[input_trigger][2][1][(zone := _router.input_zone)]
        text = trigger_long if zone_name == '' else f'{trigger_long}   {zone_name}'
        blocks[_INPUT_TRIGGER].set_value(text, False)
        if len(routing := _router.routing) > 0:
            trigger_short = TRIGGERS_SHORT[input_trigger]
            output_mapping = ml.data.output_mapping
            for route in routing:
                if route['trigger'] == trigger_short and route['zone'] == zone:
                    layers = route['layers']
                    for i in range(4):
                        if (ch := chr(_ASCII_A + i)) in layers:
                            layer = layers[ch]
                            voice = output_mapping[2 * (port := layer['output_port']) + 1]['mapping'].index(layer['voice']) // 2
                            settings[i] = [port, voice, layer['note'], layer['note_off'], layer['transient'], layer['transient_layer'],
                                           layer['scale']]
        if sub_page == _SUB_PAGE_MAPPING:
            self._set_voice_options(False)
        else: # sub_page == _SUB_PAGE_NOTE
            self._set_note_options(False)

    def _set_voice_options(self, redraw: bool = True) -> None:
        '''load and set options and values to voice selection blocks on the mapping sub-page; called by self.process_user_input and
        self._set_mapping_options'''
        if self.sub_page != _SUB_PAGE_MAPPING:
            return
        output_mapping = ml.data.output_mapping
        blocks = self.blocks
        for i, setting in enumerate(self.mapping_settings):
            block = blocks[_FIRST_OUTPUT_PORT + 2 * i]
            block.set_options(self.device_options, (port := setting[_MAPPING_PORT_COL]) + 1, 0, redraw) # _NONE becomes 0
            voices = GenOptions(len(output_mapping[2 * port + 1]['mapping']) // 2 + 1, first_options=EMPTY_OPTIONS_4,
                                func=lambda i, p: output_mapping[2 * p + 1]['mapping'][2 * i], argument=port)
            block = blocks[_FIRST_VOICE + 2 * i]
            block.set_options(voices, setting[_MAPPING_VOICE_COL] + 1, 0, redraw) # _NONE becomes 0

    def _set_note_options(self, redraw: bool = True) -> None:
        '''load and set options and values to note blocks on the mapping note sub-page; called by self.process_user_input and
        self._set_mapping_options'''
        if self.sub_page != _SUB_PAGE_NOTE:
            return
        blocks = self.blocks
        for i, setting in enumerate(self.mapping_settings):
            if setting[_MAPPING_PORT_COL] == _NONE or setting[_MAPPING_VOICE_COL] == _NONE:
                block = blocks[_FIRST_NOTE + 5 * i]
                block.enable(False, redraw=False)
                block.set_label(f'{chr(_ASCII_A + i)}      ', False)
                block.set_options(EMPTY_OPTIONS_BLANK, redraw=redraw)
                block = blocks[_FIRST_NOTE_OFF + 5 * i]
                block.enable(False, redraw=False)
                block.set_label('', False)
                block.set_options(EMPTY_OPTIONS_BLANK, redraw=redraw)
                block = blocks[_FIRST_TRANSIENT + 5 * i]
                block.enable(False, redraw=False)
                block.set_label('', False)
                block.set_options(EMPTY_OPTIONS_BLANK, redraw=redraw)
                block = blocks[_FIRST_LAYER + 5 * i]
                block.enable(False, redraw=False)
                block.set_label('', False)
                block.set_options(EMPTY_OPTIONS_BLANK, redraw=redraw)
                block = blocks[_FIRST_SCALING + 5 * i]
                block.enable(False, redraw=False)
                block.set_label('', redraw)
                continue
            block = blocks[_FIRST_NOTE + 5 * i]
            block.enable(True, redraw=False)
            block.set_label(f'{chr(_ASCII_A + i)}: note', False)
            block.set_options(NOTE_OPTIONS, setting[_MAPPING_NOTE_COL] + 1, 0, redraw) # _NONE becomes 0
            block = blocks[_FIRST_NOTE_OFF + 5 * i]
            block.enable(True, redraw=False)
            block.set_label('note off', False)
            block.set_options(NOTE_OFF_OPTIONS_W, setting[_MAPPING_NOTE_OFF_COL] + 1, 0, redraw) # _NONE becomes 0
            block = blocks[_FIRST_TRANSIENT + 5 * i]
            block.enable(True, redraw=False)
            block.set_label('trans', False)
            block.set_options(TRANSIENT_OPTIONS[0], (transient := setting[_MAPPING_TRANSIENT_COL]) + 1, 0, redraw) # _NONE becomes 0
            if transient == _NONE:
                block = blocks[_FIRST_LAYER + 5 * i]
                block.enable(False, redraw=False)
                block.set_label('', False)
                block.set_options(EMPTY_OPTIONS_BLANK, redraw=redraw)
                block = blocks[_FIRST_SCALING + 5 * i]
                block.enable(False, redraw=False)
                block.set_label('', redraw)
            else:
                block = blocks[_FIRST_LAYER + 5 * i]
                block.enable(True, redraw=False)
                block.set_label('lo/hi', False)
                block.set_options(LAYER_OPTIONS_WO, setting[_MAPPING_LAYER_COL], 0, redraw)
                block = blocks[_FIRST_SCALING + 5 * i]
                block.enable(True, redraw=False)
                block.set_label('scale', False)
                block.set_checked(setting[_MAPPING_SCALING_COL], redraw=redraw)

    def _set_pc_options(self) -> None:
        '''load and set options and values to input blocks on the program change sub-page; called by self._load'''
        if self.sub_page != _SUB_PAGE_PC:
            return
        _router = ml.router
        settings = self.pc_settings
        for i in range(_NR_OUT_PORTS):
            settings[i][0] = _NONE
            settings[i][1] = _NONE
            settings[i][2] = _NONE
        for port, value in _router.program['program_change']:
            settings[port][0] = value
        for port, bank in _router.program['bank_select']:
            settings[port][1] = bank[0]
            settings[port][2] = bank[1]
        output_mapping = ml.data.output_mapping
        blocks = self.blocks
        for port, pc_and_bank in enumerate(settings):
            options = EMPTY_OPTIONS_3 if output_mapping[2 * port] == '' else PC_OPTIONS
            blocks[_FIRST_PC + 3 * port].set_options(options, pc_and_bank[0] + 1, 0, False) # _NONE becomes 0
            options = EMPTY_OPTIONS_3 if output_mapping[2 * port] == '' else BANK_OPTIONS
            blocks[_FIRST_BANK_MSB + 3 * port].set_options(options, pc_and_bank[1] + 1, 0, False) # _NONE becomes 0
            blocks[_FIRST_BANK_LSB + 3 * port].set_options(options, pc_and_bank[2] + 1, 0, False) # _NONE becomes 0

    def _save_mapping_settings(self) -> bool:
        '''save values from input blocks on the mapping sub-pages; called by self.process_user_input'''
        _ml = ml
        _router = _ml.router
        _router.handshake() # request second thread to wait
        trigger_short = TRIGGERS_SHORT[_router.input_trigger]
        zone = _router.input_zone
        output_mapping = ml.data.output_mapping
        changed = False
        found = False
        for route in (routing := _router.routing):
            if route['trigger'] == trigger_short and route['zone'] == zone:
                layers = route['layers']
                found = True
                break
        if not found:
            layers = {}
            routing.append({'trigger': trigger_short, 'zone': zone, 'layers': layers})
            changed = True
        for i, (port, voice, note, note_off, transient, transient_layer, scaling) in enumerate(settings := self.mapping_settings):
            # skip if a port/device is assigned but no voice yet (so it will not save, but it will also not remove the line)
            if port != _NONE and voice == _NONE:
                _router.resume() # resume second thread
                return True
            elif port == _NONE or voice == _NONE:
                if (ch := chr(_ASCII_A + i)) in layers:
                    del layers[ch]
                    changed = True
                setting = [_NONE, _NONE, _NONE, _NOTE_OFF_OFF, _NONE, 0, True]
                if settings[i] != setting:
                    settings[i] = [_NONE, _NONE, _NONE, _NOTE_OFF_OFF, _NONE, 0, True]
                    changed = True
            else:
                skip = False
                for j, setting in enumerate(settings):
                    if i == j or port != setting[_MAPPING_PORT_COL]:
                        continue
                    if voice == setting[_MAPPING_VOICE_COL]:
                        skip = True
                        break
                if skip:
                    _router.resume() # resume second thread
                    return False
                voice_name = output_mapping[2 * port + 1]['mapping'][2 * voice]
                if (ch := chr(_ASCII_A + i)) in layers:
                    layer = layers[ch]
                    if layer['output_port'] != port:
                        layer['output_port'] = port
                        changed = True
                    if layer['voice'] != voice_name:
                        layer['voice'] = voice_name
                        changed = True 
                    if layer['note'] != note:
                        layer['note'] = note
                        changed = True
                    if layer['note_off'] != note_off:
                        layer['note_off'] = note_off
                        changed = True
                    if layer['transient'] != transient:
                        layer['transient'] = transient
                        changed = True
                    if layer['transient_layer'] != transient_layer:
                        layer['transient_layer'] = transient_layer
                        changed = True
                    if layer['scale'] != scaling:
                        layer['scale'] = scaling
                        changed = True
                    changed = True
                else:
                    layers[ch] = {'output_port': port, 'voice': voice_name, 'note': note, 'note_off': note_off,
                                  'transient': transient, 'transient_layer': transient_layer, 'scale': scaling}
                    changed = True
        if changed:
            _router.program_changed = True
            _router.update(already_waiting=True)
        else:
            _router.resume() # resume second thread
        return changed

    def _save_pc_settings(self) -> None:
        '''save values from input blocks on the program change sub-page; called by self.process_user_input'''
        _router = ml.router
        _router.handshake() # request second thread to wait
        program = _router.program
        new_program_change = []
        new_bank_select = []
        for port, pc_and_bank in enumerate(self.pc_settings):
            if pc_and_bank[0] != _NONE:
                new_program_change.append([port, pc_and_bank[0]])
            if pc_and_bank[1] != _NONE or pc_and_bank[2] != _NONE:
                new_bank_select.append([port, [pc_and_bank[1], pc_and_bank[2]]])
        changed = False
        if program['program_change'] != new_program_change:
            changed = True
            program['program_change'] = new_program_change
        if program['bank_select'] != new_bank_select:
            changed = True
            program['bank_select'] = new_bank_select
        if not changed:
            _router.resume() # resume second thread
            return
        if not _router.program_changed:
            _router.program_changed = True
        _router.update(already_waiting=True)

    def _callback_trigger(self, trigger: int, zone: int) -> None:
        '''callback for trigger select pop-up; called (passed on) by self.process_user_input'''
        ml.ui.set_trigger(trigger, zone)

    def _callback_text_edit(self, caller_id: int, text: str) -> None:
        '''callback function for text edit pop-up; called (passed on) by self._callback_menu'''
        if text == '':
            text = DEFAULT_PROGRAM_NAME
        _router = ml.router
        _router.rename_program(text)

    def _callback_confirm(self, caller_id: int, confirm: bool) -> None:
        '''callback for confirm pop-up; called (passed on) by self.process_user_input, self._callback_confirm and self._callback_menu'''
        if not confirm:
            return
        if caller_id == _NAME:
            ml.router.delete_program()

    def _callback_menu(self, selection: int) -> None:
        '''callback for menu pop-up; called (passed on) by self.process_user_input'''
        sub_page = self.sub_page
        if sub_page == _SUB_PAGE_MAPPING or sub_page == _SUB_PAGE_NOTE:
            _ml = ml
            _router = _ml.router
            if selection == _RENAME:
                try:
                    text = _ml.data.programs[_router.active_bank][_router.active_program]
                except:
                    text = DEFAULT_PROGRAM_NAME
                self.draw()
                _ml.ui.pop_ups[_POP_UP_TEXT_EDIT].open(self, _NAME, text, is_file_name=True, callback_func=self._callback_text_edit)
            elif selection == _MOVE_BACKWARD:
                if (destination := _router.active_program - 1) >= 0:
                    _router.move_program(_router.active_bank, destination)
                else:
                    _router.update()
            elif selection == _MOVE_FORWARD:
                if (destination := _router.active_program + 1) < 100:
                    _router.move_program(_router.active_bank, destination)
                else:
                    _router.update()
            else: # program_changed and selection == _MOVE_TO_W or not program_changed and selection == _MOVE_TO_WO
                _ml.ui.pop_ups[_POP_UP_PROGRAM].open(self, ('move to bank', 'move to program'), _router.active_bank,
                                                     _router.active_program, self._callback_program)

    def _callback_program(self, bank: int, program: int) -> None:
        '''callback for program select pop-up; called (passed on) by self._callback_menu'''
        _router = ml.router
        if bank == _router.active_bank and program == _router.active_program:
            _router.update()
        else:
            _router.move_program(bank, program)

    def _device_options(self, i: int) -> str:
        '''function to pass on to device options generator'''
        output_mapping = ml.data.output_mapping
        return f'[port {i + 1}]' if output_mapping[2 * i] == '' else output_mapping[2 * i]
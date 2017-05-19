# -*- coding: utf-8 -*-
"""
Copyright (C) 2016 Korcan Karaokçu <korcankaraokcu@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from PyQt5.QtWidgets import QDesktopWidget
from re import search, sub
from . import type_defs
from . import SysUtils


def get_icons_directory():
    """Gets the directory of the icons

    Returns:
        str: Path to the icons directory
    """
    return SysUtils.get_current_script_directory() + "/media/icons"


def center(window):
    """Center the given window to desktop

    Args:
        window (QMainWindow, QWidget etc.): The window that'll be centered to desktop
    """
    window.move(QDesktopWidget().availableGeometry().center() - window.frameGeometry().center())


def center_to_parent(window):
    """Center the given window to it's parent

    Args:
        window (QMainWindow, QWidget etc.): The window that'll be centered to it's parent
    """
    window.move(window.parent().frameGeometry().center() - window.frameGeometry().center())


def center_to_window(window_secondary, window_main):
    """Center the given window_secondary to window_main

    Args:
        window_secondary (QMainWindow, QWidget etc.): The window that'll be centered to window_main
        window_main (QMainWindow, QWidget etc.): The window that window_secondary will centered to
    """
    window_secondary.move(window_main.frameGeometry().center() - window_secondary.frameGeometry().center())


def center_scroll_bar(QScrollBar):
    """Center the given scrollbar

    Args:
        QScrollBar (QScrollbar): The scrollbar that'll be centered
    """
    maximum = QScrollBar.maximum()
    minimum = QScrollBar.minimum()
    QScrollBar.setValue((maximum + minimum) / 2)


def fill_value_combobox(QCombobox, current_index=type_defs.VALUE_INDEX.INDEX_4BYTES):
    """Fills the given QCombobox with value_index strings

    Args:
        QCombobox (QCombobox): The combobox that'll be filled
        current_index (int): Can be a member of type_defs.VALUE_INDEX
    """
    for key in type_defs.index_to_text_dict:
        if key == type_defs.VALUE_INDEX.INDEX_AOB:
            QCombobox.addItem("Array of Bytes")
        else:
            QCombobox.addItem(type_defs.index_to_text_dict[key])
    QCombobox.setCurrentIndex(current_index)


def search_parents_by_function(qt_object, func_name):
    """Search for func_name in the parents of given qt_object. Once function is found, parent that possesses func_name
    is returned

    Args:
        qt_object (object): The object that'll be searched for it's parents
        func_name (str): The name of the function that'll be searched
    """
    while qt_object is not None:
        qt_object = qt_object.parent()
        if func_name in dir(qt_object):
            return qt_object


def valuetype_to_text(value_index=int, length=0, zero_terminate=True):
    """Returns a str according to given parameters

    Args:
        value_index (int): Determines the type of data. Can be a member of type_defs.VALUE_INDEX
        length (int): Length of the data. Only used when the value_index is INDEX_STRING or INDEX_AOB. Ignored otherwise
        zero_terminate (bool): If False, ",NZT" will be appended to str. Only used when value_index is INDEX_STRING.
        Ignored otherwise. "NZT" stands for "Not Zero Terminate"

    Returns:
        str: A str generated by given parameters
        str "out of bounds" is returned if the value_index doesn't match the dictionary

    Examples:
        value_index=type_defs.VALUE_INDEX.INDEX_STRING_UTF16, length=15, zero_terminate=False--▼
        returned str="String_UTF16[15],NZT"
        value_index=type_defs.VALUE_INDEX.INDEX_AOB, length=42-->returned str="AoB[42]"
    """
    returned_string = type_defs.index_to_text_dict.get(value_index, "out of bounds")
    if type_defs.VALUE_INDEX.is_string(value_index):
        returned_string = returned_string + "[" + str(length) + "]"
        if not zero_terminate:
            returned_string += ",NZT"
    elif value_index is type_defs.VALUE_INDEX.INDEX_AOB:
        returned_string += "[" + str(length) + "]"
    return returned_string


def text_to_valuetype(string):
    """Returns a tuple of parameters of the function valuetype_to_text evaluated according to given str

    Args:
        string (str): String must be generated from the function valuetype_to_text

    Returns:
        tuple: A tuple consisting of parameters of the function valuetype_to_text--▼
        value_index, length, zero_terminate, byte_length

        If value_index doesn't contain length, length will be returned as -1
        If value_index is INDEX_STRING, byte_length will be returned as -1

    Examples:
        string="String_UTF8[15],NZT"--▼
        value_index=type_defs.VALUE_INDEX.INDEX_STRING_UTF8, length=15, zero_terminate=False, byte_length=-1
        string="AoB[42]"-->value_index=type_defs.VALUE_INDEX.INDEX_AOB, length=42, None, 42
        string="Double"-->value_index=type_defs.VALUE_INDEX.INDEX_DOUBLE, length=-1, None, 8
    """
    index, length = -1, -1
    zero_terminate = None
    for key in type_defs.text_to_index_dict:
        if string.startswith(key):
            index = type_defs.text_to_index_dict[key]
            break
    byte_len = type_defs.index_to_valuetype_dict.get(index, [-1])[0]
    if type_defs.VALUE_INDEX.has_length(index):
        length = search(r"\[\d+\]", string).group(0)[1:-1]
        length = int(length)
        byte_len = length
        if type_defs.VALUE_INDEX.is_string(index):
            byte_len = -1
            if search(r",NZT", string):
                zero_terminate = False
            else:
                zero_terminate = True
    return index, length, zero_terminate, byte_len


def change_text_length(string, length):
    """Changes the length of the given str to the given length

    Args:
        string (str): String must be generated from the function valuetype_to_text
        length (int,str): New length

    Returns:
        str: The changed str
        int: -1 is returned if the value_index of the given string isn't INDEX_STRING or INDEX_AOB
    """
    index = text_to_valuetype(string)[0]
    if type_defs.VALUE_INDEX.has_length(index):
        return sub(r"\[\d+\]", "[" + str(length) + "]", string)
    return -1


def remove_bookmark_mark(string):
    """Removes the bookmark mark from the given string

    Args:
        string (str): String that'll be cleansed from the bookmark mark

    Returns:
        str: Remaining str after the cleansing
    """
    return sub(r"\(M\)", "", string, count=1)


def contains_reference_mark(string):
    """Checks if given string contains the reference mark

    Args:
        string (str): String that'll be checked for the reference mark

    Returns:
        bool: True if given string contains the reference mark, False otherwise
    """
    return True if search(r"\{\d*\}", string) else False

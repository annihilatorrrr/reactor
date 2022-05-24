from typing import Optional

import regex
from telegram import Message as TGMessage

from bot.utils import clear_buttons

MAGIC_MARK = regex.compile(r'^(?:\.(-|\+|~|`.*`)+|(\+\++|--))')


def get_magic_marks(text: str):
    if not text:
        return
    if m := MAGIC_MARK.search(text):
        return m.captures(1) or m[2]  # list of captured values or string with special cases


def clear_magic_marks(text: str, marks: list):
    text = text[1:]  # remove .
    s = sum(map(len, marks))
    text = text[s:] if len(text) > s else None
    return text


def restore_text(msg: TGMessage, text: Optional[str]):
    """Return False if text was removed and message can't be reposted."""
    had_text = bool(msg.text)
    msg.text = text
    msg.caption = text
    return not (had_text and text is None)


def process_magic_mark(msg: TGMessage):
    force = 0  # force message repost
    anon = False  # hide credits
    skip = False  # skip message
    buttons = None  # override buttons on message

    text: str = msg.text or msg.caption
    marks = get_magic_marks(text)
    if not marks:
        return force, anon, skip, buttons
    elif isinstance(marks, str):
        if marks == '--':
            skip = True
            return force, anon, skip, buttons
        # assume ++
        force = marks.count('+') - 1
        return force, anon, skip, buttons

    text_wo_marks = clear_magic_marks(text, marks)
    if not restore_text(msg, text_wo_marks):
        skip = True
    if '-' in marks:
        skip = True
    force = marks.count('+')
    if '~' in marks:
        anon = True
    for mark in marks:
        if '`' in mark:
            buttons = mark[1:-1].split()
            buttons = clear_buttons(buttons)
            break
    return force, anon, skip, buttons

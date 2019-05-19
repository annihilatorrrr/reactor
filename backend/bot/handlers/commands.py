import logging

from django.utils.datastructures import OrderedSet
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from .utils import command, get_chat

logger = logging.getLogger(__name__)


@command('help')
def command_help(update: Update, context: CallbackContext):
    text = '\n'.join([
        "This bot will automagically add reactions panel to your images/gifs/videos/links.",
        "`/help` - print this message",
        "`/set <button> [<button>...]` - set up buttons",
        "`/get` - get list of default buttons for this chat",
    ])
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


@command('get')
def command_get_buttons(update: Update, context: CallbackContext):
    chat = get_chat(update)
    bs = ', '.join(chat.buttons)
    update.message.reply_text(f"Current default buttons: [{bs}]")


@command('set', pass_args=True)
def command_set_buttons(update: Update, context: CallbackContext):
    chat = get_chat(update)
    if len(context.args) > 80:
        update.message.reply_text("Number of buttons is too big.")
        return
    bs = [b for b in OrderedSet(context.args) if len(b) < 20]
    chat.buttons = bs
    chat.save()
    bs = ', '.join(bs)
    update.message.reply_text(f"New default buttons: [{bs}]")


@command('credits', pass_args=True)
def command_show_credits(update: Update, context: CallbackContext):
    chat = get_chat(update)
    if len(context.args) != 1:
        update.message.reply_text("Specify show/hide option.")
        return
    option = context.args[0]
    if option == 'show':
        chat.show_credits = True
        chat.save()
    elif option == 'hide':
        chat.show_credits = False
        chat.save()
    else:
        update.message.reply_text(f"Unknown option '{option}'. Should be show or hide.")


@command('padding', pass_args=True)
def command_show_credits(update: Update, context: CallbackContext):
    chat = get_chat(update)
    if len(context.args) != 1:
        update.message.reply_text("Specify add/remove option.")
        return
    option = context.args[0]
    if option == 'add':
        chat.add_padding = True
        chat.save()
    elif option == 'remove':
        chat.add_padding = False
        chat.save()
    else:
        update.message.reply_text(f"Unknown option '{option}'. Should be add or remove.")


@command('row', pass_args=True)
def command_show_credits(update: Update, context: CallbackContext):
    chat = get_chat(update)
    if len(context.args) != 1 or context.args[0].isdecimal():
        update.message.reply_text("Specify number of buttons per row.")
        return
    option = int(context.args[0])
    chat.buttons_per_row = option
    chat.save()
    update.message.reply_text(f"New number of buttons per row: {option}.")


@command('add_allowed', pass_args=True)
def command_show_credits(update: Update, context: CallbackContext):
    chat = get_chat(update)
    if len(context.args) < 1:
        update.message.reply_text("Specify at least one type.")
        return

    types = set(chat.allowed_types) | set(context.args)
    allowed = {'photo', 'video', 'animation', 'text', 'link', 'forward'}
    types = list(filter(lambda e: e in allowed, types))
    chat.allowed_types = types
    chat.save()
    types_str = ', '.join(types)
    update.message.reply_text(f"Allowed types: {types_str}.")


@command('remove_allowed', pass_args=True)
def command_show_credits(update: Update, context: CallbackContext):
    chat = get_chat(update)
    if len(context.args) < 1:
        update.message.reply_text("Specify at least one type.")
        return

    types = set(chat.allowed_types) - set(context.args)
    types = list(types)
    chat.allowed_types = types
    chat.save()
    types_str = ', '.join(types)
    update.message.reply_text(f"Allowed types: {types_str}.")

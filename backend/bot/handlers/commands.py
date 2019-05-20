import logging

from django.utils.datastructures import OrderedSet
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, Filters

from core.models import Chat
from .utils import command, get_chat

logger = logging.getLogger(__name__)


@command('help', pass_args=True)
def command_help(update: Update, context: CallbackContext):
    print_all = context.args and context.args[0] == 'all'
    commands = [
        "This bot can automagically add reactions panel to messages.",
        "`/help` - print commands",
        "`/help all` - print all commands",
    ]
    t = update.effective_chat.type
    if print_all or t == 'private':
        commands.extend([
            "`/chats [update]` - show available chats",
        ])
    if print_all or 'group' in t:
        commands.extend([
            "`/set <button> [<button>...]` - set up buttons",
            "`/get` - get list of default buttons for this chat",
            "`/credits show|hide` - show how posted message message",
            "`/padding add|remove` - add padding to buttons",
            "`/columns <number>` - number of buttons in row [1, 10]",
            "`/allowed` - show allowed for reposting message types",
            "`/add_allowed <type> [<type>...]` - add allowed types",
            "`/remove_allowed <type> [<type>...]` - remove allowed types",
        ])
    text = '\n'.join(commands)
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


@command('get')
def command_get_buttons(update: Update, context: CallbackContext):
    chat = get_chat(update)
    bs = ', '.join(chat.buttons)
    update.message.reply_text(f"Current default buttons: [{bs}]")


@command('set', pass_args=True, admin_required=True)
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


@command('credits', pass_args=True, admin_required=True)
def command_credits(update: Update, context: CallbackContext):
    chat = get_chat(update)
    if len(context.args) != 1:
        update.message.reply_text("Specify show/hide option.")
        return
    option = context.args[0]
    if option == 'show':
        chat.show_credits = True
        chat.save()
        reply = f"Will show message credits."
    elif option == 'hide':
        chat.show_credits = False
        chat.save()
        reply = f"Will not show message credits."
    else:
        reply = f"Unknown option '{option}'. Should be show or hide."
    update.message.reply_text(reply)


@command('padding', pass_args=True, admin_required=True)
def command_padding(update: Update, context: CallbackContext):
    chat = get_chat(update)
    if len(context.args) != 1:
        update.message.reply_text("Specify add/remove option.")
        return
    option = context.args[0]
    if option == 'add':
        chat.add_padding = True
        chat.save()
        reply = "Will add padding to buttons."
    elif option == 'remove':
        chat.add_padding = False
        chat.save()
        reply = "Will not add padding to buttons."
    else:
        reply = f"Unknown option '{option}'. Should be add or remove."
    update.message.reply_text(reply)


@command('columns', pass_args=True, admin_required=True)
def command_columns(update: Update, context: CallbackContext):
    chat = get_chat(update)
    if len(context.args) != 1 or not context.args[0].isdecimal():
        update.message.reply_text("Specify number of buttons per row (number of columns).")
        return
    option = int(context.args[0])
    if not 1 <= option <= 10:
        update.message.reply_text("Number of columns should be between 1 and 10.")
        return
    chat.columns = option
    chat.save()
    update.message.reply_text(f"New number of buttons per row: {option}.")


@command('allowed', pass_args=True)
def command_allowed(update: Update, context: CallbackContext):
    chat = get_chat(update)
    types_str = ', '.join(sorted(chat.allowed_types))
    update.message.reply_text(f"Allowed types: {types_str}.")


@command('add_allowed', pass_args=True, admin_required=True)
def command_add_allowed(update: Update, context: CallbackContext):
    chat = get_chat(update)
    if len(context.args) < 1:
        update.message.reply_text("Specify at least one type.")
        return

    types = set(chat.allowed_types) | set(context.args)
    allowed = {'photo', 'video', 'animation', 'text', 'link', 'forward', 'album'}
    types = list(filter(lambda e: e in allowed, types))
    chat.allowed_types = types
    chat.save()
    types_str = ', '.join(sorted(types))
    update.message.reply_text(f"Allowed types: {types_str}.")


@command('remove_allowed', pass_args=True, admin_required=True)
def command_remove_allowed(update: Update, context: CallbackContext):
    chat = get_chat(update)
    if len(context.args) < 1:
        update.message.reply_text("Specify at least one type.")
        return

    types = set(chat.allowed_types) - set(context.args)
    types = list(types)
    chat.allowed_types = types
    chat.save()
    types_str = ', '.join(sorted(types))
    update.message.reply_text(f"Allowed types: {types_str}.")

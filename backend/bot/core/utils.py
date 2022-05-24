def get_commands_help(*commands):
    for cmd in commands:
        names = ' '.join([f"/{c}" for c in cmd.handler.command])
        if docs := cmd.__doc__:
            docs = docs.strip()
            yield f"{names} - {docs}"
        else:
            yield names


def normalize_text(text: str):
    lines = text.strip().split('\n')
    return '\n'.join([line.strip() for line in lines])

def split_source_lines(content: str) -> list[str]:
    content = content.replace("\r\n","\n").replace("\r","\n")

    lines = content.split("\n")

    if content.endswith("\n"):
        lines.pop()

    return lines
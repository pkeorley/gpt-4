import re


def add_triple_backticks(text):
    pattern = r"(```[\w]*\n[^`]*)(?<!```)"

    def add_backticks(match_obj):
        r = match_obj.group(1)
        print(r)
        return r + "```"

    result = re.sub(pattern, add_backticks, text)
    return result.replace("``````", "```")


if __name__ == "__main__":
    arg = "```py\ndef fibo(x):\n\treturn x * 2```Here you can see an code that..."
    print("=" * 25)
    print(add_triple_backticks(arg))
    print("=" * 25)


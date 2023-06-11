import re


def check(answer: str):
    answer = answer.rstrip("\n```")
    r = re.findall(r"^(.*)\n", answer)
    if len(r) == 1:
        answer += "\n```"
    return answer


print(check("```py\nHere is the text...```\n\njejeconsole.log('hi');```"))

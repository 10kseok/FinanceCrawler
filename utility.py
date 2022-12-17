import re


def only_num(content) -> str:
    num = re.sub(r'[^0-9]', '', content)
    return num

if __name__ == "__main__":
    print(only_num('24 sad  ,386,473'))

from ScreenInterpreter import ScreenInterpreter

raw = '\nNAPOJ GOTOWY\nOdbierz\n'
# '\n\n\nCena    :      2.00'
# '\nWoda      - \x01 \x01 \x01 +\n\n'
# 'WYBRANY NAPOJ\nWoda      - \x01 \x01 \x01 +\n>'
# 'WYBRANY NAPOJ\n\n\nCena    :      3.00'
# 'WYBRANY NAPOJ\nDodatkowy cukier\n\nCena    : >'
# '\n\n\nCena    :      2.00'
# '\n\n\n'
# '\nDodatkowy cukier\n\nKredyt  :      3.00'
# 'WYBIERZ NAPOJ\nWoda      - \x01 \x01 \x01 +\n>'
# '\nWoda      - \x01 \x01 \x01 +\n\nKredyt  :  >'
# 'WYBRANY NAPOJ\n\n\nCena    :      0.00'
# 'WYBRANY NAPOJ\n\n\n\x03'
# 'WYBRANY NAPOJ\n\n\n\x04'
# 'WYBRANY NAPOJ\n\n\n\x06'
# 'WYBRANY NAPOJ\n\n\n�'
# 'WYBRANY NAPOJ\n\n\n�\x04'
#
# '\n\n\n���������������\x05'
# '\nNAPOJ GOTOWY\nOdbierz\n'
# '\nNAPOJ GOTOWY\n\n'
# 'WYBIERZ NAPOJ\n\n\n'

lines = [
    line.strip()
    .replace("-", "")
    .replace("+", "")
    for line in raw.split("\n")
    if line.strip() != ""
]

print("Parsed raw into LCD lines:", lines)
interpreter = ScreenInterpreter()
state = interpreter.interpret_lines(lines)


print("\nStan maszyny:", state)


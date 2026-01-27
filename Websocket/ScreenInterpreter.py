import re


class ScreenInterpreter:

    def __init__(self):
        # Add missing attribute!
        self.last_valid_price = None

    def interpret_lines(self, raw_lines):

        state = {
            "tech": False,
            "loading": False,
            "ready": False,
            "current_price": None,
            "has_credit": False,
            "timed_out": False,
            "sugar": None,
            "credit": None,
            "remaining_lines": []
        }

        for line in raw_lines:

            # Woda/Cukier → liczymy \x01
            if line.startswith("Woda") or line.startswith("Cukier"):
                state["sugar"] = line.count("\x01")

                # remaining_lines.append(line)  # zachowujemy linię
                continue
            if line.startswith("Brak cukru"):
                state["sugar"] = None
                continue

            # LOADING — kontrolne znaki lub WYBRANY NAPOJ
            if any(3 <= ord(ch) <= 7 for ch in line):
                state["loading"] = True

            # Tryb TECH
            if line.startswith("TECH") or line.startswith("NAPE"):
                state["tech"] = True

            # WYBIERZ → normalny ekran
            if line.startswith("WYBIERZ"):
                state["loading"] = False
                state["tech"] = False

            # Gotowy napój
            if line.startswith("NAPOJ"):
                state["ready"] = True
                state["loading"] = False

            # Kredyt
            if line.startswith("Kredyt"):
                match = re.search(r"(\d+\.\d{2})", line)
                state["credit"] = float(match.group(1)) if match else 0.0
                state["has_credit"] = True
                state["timed_out"] = False
                continue  # nie dodajemy linii do remaining_lines

            # Cena
            if line.startswith("Cena"):
                # 1) Format z przecinkiem lub kropką → używamy jako float
                match_decimal = re.search(r"(\d+[.,]\d+)", line)
                if match_decimal:
                    price = float(match_decimal.group(1).replace(",", "."))
                    self.last_valid_price = price
                    state["current_price"] = price
                    continue

                # 2) Format liczbowy bez separatora
                match_int = re.search(r"(\d+)", line)
                if match_int:
                    price = float(match_int.group(1))  # ← używamy BEZ zmiany wartości
                    self.last_valid_price = price
                    state["current_price"] = price
                    continue

                # 3) Jeśli brak liczby → użyj poprzedniej
                if self.last_valid_price is not None:
                    state["current_price"] = self.last_valid_price
                continue

            # pozostałe linie zostają
            state["remaining_lines"].append(line)

        return state

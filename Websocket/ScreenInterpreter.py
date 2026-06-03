import re


class ScreenInterpreter:

    def __init__(self):
        self.last_valid_price = None

    def interpret_lines(self, raw_lines):

        state = {
            "out_of_order": False,
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
            line_lower = line.lower()

            # OUT OF ORDER detection (MUST be per-line)
            if (
                "nieczynny" in line_lower
                or "lista bledow" in line_lower
                or "koniec bledow" in line_lower
                or "automat sprzedajacy" in line_lower
            ):
                state["out_of_order"] = True

            # Woda / Cukier
            if line.startswith("Woda") or line.startswith("Cukier"):
                state["sugar"] = line.count("\x01")
                continue

            if line.startswith("Brak cukru"):
                state["sugar"] = None
                continue

            # loading detection
            if any(3 <= ord(ch) <= 7 for ch in line):
                state["loading"] = True

            # tech mode
            if line.startswith("TECH") or line.startswith("NAPE"):
                state["tech"] = True

            # reset screen
            if line.startswith("WYBIERZ"):
                state["loading"] = False
                state["tech"] = False
                state["out_of_order"] = False

            # ready
            if line.startswith("NAPOJ"):
                state["ready"] = True
                state["loading"] = False

            # credit
            if line.startswith("Kredyt"):
                match = re.search(r"(\d+\.\d{2})", line)
                state["credit"] = float(match.group(1)) if match else 0.0
                state["has_credit"] = True
                state["timed_out"] = False
                continue

            # price
            if line.startswith("Cena"):
                match_decimal = re.search(r"(\d+[.,]\d+)", line)
                if match_decimal:
                    price = float(match_decimal.group(1).replace(",", "."))
                    self.last_valid_price = price
                    state["current_price"] = price
                    continue

                match_int = re.search(r"(\d+)", line)
                if match_int:
                    price = float(match_int.group(1))
                    self.last_valid_price = price
                    state["current_price"] = price
                    continue

                if self.last_valid_price is not None:
                    state["current_price"] = self.last_valid_price
                    continue

            # default: keep line
            state["remaining_lines"].append(line)

        return state
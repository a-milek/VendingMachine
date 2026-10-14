import os
import re
import time

# Unique frames that matched no known pattern are appended here, so init/error
# screens (PL/EN/IT) can be collected and given proper handling later.
UNKNOWN_FRAMES_LOG = os.getenv(
    "VENDING_MACHINE_UNKNOWN_FRAMES_LOG",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "unknown_frames.log"),
)


class ScreenInterpreter:

    def __init__(self):
        self.last_valid_price = None
        # Set by a frame we can't interpret (init, errors, other languages);
        # held until the idle WYBIERZ screen so multi-step screens don't flicker.
        self.unrecognized = False
        self.logged_frames = set()

    def _log_unknown_frame(self, raw_lines):
        key = "\n".join(raw_lines)
        if key in self.logged_frames:
            return
        self.logged_frames.add(key)
        try:
            with open(UNKNOWN_FRAMES_LOG, "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {raw_lines!r}\n")
        except OSError as e:
            print(f"Could not write {UNKNOWN_FRAMES_LOG}: {e}")

    def interpret_lines(self, raw_lines):
        recognized = False

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
            "remaining_lines": [],
            "raw_lines": list(raw_lines),
            "unrecognized": False
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
            if line.startswith("Cukier"):
                state["sugar"] = line.count("\x01")
                recognized = True
                continue

            if line.startswith("Brak cukru"):
                state["sugar"] = None
                recognized = True
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
                recognized = True
                self.unrecognized = False

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

            # price (shown during a normal selection, so it's a known screen)
            if line.startswith("Cena"):
                recognized = True

            # if line.startswith("Cena"):
            #     match_decimal = re.search(r"(\d+[.,]\d+)", line)
            #     if match_decimal:
            #         price = float(match_decimal.group(1).replace(",", "."))
            #         self.last_valid_price = price
            #         state["current_price"] = price
            #         continue

            #     match_int = re.search(r"(\d+)", line)
            #     if match_int:
            #         price = float(match_int.group(1))
            #         self.last_valid_price = price
            #         state["current_price"] = price
            #         continue

            #     if self.last_valid_price is not None:
            #         state["current_price"] = self.last_valid_price
            #         continue

            # default: keep line
            state["remaining_lines"].append(line)

        recognized = recognized or any(
            state[k] for k in ("out_of_order", "tech", "loading", "ready", "has_credit")
        )
        if not recognized:
            self.unrecognized = True
            self._log_unknown_frame(raw_lines)
        state["unrecognized"] = self.unrecognized

        return state
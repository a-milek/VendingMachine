import os
import re
import time

# Unique frames that matched no known pattern are appended here, so init/error
# screens (PL/EN/IT) can be collected and given proper handling later.
UNKNOWN_FRAMES_LOG = os.getenv(
    "VENDING_MACHINE_UNKNOWN_FRAMES_LOG",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "unknown_frames.log"),
)

OUT_OF_ORDER_MARKERS = ("nieczynny", "lista bledow", "koniec bledow", "automat sprzedajacy")
KNOWN_PREFIXES = (
    "Cukier", "Brak cukru", "Bez cukru", "WYBIERZ", "WYBRANY", "NAPOJ",
    "ODBIERZ", "Kredyt", "Cena", "TECH", "NAPE",
)
# Machine messages we don't translate but know are normal operation. They're
# still reported in unknown_lines (the UI shows them as an extra line), but a
# frame showing only one of them must not flip the sticky full-screen
# unrecognized mode. Matched case-insensitively as prefixes.
NOTICE_PREFIXES = ("kawa ziarn", "wybor", "nieudane")


def is_notice_line(line):
    return line.strip().lower().startswith(NOTICE_PREFIXES)


def is_known_line(line):
    """True for LCD lines the interpreter understands; the rest (e.g.
    "Kawa ziarn.niedostep") are reported in unknown_lines so the UI shows them."""
    if not line.strip():
        return True
    if line.startswith(KNOWN_PREFIXES):
        return True
    if any(3 <= ord(ch) <= 7 for ch in line):  # progress bar
        return True
    line_lower = line.lower()
    return any(m in line_lower for m in OUT_OF_ORDER_MARKERS)


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
            "unrecognized": False,
            # lines not understood, shown by the UI as an extra line
            "unknown_lines": [l.strip() for l in raw_lines if not is_known_line(l)],
        }

        for line in raw_lines:
            line_lower = line.lower()

            # OUT OF ORDER detection (MUST be per-line)
            if any(m in line_lower for m in OUT_OF_ORDER_MARKERS):
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

            # sugar set to zero by the customer
            if line.startswith("Bez cukru"):
                state["sugar"] = 0
                recognized = True
                continue

            # "WYBRANY NAPOJ": a drink was selected and is about to brew. It's a
            # known screen and, like WYBIERZ, clears the sticky unrecognized
            # flag, so an earlier odd frame can't hide the progress screen.
            if line.startswith("WYBRANY"):
                recognized = True
                self.unrecognized = False

            # known machine messages (shown via unknown_lines, see NOTICE_PREFIXES)
            if is_notice_line(line):
                recognized = True

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
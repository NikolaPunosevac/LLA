"""
Generates a step-by-step markdown tutorial for configuring a DocuWise
interview, based on the structured JSON specification.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TYPE_LABELS = {
    "text": "Text",
    "number": "Number",
    "date": "Date",
    "yes_no": "Yes/No",
    "accept": "Accept",
    "select": "Select",
    "multiselect": "Multiselect",
    "object": "Object",
    "list": "List",
}

OPERATOR_LABELS = {
    "equals": "je enako",
    "not_equals": "ni enako",
    "greater_than": "je večje od",
    "less_than": "je manjše od",
    "greater_or_equal": "je večje ali enako",
    "less_or_equal": "je manjše ali enako",
    "is_one_of": "je eden od",
}


def _fmt_value(value: Any) -> str:
    """Format a condition value for display."""
    if isinstance(value, bool):
        return "Da" if value else "Ne"
    if isinstance(value, list):
        return ", ".join(f"`{v}`" for v in value)
    return f"`{value}`"


def _describe_condition(cond: dict) -> str:
    """Return a human-readable description of a Condition object."""
    logic = cond.get("logic", "and").upper()
    parts: list[str] = []
    for item in cond["conditions"]:
        var = item["variable"]
        op = OPERATOR_LABELS.get(item["operator"], item["operator"])
        val = _fmt_value(item["value"])
        parts.append(f"`{var}` {op} {val}")
    joiner = f" **{logic}** "
    return joiner.join(parts)


# ---------------------------------------------------------------------------
# Settings describers (per variable type)
# ---------------------------------------------------------------------------

def _text_settings_steps(var_name: str, settings: dict) -> list[str]:
    steps: list[str] = []
    if settings.get("multiline"):
        steps.append(f"  - Vklopi **Multiline**.")
    if settings.get("min_length") is not None:
        steps.append(f"  - Nastavi **Min length** na `{settings['min_length']}`.")
    if settings.get("max_length") is not None:
        steps.append(f"  - Nastavi **Max length** na `{settings['max_length']}`.")
    return steps


def _number_settings_steps(var_name: str, settings: dict) -> list[str]:
    steps: list[str] = []
    if settings.get("unit"):
        steps.append(f"  - Nastavi **Unit** na `{settings['unit']}`.")
    if settings.get("is_float"):
        steps.append(f"  - Vklopi **Is float**.")
    if settings.get("min_value") is not None:
        steps.append(f"  - Nastavi **Min value** na `{settings['min_value']}`.")
    if settings.get("max_value") is not None:
        steps.append(f"  - Nastavi **Max value** na `{settings['max_value']}`.")
    return steps


def _date_settings_steps(var_name: str, settings: dict) -> list[str]:
    steps: list[str] = []
    if settings.get("date_format"):
        steps.append(
            f"  - Nastavi **Date format** na `{settings['date_format']}`."
        )
    if settings.get("locale"):
        steps.append(f"  - Nastavi **Date locale** na `{settings['locale']}`.")
    return steps


def _yes_no_settings_steps(var_name: str, settings: dict) -> list[str]:
    steps: list[str] = []
    yes_l = settings.get("yes_label", "Da")
    no_l = settings.get("no_label", "Ne")
    if yes_l != "Da" or no_l != "Ne":
        steps.append(
            f"  - Nastavi oznaki na `{yes_l}` / `{no_l}`."
        )
    return steps


def _select_settings_steps(var_name: str, settings: dict) -> list[str]:
    steps: list[str] = []
    display = settings.get("display_type", "dropdown")
    if display == "radio":
        steps.append(f"  - Nastavi prikaz na **Radio** (namesto Dropdown).")
    for opt in settings.get("options", []):
        steps.append(
            f"  - Dodaj opcijo: oznaka `{opt['label']}`, vrednost `{opt['value']}`."
        )
    return steps


def _multiselect_settings_steps(var_name: str, settings: dict) -> list[str]:
    steps: list[str] = []
    for opt in settings.get("options", []):
        steps.append(
            f"  - Dodaj opcijo: oznaka `{opt['label']}`, vrednost `{opt['value']}`."
        )
    return steps


SETTINGS_HANDLERS = {
    "text": _text_settings_steps,
    "number": _number_settings_steps,
    "date": _date_settings_steps,
    "yes_no": _yes_no_settings_steps,
    "accept": lambda vn, s: [],
    "select": _select_settings_steps,
    "multiselect": _multiselect_settings_steps,
}


# ---------------------------------------------------------------------------
# Attribute steps (for object / list)
# ---------------------------------------------------------------------------

def _attribute_steps(var_name: str, attr: dict) -> list[str]:
    steps: list[str] = []
    a_name = attr["attribute_name"]
    a_label = attr["label"]
    a_type = attr["type"]
    a_req = attr.get("required", False)

    steps.append(
        f"  - Dodaj atribut z imenom `{a_name}`."
    )
    steps.append(
        f"    - Nastavi oznako na `{a_label}`."
    )
    steps.append(
        f"    - Nastavi tip na **{TYPE_LABELS.get(a_type, a_type)}**."
    )
    if a_req:
        steps.append(f"    - Vklopi **Required**.")

    # Attribute-level settings
    handler = SETTINGS_HANDLERS.get(a_type)
    if handler:
        sub = handler(a_name, attr.get("settings", {}))
        for s in sub:
            # Indent one extra level
            steps.append(f"  {s}")
    return steps


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_tutorial(data: dict) -> list[str]:
    """
    Generate a list of markdown-formatted tutorial steps from a DocuWise
    interview JSON specification.

    Parameters
    ----------
    data : dict
        The parsed JSON conforming to the DocuWise interview spec.

    Returns
    -------
    list[str]
        Each element is one logical step (may contain sub-bullets),
        formatted in markdown.
    """
    steps: list[str] = []
    pages = sorted(data.get("pages", []), key=lambda p: p["order"])
    variables = data.get("variables", [])

    # Build lookup: page_id -> page
    page_map = {p["page_id"]: p for p in pages}

    # Group variables by page, sorted by order within each page
    vars_by_page: dict[str, list[dict]] = {p["page_id"]: [] for p in pages}
    for var in variables:
        pid = var["page_id"]
        if pid in vars_by_page:
            vars_by_page[pid].append(var)
    for pid in vars_by_page:
        vars_by_page[pid].sort(key=lambda v: v["order"])

    # ------------------------------------------------------------------
    # 0. Header
    # ------------------------------------------------------------------
    tpl_name = data.get("template_name", "Predloga")
    steps.append(
        f"# Navodila za konfiguracijo intervjuja: {tpl_name}"
    )
    steps.append("")

    lang = data.get("language", "sl")
    fmts = ", ".join(data.get("output_formats", []))
    steps.append("## Osnovne nastavitve")
    steps.append("")
    steps.append(f"1. Nastavi **jezik intervjuja** na `{lang}`.")
    steps.append(f"2. Nastavi **izhodne formate** na: {fmts}.")
    steps.append("")

    # ------------------------------------------------------------------
    # 1. Create pages
    # ------------------------------------------------------------------

    for i, page in enumerate(pages):
        if i == 0:
            steps.append(
                f"## Stran {i + 1}: {page['title']}"
            )
            steps.append("")
            steps.append(
                f"1. Preimenuj obstoječo (prvo) stran – nastavi naslov na "
                f"`{page['title']}`."
            )
        else:
            steps.append(
                f"## Stran {i + 1}: {page['title']}"
            )
            steps.append("")
            steps.append(
                f"1. Klikni **Add page** in nastavi naslov na "
                f"`{page['title']}`."
            )

        step_num = 2
        if page.get("description"):
            steps.append(
                f"{step_num}. Nastavi opis strani na:\n"
                f"   ```\n"
                f"   {page['description']}\n"
                f"   ```"
            )
            step_num += 1

        if page.get("show_if"):
            cond_desc = _describe_condition(page["show_if"])
            steps.append(
                f"{step_num}. Dodaj pogoj **Show-if** na stran: prikaži, če {cond_desc}."
            )
            step_num += 1

        steps.append("")

    # ------------------------------------------------------------------
    # 2. Variables, grouped by page
    # ------------------------------------------------------------------

    global_var_num = 0
    for page in pages:
        pid = page["page_id"]
        page_vars = vars_by_page.get(pid, [])
        if not page_vars:
            continue

        steps.append(f"## Stran: {page['title']}")
        steps.append("")

        for var in page_vars:
            global_var_num += 1
            vname = var["variable_name"]
            vtype = var["type"]
            vlabel = var["label"]
            vreq = var.get("required", False)
            settings = var.get("settings", {})

            steps.append(f"### {global_var_num}. `{vname}`")
            steps.append("")

            substeps: list[str] = []
            substeps.append(
                f"1. Poišči spremenljivko `{vname}` in jo **premakni** na "
                f"stran `{page['title']}`."
            )
            substeps.append(
                f"2. Nastavi tip na **{TYPE_LABELS.get(vtype, vtype)}**."
            )
            substeps.append(
                f"3. Nastavi oznako (label) na:\n"
                f"   ```\n"
                f"   {vlabel}\n"
                f"   ```"
            )
            if vreq:
                substeps.append(f"4. Vklopi **Required**.")
            else:
                substeps.append(f"4. Izklopi **Required** (ni obvezno).")

            next_num = 5

            # Type-specific settings
            handler = SETTINGS_HANDLERS.get(vtype)
            if handler:
                type_steps = handler(vname, settings)
                if type_steps:
                    substeps.append(f"{next_num}. Nastavitve:")
                    substeps.extend(type_steps)
                    next_num += 1

            # Object / List attributes
            if vtype in ("object", "list"):
                if vtype == "list":
                    min_it = settings.get("min_items")
                    max_it = settings.get("max_items")
                    if min_it is not None or max_it is not None:
                        substeps.append(f"{next_num}. Nastavitve seznama:")
                        if min_it is not None:
                            substeps.append(
                                f"  - Nastavi **Min items** na `{min_it}`."
                            )
                        if max_it is not None:
                            substeps.append(
                                f"  - Nastavi **Max items** na `{max_it}`."
                            )
                        next_num += 1

                attrs = settings.get("attributes", [])
                if attrs:
                    substeps.append(f"{next_num}. Dodaj atribute:")
                    for attr in attrs:
                        substeps.extend(_attribute_steps(vname, attr))
                    next_num += 1

            # Show-if / Hide-if
            if var.get("show_if"):
                cond_desc = _describe_condition(var["show_if"])
                substeps.append(
                    f"{next_num}. Dodaj pogoj **Show-if**: prikaži, "
                    f"če {cond_desc}."
                )
                next_num += 1
            elif var.get("hide_if"):
                cond_desc = _describe_condition(var["hide_if"])
                substeps.append(
                    f"{next_num}. Dodaj pogoj **Hide-if**: skrij, "
                    f"če {cond_desc}."
                )
                next_num += 1

            steps.extend(substeps)
            steps.append("")

    # ------------------------------------------------------------------
    # 3. Reorder reminder
    # ------------------------------------------------------------------
    steps.append("## Vrstni red spremenljivk")
    steps.append("")
    steps.append(
        "Na vsaki strani uporabi gumb za razvrščanje (drag & drop) in "
        "razvrsti spremenljivke v vrstnem redu, kot je naveden zgoraj."
    )
    steps.append("")

    # ------------------------------------------------------------------
    # 4. Final check
    # ------------------------------------------------------------------
    steps.append("## Zaključek")
    steps.append("")
    steps.append(
        "Klikni **Preview** in preveri, da se vsa vprašanja prikažejo "
        "pravilno. Ko je vse v redu, klikni **Publish**."
    )

    return steps


def generate_tutorial_text(data: dict) -> str:
    """Convenience: return the full tutorial as a single markdown string."""
    return "\n".join(generate_tutorial(data))


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print("Uporaba: python generate_tutorial.py <pot_do_json>")
        sys.exit(1)

    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))
    print(generate_tutorial_text(data))


if __name__ == "__main__":
    main()

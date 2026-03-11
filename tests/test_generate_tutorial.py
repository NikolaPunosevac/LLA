"""Unit tests for generate_tutorial module."""

import sys
from pathlib import Path

# Allow importing from src/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from generate_tutorial import generate_tutorial, generate_tutorial_text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lines(data: dict) -> list[str]:
    """Return non-empty tutorial lines for easier assertion."""
    return [l for l in generate_tutorial(data) if l.strip()]


def _text(data: dict) -> str:
    return generate_tutorial_text(data)


# ---------------------------------------------------------------------------
# 1. Minimal JSON – single page, single text variable
# ---------------------------------------------------------------------------

MINIMAL_JSON = {
    "template_name": "Test predloga",
    "language": "sl",
    "output_formats": ["pdf"],
    "pages": [
        {
            "page_id": "p1",
            "title": "Glavna stran",
            "description": None,
            "order": 1,
            "show_if": None,
        }
    ],
    "variables": [
        {
            "variable_name": "ime",
            "page_id": "p1",
            "order": 1,
            "type": "text",
            "label": "Vnesite ime",
            "required": True,
            "show_if": None,
            "hide_if": None,
            "settings": {
                "multiline": False,
                "min_length": None,
                "max_length": None,
            },
        }
    ],
}


def test_minimal_header():
    text = _text(MINIMAL_JSON)
    assert "# Navodila za konfiguracijo intervjuja: Test predloga" in text


def test_minimal_language_and_formats():
    text = _text(MINIMAL_JSON)
    assert "`sl`" in text
    assert "pdf" in text


def test_minimal_page_rename():
    text = _text(MINIMAL_JSON)
    # First page should be renamed, not added
    assert "Preimenuj obstoječo (prvo) stran" in text
    assert "`Glavna stran`" in text


def test_minimal_variable_steps():
    text = _text(MINIMAL_JSON)
    assert "`ime`" in text
    assert "**Text**" in text
    assert "Vnesite ime" in text
    assert "Vklopi **Required**" in text


def test_minimal_no_settings_for_defaults():
    """No multiline/length steps when all are defaults/None."""
    text = _text(MINIMAL_JSON)
    assert "Multiline" not in text
    assert "Min length" not in text
    assert "Max length" not in text


# ---------------------------------------------------------------------------
# 2. Text variable with non-default settings
# ---------------------------------------------------------------------------

TEXT_SETTINGS_JSON = {
    "template_name": "Text test",
    "language": "en",
    "output_formats": ["docx"],
    "pages": [
        {"page_id": "p1", "title": "Page 1", "description": "Some desc", "order": 1, "show_if": None}
    ],
    "variables": [
        {
            "variable_name": "opis",
            "page_id": "p1",
            "order": 1,
            "type": "text",
            "label": "Opis situacije",
            "required": False,
            "show_if": None,
            "hide_if": None,
            "settings": {"multiline": True, "min_length": 10, "max_length": 500},
        }
    ],
}


def test_text_multiline():
    text = _text(TEXT_SETTINGS_JSON)
    assert "Vklopi **Multiline**" in text


def test_text_length_constraints():
    text = _text(TEXT_SETTINGS_JSON)
    assert "Min length" in text and "`10`" in text
    assert "Max length" in text and "`500`" in text


def test_page_description():
    text = _text(TEXT_SETTINGS_JSON)
    assert "Some desc" in text


def test_not_required():
    text = _text(TEXT_SETTINGS_JSON)
    assert "Izklopi **Required**" in text


# ---------------------------------------------------------------------------
# 3. Number variable
# ---------------------------------------------------------------------------

NUMBER_JSON = {
    "template_name": "Number test",
    "language": "sl",
    "output_formats": ["pdf"],
    "pages": [
        {"page_id": "p1", "title": "Stran", "description": None, "order": 1, "show_if": None}
    ],
    "variables": [
        {
            "variable_name": "placa",
            "page_id": "p1",
            "order": 1,
            "type": "number",
            "label": "Bruto plača",
            "required": True,
            "show_if": None,
            "hide_if": None,
            "settings": {"unit": "EUR", "is_float": True, "min_value": 1253.90, "max_value": None},
        }
    ],
}


def test_number_settings():
    text = _text(NUMBER_JSON)
    assert "**Number**" in text
    assert "`EUR`" in text
    assert "Vklopi **Is float**" in text
    assert "Min value" in text and "`1253.9`" in text
    assert "Max value" not in text  # None -> no step


# ---------------------------------------------------------------------------
# 4. Select with radio + show_if condition
# ---------------------------------------------------------------------------

SELECT_SHOWIF_JSON = {
    "template_name": "Select test",
    "language": "sl",
    "output_formats": ["pdf"],
    "pages": [
        {"page_id": "p1", "title": "Stran 1", "description": None, "order": 1, "show_if": None}
    ],
    "variables": [
        {
            "variable_name": "vrsta",
            "page_id": "p1",
            "order": 1,
            "type": "select",
            "label": "Vrsta pogodbe",
            "required": True,
            "show_if": None,
            "hide_if": None,
            "settings": {
                "display_type": "radio",
                "options": [
                    {"label": "Določen čas", "value": "fixed"},
                    {"label": "Nedoločen čas", "value": "indefinite"},
                ],
            },
        },
        {
            "variable_name": "trajanje",
            "page_id": "p1",
            "order": 2,
            "type": "number",
            "label": "Trajanje v mesecih",
            "required": True,
            "show_if": {
                "logic": "and",
                "conditions": [
                    {"variable": "vrsta", "operator": "equals", "value": "fixed"}
                ],
            },
            "hide_if": None,
            "settings": {"unit": "mesecev", "is_float": False, "min_value": 1, "max_value": 24},
        },
    ],
}


def test_select_radio():
    text = _text(SELECT_SHOWIF_JSON)
    assert "**Radio**" in text


def test_select_options():
    text = _text(SELECT_SHOWIF_JSON)
    assert "`Določen čas`" in text
    assert "`fixed`" in text
    assert "`indefinite`" in text


def test_show_if_condition():
    text = _text(SELECT_SHOWIF_JSON)
    assert "Show-if" in text
    assert "`vrsta`" in text
    assert "je enako" in text
    assert "`fixed`" in text


# ---------------------------------------------------------------------------
# 5. Multiple pages with page-level show_if
# ---------------------------------------------------------------------------

MULTI_PAGE_JSON = {
    "template_name": "Multi page",
    "language": "sl",
    "output_formats": ["pdf", "docx"],
    "pages": [
        {"page_id": "p1", "title": "Osnovno", "description": None, "order": 1, "show_if": None},
        {
            "page_id": "p2",
            "title": "Dodatno",
            "description": "Dodatni podatki",
            "order": 2,
            "show_if": {
                "logic": "and",
                "conditions": [
                    {"variable": "tip", "operator": "equals", "value": "advanced"}
                ],
            },
        },
    ],
    "variables": [
        {
            "variable_name": "tip",
            "page_id": "p1",
            "order": 1,
            "type": "select",
            "label": "Tip",
            "required": True,
            "show_if": None,
            "hide_if": None,
            "settings": {
                "display_type": "dropdown",
                "options": [
                    {"label": "Osnovno", "value": "basic"},
                    {"label": "Napredno", "value": "advanced"},
                ],
            },
        },
        {
            "variable_name": "extra",
            "page_id": "p2",
            "order": 1,
            "type": "text",
            "label": "Dodatno polje",
            "required": False,
            "show_if": None,
            "hide_if": None,
            "settings": {"multiline": False, "min_length": None, "max_length": None},
        },
    ],
}


def test_second_page_add():
    text = _text(MULTI_PAGE_JSON)
    assert "Add page" in text
    assert "`Dodatno`" in text


def test_page_show_if():
    text = _text(MULTI_PAGE_JSON)
    # The page-level show_if
    lines = text.split("\n")
    page_section = [l for l in lines if "Show-if" in l and "stran" in l.lower()]
    # There should be at least one page-level show-if
    assert len(page_section) >= 1


def test_output_formats():
    text = _text(MULTI_PAGE_JSON)
    assert "pdf, docx" in text


# ---------------------------------------------------------------------------
# 6. Object variable with attributes
# ---------------------------------------------------------------------------

OBJECT_JSON = {
    "template_name": "Object test",
    "language": "sl",
    "output_formats": ["pdf"],
    "pages": [
        {"page_id": "p1", "title": "Stran", "description": None, "order": 1, "show_if": None}
    ],
    "variables": [
        {
            "variable_name": "podjetje",
            "page_id": "p1",
            "order": 1,
            "type": "object",
            "label": "Podatki o podjetju",
            "required": True,
            "show_if": None,
            "hide_if": None,
            "settings": {
                "attributes": [
                    {
                        "attribute_name": "ime",
                        "label": "Ime podjetja",
                        "type": "text",
                        "required": True,
                        "settings": {"multiline": False, "min_length": None, "max_length": None},
                    },
                    {
                        "attribute_name": "davcna",
                        "label": "Davčna številka",
                        "type": "text",
                        "required": True,
                        "settings": {"multiline": False, "min_length": None, "max_length": 10},
                    },
                ]
            },
        }
    ],
}


def test_object_type():
    text = _text(OBJECT_JSON)
    assert "**Object**" in text


def test_object_attributes():
    text = _text(OBJECT_JSON)
    assert "Dodaj atribut" in text
    assert "`ime`" in text
    assert "`Ime podjetja`" in text
    assert "`davcna`" in text
    assert "`Davčna številka`" in text


def test_object_attribute_max_length():
    text = _text(OBJECT_JSON)
    assert "Max length" in text and "`10`" in text


# ---------------------------------------------------------------------------
# 7. List variable with min/max items
# ---------------------------------------------------------------------------

LIST_JSON = {
    "template_name": "List test",
    "language": "sl",
    "output_formats": ["pdf"],
    "pages": [
        {"page_id": "p1", "title": "Stran", "description": None, "order": 1, "show_if": None}
    ],
    "variables": [
        {
            "variable_name": "otroci",
            "page_id": "p1",
            "order": 1,
            "type": "list",
            "label": "Otroci",
            "required": False,
            "show_if": None,
            "hide_if": None,
            "settings": {
                "min_items": 1,
                "max_items": 5,
                "attributes": [
                    {
                        "attribute_name": "name",
                        "label": "Ime otroka",
                        "type": "text",
                        "required": True,
                        "settings": {"multiline": False, "min_length": None, "max_length": None},
                    },
                    {
                        "attribute_name": "age",
                        "label": "Starost",
                        "type": "number",
                        "required": True,
                        "settings": {"unit": None, "is_float": False, "min_value": 0, "max_value": 18},
                    },
                ],
            },
        }
    ],
}


def test_list_type():
    text = _text(LIST_JSON)
    assert "**List**" in text


def test_list_min_max_items():
    text = _text(LIST_JSON)
    assert "Min items" in text and "`1`" in text
    assert "Max items" in text and "`5`" in text


def test_list_attributes():
    text = _text(LIST_JSON)
    assert "`name`" in text
    assert "`Ime otroka`" in text
    assert "`age`" in text
    assert "Max value" in text and "`18`" in text


# ---------------------------------------------------------------------------
# 8. Hide-if condition
# ---------------------------------------------------------------------------

HIDEIF_JSON = {
    "template_name": "Hide-if test",
    "language": "sl",
    "output_formats": ["pdf"],
    "pages": [
        {"page_id": "p1", "title": "Stran", "description": None, "order": 1, "show_if": None}
    ],
    "variables": [
        {
            "variable_name": "razlog",
            "page_id": "p1",
            "order": 1,
            "type": "text",
            "label": "Razlog",
            "required": False,
            "show_if": None,
            "hide_if": {
                "logic": "or",
                "conditions": [
                    {"variable": "tip", "operator": "equals", "value": "A"},
                    {"variable": "tip", "operator": "equals", "value": "B"},
                ],
            },
            "settings": {"multiline": False, "min_length": None, "max_length": None},
        }
    ],
}


def test_hide_if():
    text = _text(HIDEIF_JSON)
    assert "Hide-if" in text
    assert "**OR**" in text
    assert "`A`" in text
    assert "`B`" in text


# ---------------------------------------------------------------------------
# 9. Yes/No with custom labels
# ---------------------------------------------------------------------------

YESNO_JSON = {
    "template_name": "Yes/No test",
    "language": "sl",
    "output_formats": ["pdf"],
    "pages": [
        {"page_id": "p1", "title": "Stran", "description": None, "order": 1, "show_if": None}
    ],
    "variables": [
        {
            "variable_name": "tujec",
            "page_id": "p1",
            "order": 1,
            "type": "yes_no",
            "label": "Ali je tujec?",
            "required": True,
            "show_if": None,
            "hide_if": None,
            "settings": {"yes_label": "Da, je tujec", "no_label": "Ne, ni tujec"},
        }
    ],
}


def test_yes_no_custom_labels():
    text = _text(YESNO_JSON)
    assert "**Yes/No**" in text
    assert "`Da, je tujec`" in text
    assert "`Ne, ni tujec`" in text


# ---------------------------------------------------------------------------
# 10. Date variable
# ---------------------------------------------------------------------------

DATE_JSON = {
    "template_name": "Date test",
    "language": "sl",
    "output_formats": ["pdf"],
    "pages": [
        {"page_id": "p1", "title": "Stran", "description": None, "order": 1, "show_if": None}
    ],
    "variables": [
        {
            "variable_name": "datum",
            "page_id": "p1",
            "order": 1,
            "type": "date",
            "label": "Datum začetka",
            "required": True,
            "show_if": None,
            "hide_if": None,
            "settings": {"date_format": "d. MMMM yyyy", "locale": "sl"},
        }
    ],
}


def test_date_format():
    text = _text(DATE_JSON)
    assert "**Date**" in text
    assert "`d. MMMM yyyy`" in text
    assert "`sl`" in text


# ---------------------------------------------------------------------------
# 11. Full example from spec
# ---------------------------------------------------------------------------

FULL_EXAMPLE_JSON = {
    "template_name": "Pogodba o zaposlitvi",
    "language": "sl",
    "output_formats": ["pdf", "docx"],
    "pages": [
        {"page_id": "page_basic", "title": "Osnovni podatki", "description": "Vnesite podatke o zaposlenem.", "order": 1, "show_if": None},
        {"page_id": "page_contract", "title": "Pogoji pogodbe", "description": None, "order": 2, "show_if": None},
        {
            "page_id": "page_fixed_term",
            "title": "Določbe za določen čas",
            "description": "Izpolnite podatke o trajanju pogodbe.",
            "order": 3,
            "show_if": {
                "logic": "and",
                "conditions": [{"variable": "contract_type", "operator": "equals", "value": "fixed_period"}],
            },
        },
    ],
    "variables": [
        {
            "variable_name": "employee_name",
            "page_id": "page_basic",
            "order": 1,
            "type": "text",
            "label": "Ime in priimek zaposlenega",
            "required": True,
            "show_if": None,
            "hide_if": None,
            "settings": {"multiline": False, "min_length": None, "max_length": 100},
        },
        {
            "variable_name": "contract_type",
            "page_id": "page_contract",
            "order": 1,
            "type": "select",
            "label": "Vrsta pogodbe",
            "required": True,
            "show_if": None,
            "hide_if": None,
            "settings": {
                "display_type": "radio",
                "options": [
                    {"label": "Za določen čas", "value": "fixed_period"},
                    {"label": "Za nedoločen čas", "value": "indefinite"},
                ],
            },
        },
        {
            "variable_name": "duration_months",
            "page_id": "page_fixed_term",
            "order": 1,
            "type": "number",
            "label": "Trajanje pogodbe v mesecih",
            "required": True,
            "show_if": None,
            "hide_if": None,
            "settings": {"unit": "mesecev", "is_float": False, "min_value": 1, "max_value": 24},
        },
        {
            "variable_name": "company",
            "page_id": "page_contract",
            "order": 2,
            "type": "object",
            "label": "Podatki o podjetju",
            "required": True,
            "show_if": None,
            "hide_if": None,
            "settings": {
                "attributes": [
                    {"attribute_name": "name", "label": "Ime podjetja", "type": "text", "required": True, "settings": {"multiline": False, "min_length": None, "max_length": None}},
                    {"attribute_name": "address", "label": "Naslov podjetja", "type": "text", "required": True, "settings": {"multiline": False, "min_length": None, "max_length": None}},
                ]
            },
        },
    ],
}


def test_full_example_three_pages():
    text = _text(FULL_EXAMPLE_JSON)
    assert "Stran 1: Osnovni podatki" in text
    assert "Stran 2: Pogoji pogodbe" in text
    assert "Stran 3: Določbe za določen čas" in text


def test_full_example_page_show_if():
    text = _text(FULL_EXAMPLE_JSON)
    assert "`contract_type` je enako `fixed_period`" in text


def test_full_example_variable_count():
    """All 4 variables should appear."""
    text = _text(FULL_EXAMPLE_JSON)
    for vname in ["employee_name", "contract_type", "duration_months", "company"]:
        assert f"`{vname}`" in text


def test_full_example_object_attrs():
    text = _text(FULL_EXAMPLE_JSON)
    assert "`name`" in text
    assert "`address`" in text
    assert "`Ime podjetja`" in text
    assert "`Naslov podjetja`" in text


def test_full_example_preview_publish():
    text = _text(FULL_EXAMPLE_JSON)
    assert "Preview" in text
    assert "Publish" in text


# ---------------------------------------------------------------------------
# 12. Multiselect
# ---------------------------------------------------------------------------

MULTISELECT_JSON = {
    "template_name": "Multiselect test",
    "language": "sl",
    "output_formats": ["pdf"],
    "pages": [
        {"page_id": "p1", "title": "Stran", "description": None, "order": 1, "show_if": None}
    ],
    "variables": [
        {
            "variable_name": "klavzule",
            "page_id": "p1",
            "order": 1,
            "type": "multiselect",
            "label": "Dodatne klavzule",
            "required": False,
            "show_if": None,
            "hide_if": None,
            "settings": {
                "options": [
                    {"label": "Zaupnost", "value": "confidentiality"},
                    {"label": "Konkurenca", "value": "non_compete"},
                ],
            },
        }
    ],
}


def test_multiselect():
    text = _text(MULTISELECT_JSON)
    assert "**Multiselect**" in text
    assert "`Zaupnost`" in text
    assert "`confidentiality`" in text
    assert "`Konkurenca`" in text
    assert "`non_compete`" in text


# ---------------------------------------------------------------------------
# 13. Condition with is_one_of operator
# ---------------------------------------------------------------------------

IS_ONE_OF_JSON = {
    "template_name": "is_one_of test",
    "language": "sl",
    "output_formats": ["pdf"],
    "pages": [
        {"page_id": "p1", "title": "Stran", "description": None, "order": 1, "show_if": None}
    ],
    "variables": [
        {
            "variable_name": "detail",
            "page_id": "p1",
            "order": 1,
            "type": "text",
            "label": "Detail",
            "required": False,
            "show_if": {
                "logic": "and",
                "conditions": [
                    {"variable": "lokacija", "operator": "is_one_of", "value": ["Ljubljana", "Maribor"]}
                ],
            },
            "hide_if": None,
            "settings": {"multiline": False, "min_length": None, "max_length": None},
        }
    ],
}


def test_is_one_of():
    text = _text(IS_ONE_OF_JSON)
    assert "je eden od" in text
    assert "`Ljubljana`" in text
    assert "`Maribor`" in text


# ---------------------------------------------------------------------------
# 14. Accept type
# ---------------------------------------------------------------------------

ACCEPT_JSON = {
    "template_name": "Accept test",
    "language": "sl",
    "output_formats": ["pdf"],
    "pages": [
        {"page_id": "p1", "title": "Stran", "description": None, "order": 1, "show_if": None}
    ],
    "variables": [
        {
            "variable_name": "potrjujem",
            "page_id": "p1",
            "order": 1,
            "type": "accept",
            "label": "Potrjujem pogoje.",
            "required": True,
            "show_if": None,
            "hide_if": None,
            "settings": {},
        }
    ],
}


def test_accept_type():
    text = _text(ACCEPT_JSON)
    assert "**Accept**" in text
    assert "Potrjujem pogoje." in text


# ---------------------------------------------------------------------------
# 15. Boolean condition value display
# ---------------------------------------------------------------------------

BOOL_COND_JSON = {
    "template_name": "Bool cond test",
    "language": "sl",
    "output_formats": ["pdf"],
    "pages": [
        {"page_id": "p1", "title": "Stran", "description": None, "order": 1, "show_if": None}
    ],
    "variables": [
        {
            "variable_name": "dovoljenje",
            "page_id": "p1",
            "order": 1,
            "type": "accept",
            "label": "Dovoljenje",
            "required": True,
            "show_if": {
                "logic": "and",
                "conditions": [
                    {"variable": "tujec", "operator": "equals", "value": True}
                ],
            },
            "hide_if": None,
            "settings": {},
        }
    ],
}


def test_boolean_condition_display():
    text = _text(BOOL_COND_JSON)
    assert "`tujec` je enako Da" in text

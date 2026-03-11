# DocuWise Interview JSON Specification

## Pregled

Ta dokument opisuje JSON strukturo, ki vsebuje vse podatke potrebne za pripravo vprasanj (interview) v DocuWise GUI. JSON generira LLM na podlagi Word predloge (.docx), nato pa BrowserUse na podlagi tega JSONa avtomatsko konfigurira vprasanja v DocuWise aplikaciji.

---

## Vrhnji nivo (root)

```json
{
  "template_name": "Pogodba o zaposlitvi",
  "language": "sl",
  "output_formats": ["pdf", "docx"],
  "pages": [...],
  "variables": [...]
}
```

| Polje | Tip | Obvezno | Opis |
|---|---|---|---|
| `template_name` | string | da | Ime predloge / workflow-a v DocuWise |
| `language` | string | da | Jezik intervjuja. Vrednosti: `"sl"`, `"en"` |
| `output_formats` | string[] | da | Formati izhodnega dokumenta. Mozne vrednosti: `"pdf"`, `"docx"` |
| `pages` | Page[] | da | Seznam strani intervjuja (vsaj 1) |
| `variables` | Variable[] | da | Seznam vseh spremenljivk / vprasanj |

---

## Page (stran intervjuja)

Vsaka stran predstavlja logicno skupino vprasanj v intervjuju.

```json
{
  "page_id": "page_1",
  "title": "Podatki o zaposlenem",
  "description": "Vnesite osnovne podatke o zaposlenem.",
  "order": 1,
  "show_if": null
}
```

| Polje | Tip | Obvezno | Opis |
|---|---|---|---|
| `page_id` | string | da | Unikaten identifikator strani. Uporablja se za referenco v `variables[].page_id`. |
| `title` | string | da | Naslov strani, ki se prikaze uporabniku |
| `description` | string \| null | ne | Dodatna razlaga ali navodila za uporabnika na tej strani |
| `order` | integer | da | Zaporedna stevilka strani (1, 2, 3...). Doloca vrstni red prikazovanja. |
| `show_if` | Condition \| null | ne | Pogoj za prikaz celotne strani. Ce `null`, je stran vedno vidna. |

---

## Variable (spremenljivka / vprasanje)

Vsaka spremenljivka predstavlja eno vprasanje v intervjuju. Spremenljivka se navezuje na placeholder v Word predlogi (npr. `{{ employee_name }}`).

### Skupna polja (veljajo za vse tipe)

```json
{
  "variable_name": "employee_name",
  "page_id": "page_1",
  "order": 1,
  "type": "text",
  "label": "Ime in priimek zaposlenega",
  "required": true,
  "show_if": null,
  "hide_if": null,
  "settings": {}
}
```

| Polje | Tip | Obvezno | Opis |
|---|---|---|---|
| `variable_name` | string | da | Ime spremenljivke, kot je zapisano v Word predlogi (brez `{{ }}`). Samo crke, stevilke in podrtaji. |
| `page_id` | string | da | Referenca na `page_id` strani, kamor spada to vprasanje |
| `order` | integer | da | Vrstni red vprasanja znotraj strani (1, 2, 3...) |
| `type` | string | da | Tip vprasanja. Mozne vrednosti: `"text"`, `"number"`, `"date"`, `"yes_no"`, `"accept"`, `"select"`, `"multiselect"`, `"object"`, `"list"` |
| `label` | string | da | Besedilo vprasanja oz. oznaka, ki jo vidi uporabnik |
| `required` | boolean | da | Ali je vprasanje obvezno |
| `show_if` | Condition \| null | ne | Pogoj za prikaz vprasanja. Ce `null`, je vprasanje vedno vidno (razen ce stran sama ima pogoj). |
| `hide_if` | Condition \| null | ne | Pogoj za skrivanje vprasanja. Uporabi bodisi `show_if` bodisi `hide_if`, ne obojega. |
| `settings` | object | da | Nastavitve specificne za posamezen tip vprasanja. Struktura je odvisna od `type`. |

---

## Settings po tipih

### type: `"text"`

```json
{
  "settings": {
    "multiline": false,
    "min_length": null,
    "max_length": null
  }
}
```

| Polje | Tip | Privzeto | Opis |
|---|---|---|---|
| `multiline` | boolean | `false` | Ali naj se prikaze vecvrsticno vnosno polje |
| `min_length` | integer \| null | `null` | Minimalno stevilo znakov. `null` = brez omejitve. |
| `max_length` | integer \| null | `null` | Maksimalno stevilo znakov. `null` = brez omejitve. |

---

### type: `"number"`

```json
{
  "settings": {
    "unit": "EUR",
    "is_float": true,
    "min_value": null,
    "max_value": null
  }
}
```

| Polje | Tip | Privzeto | Opis |
|---|---|---|---|
| `unit` | string \| null | `null` | Enota, ki se prikaze ob vnosu (npr. `"EUR"`, `"kg"`, `"ur"`, `"m2"`). Samo za prikaz, ne vstavi se v dokument. |
| `is_float` | boolean | `false` | Ali so dovoljene decimalne vrednosti. `false` = samo cela stevila. |
| `min_value` | number \| null | `null` | Minimalna dovoljena vrednost. `null` = brez omejitve. |
| `max_value` | number \| null | `null` | Maksimalna dovoljena vrednost. `null` = brez omejitve. |

---

### type: `"date"`

```json
{
  "settings": {
    "date_format": "dd. MM. yyyy",
    "locale": "sl"
  }
}
```

| Polje | Tip | Privzeto | Opis |
|---|---|---|---|
| `date_format` | string | `"dd. MM. yyyy"` | Format datuma v izhodnem dokumentu. Mozne vrednosti: `"dd. MM. yyyy"`, `"d. MMMM yyyy"`, `"MM/dd/yyyy"`, `"MMMM d, yyyy"` |
| `locale` | string | `"sl"` | Lokalizacija datuma. Vrednosti: `"sl"`, `"en"` |

---

### type: `"yes_no"`

```json
{
  "settings": {
    "yes_label": "Da",
    "no_label": "Ne"
  }
}
```

| Polje | Tip | Privzeto | Opis |
|---|---|---|---|
| `yes_label` | string | `"Da"` | Besedilo za pritrdilno opcijo (npr. `"Da, imam"`, `"Yes"`) |
| `no_label` | string | `"Ne"` | Besedilo za nikalno opcijo (npr. `"Ne, nimam"`, `"No"`) |

---

### type: `"accept"`

```json
{
  "settings": {}
}
```

Accept nima dodatnih nastavitev. Prikaze se kot checkbox, ki ga uporabnik obkljuka ali ne. Vrednost je `true` (obkljukano) ali `false` (neobkljukano).

---

### type: `"select"`

```json
{
  "settings": {
    "display_type": "dropdown",
    "options": [
      { "label": "Za dolocen cas", "value": "fixed_period" },
      { "label": "Za nedolocen cas", "value": "indefinite" }
    ]
  }
}
```

| Polje | Tip | Privzeto | Opis |
|---|---|---|---|
| `display_type` | string | `"dropdown"` | Nacin prikaza. Vrednosti: `"dropdown"`, `"radio"` |
| `options` | Option[] | - | Seznam moznih izbir (vsaj 2) |

**Option:**

| Polje | Tip | Opis |
|---|---|---|
| `label` | string | Besedilo, ki ga vidi uporabnik |
| `value` | string | Vrednost, ki se uporabi v predlogi. Mora ustrezati vrednostim v pogojih Word predloge (npr. `{% if duration == "fixed_period" %}`). |

---

### type: `"multiselect"`

```json
{
  "settings": {
    "options": [
      { "label": "Klavzula o zaupnosti", "value": "confidentiality" },
      { "label": "Konkurencna prepoved", "value": "non_compete" },
      { "label": "Arbitraza", "value": "arbitration" }
    ]
  }
}
```

| Polje | Tip | Opis |
|---|---|---|
| `options` | Option[] | Seznam moznih izbir. Uporabnik lahko izbere vec. Enaka struktura kot pri `select`. |

---

### type: `"object"`

Object grupira vec povezanih atributov v eno logicno enoto. Atributi se NE ekstrahirajo samodejno iz predloge - definirati jih je treba rocno.

```json
{
  "settings": {
    "attributes": [
      {
        "attribute_name": "name",
        "label": "Ime podjetja",
        "type": "text",
        "required": true,
        "settings": {}
      },
      {
        "attribute_name": "address",
        "label": "Naslov podjetja",
        "type": "text",
        "required": true,
        "settings": { "multiline": true, "min_length": null, "max_length": null }
      },
      {
        "attribute_name": "industry",
        "label": "Panoga",
        "type": "select",
        "required": false,
        "settings": {
          "display_type": "dropdown",
          "options": [
            { "label": "Zdravstvo", "value": "Healthcare" },
            { "label": "Tehnologija", "value": "Technology" }
          ]
        }
      }
    ]
  }
}
```

| Polje | Tip | Opis |
|---|---|---|
| `attributes` | Attribute[] | Seznam atributov (pod-spremenljivk) objekta |

**Attribute:**

| Polje | Tip | Obvezno | Opis |
|---|---|---|---|
| `attribute_name` | string | da | Ime atributa. V predlogi se uporablja kot `{{ object_name.attribute_name }}`. |
| `label` | string | da | Oznaka, ki jo vidi uporabnik |
| `type` | string | da | Tip atributa. Enake moznosti kot pri spremenljivkah: `"text"`, `"number"`, `"date"`, `"yes_no"`, `"accept"`, `"select"`, `"multiselect"`. NE more biti `"object"` ali `"list"`. |
| `required` | boolean | da | Ali je atribut obvezen (neodvisno od tega ali je objekt sam obvezen) |
| `settings` | object | da | Nastavitve za ta atribut - enaka struktura kot `settings` za ustrezni tip spremenljivke |

---

### type: `"list"`

List omogoca uporabniku, da doda vec instanc istega tipa podatka (npr. vec otrok, vec nepremicnin).

```json
{
  "settings": {
    "min_items": 1,
    "max_items": null,
    "attributes": [
      {
        "attribute_name": "name",
        "label": "Ime otroka",
        "type": "text",
        "required": true,
        "settings": {}
      },
      {
        "attribute_name": "age",
        "label": "Starost",
        "type": "number",
        "required": true,
        "settings": { "unit": null, "is_float": false, "min_value": 0, "max_value": 100 }
      },
      {
        "attribute_name": "gender",
        "label": "Spol",
        "type": "select",
        "required": true,
        "settings": {
          "display_type": "radio",
          "options": [
            { "label": "Moski", "value": "male" },
            { "label": "Zenski", "value": "female" }
          ]
        }
      }
    ]
  }
}
```

| Polje | Tip | Privzeto | Opis |
|---|---|---|---|
| `min_items` | integer \| null | `null` | Minimalno stevilo elementov, ki jih mora uporabnik dodati. `null` = brez omejitve. |
| `max_items` | integer \| null | `null` | Maksimalno stevilo elementov. `null` = brez omejitve. |
| `attributes` | Attribute[] | - | Seznam atributov posameznega elementa seznama. Enaka struktura kot pri `object`. V predlogi se uporabljajo z `{{ item.attribute_name }}` znotraj `{% for item in list_name %}` zanke. |

---

## Condition (pogoj za show_if / hide_if)

Pogoji dolocajo, kdaj se vprasanje ali stran prikaze/skrije. Pogoj se lahko nanasa samo na spremenljivke, ki so v intervjuju ZE PRED trenutnim vprasanjem/stranjo.

### Enostaven pogoj

```json
{
  "logic": "and",
  "conditions": [
    {
      "variable": "contract_type",
      "operator": "equals",
      "value": "fixed_period"
    }
  ]
}
```

### Sestavljen pogoj (vec pogojev)

```json
{
  "logic": "or",
  "conditions": [
    {
      "variable": "office_location",
      "operator": "equals",
      "value": "headquarters"
    },
    {
      "variable": "employee_role",
      "operator": "equals",
      "value": "remote"
    }
  ]
}
```

| Polje | Tip | Opis |
|---|---|---|
| `logic` | string | Logicni operator med pogoji. Vrednosti: `"and"`, `"or"`. Ce je samo en pogoj, je vseeno. **DocuWise ne podpira mesanja AND in OR v istem nizu.** |
| `conditions` | ConditionItem[] | Seznam posameznih pogojev (vsaj 1) |

**ConditionItem:**

| Polje | Tip | Opis |
|---|---|---|
| `variable` | string | Ime spremenljivke, na katero se pogoj nanasa. Mora biti spremenljivka, ki se v intervjuju pojavi PRED tem vprasanjem/stranjo. |
| `operator` | string | Operator primerjave. Mozne vrednosti: `"equals"`, `"not_equals"`, `"greater_than"`, `"less_than"`, `"greater_or_equal"`, `"less_or_equal"`, `"is_one_of"` |
| `value` | string \| number \| boolean \| string[] | Vrednost za primerjavo. Pri `"is_one_of"` je to seznam stringov (array). Pri yes_no spremenljivkah je to `true` ali `false`. |

---

## Celoten primer

Spodaj je celoten primer JSON za preprost intervju pogodbe o zaposlitvi:

```json
{
  "template_name": "Pogodba o zaposlitvi",
  "language": "sl",
  "output_formats": ["pdf", "docx"],
  "pages": [
    {
      "page_id": "page_basic",
      "title": "Osnovni podatki",
      "description": "Vnesite podatke o zaposlenem.",
      "order": 1,
      "show_if": null
    },
    {
      "page_id": "page_contract",
      "title": "Pogoji pogodbe",
      "description": null,
      "order": 2,
      "show_if": null
    },
    {
      "page_id": "page_fixed_term",
      "title": "Dolocbe za dolocen cas",
      "description": "Izpolnite podatke o trajanju pogodbe.",
      "order": 3,
      "show_if": {
        "logic": "and",
        "conditions": [
          {
            "variable": "contract_type",
            "operator": "equals",
            "value": "fixed_period"
          }
        ]
      }
    }
  ],
  "variables": [
    {
      "variable_name": "employee_name",
      "page_id": "page_basic",
      "order": 1,
      "type": "text",
      "label": "Ime in priimek zaposlenega",
      "required": true,
      "show_if": null,
      "hide_if": null,
      "settings": {
        "multiline": false,
        "min_length": null,
        "max_length": 100
      }
    },
    {
      "variable_name": "employee_salary",
      "page_id": "page_basic",
      "order": 2,
      "type": "number",
      "label": "Bruto placa",
      "required": true,
      "show_if": null,
      "hide_if": null,
      "settings": {
        "unit": "EUR",
        "is_float": true,
        "min_value": 1253.90,
        "max_value": null
      }
    },
    {
      "variable_name": "start_date",
      "page_id": "page_basic",
      "order": 3,
      "type": "date",
      "label": "Datum zacetka dela",
      "required": true,
      "show_if": null,
      "hide_if": null,
      "settings": {
        "date_format": "dd. MM. yyyy",
        "locale": "sl"
      }
    },
    {
      "variable_name": "is_foreigner",
      "page_id": "page_basic",
      "order": 4,
      "type": "yes_no",
      "label": "Ali je zaposleni tujec?",
      "required": true,
      "show_if": null,
      "hide_if": null,
      "settings": {
        "yes_label": "Da",
        "no_label": "Ne"
      }
    },
    {
      "variable_name": "work_permit_accepted",
      "page_id": "page_basic",
      "order": 5,
      "type": "accept",
      "label": "Potrjujem, da ima zaposleni veljavno delovno dovoljenje.",
      "required": true,
      "show_if": {
        "logic": "and",
        "conditions": [
          {
            "variable": "is_foreigner",
            "operator": "equals",
            "value": true
          }
        ]
      },
      "hide_if": null,
      "settings": {}
    },
    {
      "variable_name": "contract_type",
      "page_id": "page_contract",
      "order": 1,
      "type": "select",
      "label": "Vrsta pogodbe",
      "required": true,
      "show_if": null,
      "hide_if": null,
      "settings": {
        "display_type": "radio",
        "options": [
          { "label": "Za dolocen cas", "value": "fixed_period" },
          { "label": "Za nedolocen cas", "value": "indefinite" }
        ]
      }
    },
    {
      "variable_name": "selected_provisions",
      "page_id": "page_contract",
      "order": 2,
      "type": "multiselect",
      "label": "Dodatne dolocbe v pogodbi",
      "required": false,
      "show_if": null,
      "hide_if": null,
      "settings": {
        "options": [
          { "label": "Konkurencna klavzula", "value": "non_compete" },
          { "label": "Klavzula o zaupnosti", "value": "confidentiality" },
          { "label": "Sluzbeni avtomobil", "value": "company_car" }
        ]
      }
    },
    {
      "variable_name": "duration_months",
      "page_id": "page_fixed_term",
      "order": 1,
      "type": "number",
      "label": "Trajanje pogodbe v mesecih",
      "required": true,
      "show_if": null,
      "hide_if": null,
      "settings": {
        "unit": "mesecev",
        "is_float": false,
        "min_value": 1,
        "max_value": 24
      }
    },
    {
      "variable_name": "end_date",
      "page_id": "page_fixed_term",
      "order": 2,
      "type": "date",
      "label": "Datum prenehanja pogodbe",
      "required": true,
      "show_if": null,
      "hide_if": null,
      "settings": {
        "date_format": "dd. MM. yyyy",
        "locale": "sl"
      }
    },
    {
      "variable_name": "company",
      "page_id": "page_contract",
      "order": 3,
      "type": "object",
      "label": "Podatki o podjetju",
      "required": true,
      "show_if": null,
      "hide_if": null,
      "settings": {
        "attributes": [
          {
            "attribute_name": "name",
            "label": "Ime podjetja",
            "type": "text",
            "required": true,
            "settings": { "multiline": false, "min_length": null, "max_length": null }
          },
          {
            "attribute_name": "address",
            "label": "Naslov podjetja",
            "type": "text",
            "required": true,
            "settings": { "multiline": false, "min_length": null, "max_length": null }
          },
          {
            "attribute_name": "registration_number",
            "label": "Maticna stevilka",
            "type": "text",
            "required": true,
            "settings": { "multiline": false, "min_length": null, "max_length": 10 }
          }
        ]
      }
    },
    {
      "variable_name": "children",
      "page_id": "page_basic",
      "order": 6,
      "type": "list",
      "label": "Otroci zaposlenega",
      "required": false,
      "show_if": null,
      "hide_if": null,
      "settings": {
        "min_items": null,
        "max_items": 10,
        "attributes": [
          {
            "attribute_name": "name",
            "label": "Ime otroka",
            "type": "text",
            "required": true,
            "settings": { "multiline": false, "min_length": null, "max_length": null }
          },
          {
            "attribute_name": "date_of_birth",
            "label": "Datum rojstva",
            "type": "date",
            "required": true,
            "settings": { "date_format": "dd. MM. yyyy", "locale": "sl" }
          }
        ]
      }
    }
  ]
}
```

---

## Pravila za LLM pri generiranju JSONa

1. **`variable_name`** mora tocno ustrezati imenu spremenljivke v Word predlogi (brez `{{ }}`, brez presledkov).
2. **`value` v `options`** pri `select` in `multiselect` mora tocno ustrezati vrednostim v pogojih Word predloge (npr. ce predloga vsebuje `{% if contract_type == "fixed_period" %}`, mora biti value `"fixed_period"`).
3. **Atributi** pri `object` in `list` se NE ekstrahirajo samodejno - LLM jih mora eksplicitno navesti. Ime atributa mora ustrezati tistemu za piko v predlogi (npr. `{{ company.name }}` -> `attribute_name: "name"`).
4. **`show_if` pogoji** se lahko nanasajo samo na spremenljivke, ki so v intervjuju PRED trenutnim vprasanjem (glede na `page.order` in `variable.order`).
5. Ne mesaj `"and"` in `"or"` v istem pogoju - DocuWise tega ne podpira. Ce je potrebna kompleksna logika, ustvari vmesno yes_no spremenljivko.
6. Uporabi `show_if` ALI `hide_if`, ne obojega hkrati na istem vprasanju.
7. Vsi `page_id` referencirani v `variables` morajo obstajati v seznamu `pages`.
8. Znotraj iste strani ne sme biti dveh spremenljivk z enakim `order`.

---

## Navodila za BrowserUse

BrowserUse naj JSON procesira v naslednjem vrstnem redu:

1. **Ustvari strani** (`pages`) v pravilnem vrstnem redu, nastavi naslove in opise.
2. **Premakni spremenljivke** na ustrezne strani (glede na `page_id`).
3. **Nastavi vrstni red** spremenljivk znotraj vsake strani (glede na `order`).
4. **Za vsako spremenljivko:**
   - Nastavi tip (`type`)
   - Nastavi oznako (`label`)
   - Nastavi `required`
   - Vnesi nastavitve iz `settings` (specificne za tip)
   - Ce ima `show_if` ali `hide_if`, nastavi pogoj
5. **Za `object` in `list` tipe:** rocno dodaj atribute enega za drugim.
6. **Za strani s `show_if`:** nastavi pogoj na nivoju strani.

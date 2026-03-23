from collections import OrderedDict


MADE_FROM_INTERNAL_ATTRIBUTE_KEYS = [
    "BAL_SAP_STPO_ROMS1",
    "BAL_SAP_STPO_ROMS2",
    "BAL_SAP_STPO_ROMS3",
    "BAL_SAP_STPO_ROMEI",
    "BAL_SAP_STPO_ROMEN",
    "BAL_SAP_STPO_ROKME",
    "BAL_SAP_STPO_ROANZ",
    "BAL_SAP_STPO_ROAME",
]


MADE_FROM_USAGE_KEY_ALIASES = {
    "BAL_SAP_STPO_ROMS1": ["BAL_SAP_STPO_ROMS1", "BALSAPSTPOROMS1"],
    "BAL_SAP_STPO_ROMS2": ["BAL_SAP_STPO_ROMS2", "BALSAPSTPOROMS2"],
    "BAL_SAP_STPO_ROMS3": ["BAL_SAP_STPO_ROMS3", "BALSAPSTPOROMS3"],
    "BAL_SAP_STPO_ROMEI": ["BAL_SAP_STPO_ROMEI", "BALSAPSTPOROMEI"],
    "BAL_SAP_STPO_ROMEN": ["BAL_SAP_STPO_ROMEN", "BALSAPSTPOROMEN"],
    "BAL_SAP_STPO_ROKME": ["BAL_SAP_STPO_ROKME", "BALSAPSTPOROKME"],
    "BAL_SAP_STPO_ROANZ": ["BAL_SAP_STPO_ROANZ", "BALSAPSTPOROANZ"],
    "BAL_SAP_STPO_ROAME": ["BAL_SAP_STPO_ROAME", "BALSAPSTPOROAME"],
}


def _has_made_from_usage(node: dict) -> bool:
    """Prüft, ob ein Knoten MadeFrom-Usage-Attribute enthält."""
    usage = node.get("usage_attributes")
    if not isinstance(usage, dict):
        return False

    for key in MADE_FROM_INTERNAL_ATTRIBUTE_KEYS:
        value = usage.get(key)
        if value not in (None, "", []):
            return True
    return False


def _infer_children_type(node: dict) -> str:
    """Ermittelt children_type: 'makes' für MadeFrom, sonst 'subassembly'."""
    children = node.get("children")
    if not isinstance(children, list):
        return "subassembly"

    if not children:
        return "no additional children"

    if children:
        has_line_number = any(
            isinstance(child, dict) and child.get("line_number") not in (None, "")
            for child in children
        )
        has_made_from_child = any(
            isinstance(child, dict) and _has_made_from_usage(child)
            for child in children
        )

        if (not has_line_number) and has_made_from_child:
            return "makes"
        return "subassembly"

    return "subassembly"


def _ensure_action_first(node: OrderedDict) -> None:
    """Setzt action als erstes Feld für Part-/Document-Objekte."""
    node_type = node.get("type")
    if not isinstance(node_type, str):
        return

    if node_type != "WTPart" and "Document" not in node_type:
        return

    action_value = node.get("action", "undefined")
    reordered_items = [("action", action_value)]
    reordered_items.extend((k, v) for k, v in node.items() if k != "action")
    node.clear()
    node.update(reordered_items)


def _normalize_value(value):
    """Normalisiert OData-Werte auf JSON-freundliche Python-Werte."""
    if isinstance(value, dict):
        if "Value" in value:
            return value.get("Value")
        if "Display" in value:
            return value.get("Display")
        return {k: _normalize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_value(v) for v in value]
    return value


def _normalize_made_from_numbers(raw_value) -> list[str]:
    """Normalisiert BALMADEFROMNUMBER auf eine Liste von Nummern."""
    normalized = _normalize_value(raw_value)

    if normalized is None:
        return []
    if isinstance(normalized, list):
        return [str(v).strip() for v in normalized if str(v).strip()]

    text = str(normalized).strip()
    if not text:
        return []
    return [text]


def _normalize_made_from_attribute_value(value):
    """Normalisiert MadeFrom-Attributwerte auf Single-Value (statt Listen)."""
    normalized = _normalize_value(value)

    if isinstance(normalized, list):
        compact = [v for v in normalized if v not in ("", None)]
        if not compact:
            return None
        return compact[0]

    return normalized


def _reorder_usage_before_children(node: OrderedDict) -> None:
    """Normalisiert Reihenfolge: action zuerst, children_type vor children (rekursiv)."""
    if not isinstance(node, dict):
        return

    _ensure_action_first(node)

    if "children" in node:
        usage_present = "usage_attributes" in node
        usage_value = node.get("usage_attributes")
        children_value = node.get("children")
        children_type_value = node.get("children_type") or _infer_children_type(node)

        reordered_items = []
        inserted_children_block = False

        for key, value in node.items():
            if key in ("usage_attributes", "children_type", "children"):
                if key == "children" and not inserted_children_block:
                    if usage_present:
                        reordered_items.append(("usage_attributes", usage_value))
                    reordered_items.append(("children_type", children_type_value))
                    reordered_items.append(("children", children_value))
                    inserted_children_block = True
                continue

            reordered_items.append((key, value))

        if not inserted_children_block:
            if usage_present:
                reordered_items.append(("usage_attributes", usage_value))
            reordered_items.append(("children_type", children_type_value))
            reordered_items.append(("children", children_value))

        node.clear()
        node.update(reordered_items)

    for value in node.values():
        if isinstance(value, dict):
            _reorder_usage_before_children(value)
        elif isinstance(value, list):
            for entry in value:
                if isinstance(entry, dict):
                    _reorder_usage_before_children(entry)


def _extract_made_from_relation_attributes(
    part: dict,
    extra_attributes: dict | None = None,
) -> OrderedDict:
    """Sammelt normalisierte MadeFrom-Relationattribute (inkl. STPO-Mapping)."""
    relation_attributes = OrderedDict()

    for key, value in part.items():
        upper = key.upper()
        if upper.startswith("BALMADEFROM") and upper != "BALMADEFROMNUMBER":
            normalized = _normalize_made_from_attribute_value(value)
            if normalized not in ("", None, []):
                relation_attributes[key] = normalized

    for canonical_key, aliases in MADE_FROM_USAGE_KEY_ALIASES.items():
        for alias in aliases:
            if alias in part:
                normalized = _normalize_made_from_attribute_value(part.get(alias))
                if normalized not in ("", None, []):
                    relation_attributes[canonical_key] = normalized
                    break

    if extra_attributes:
        normalized_extra = {}
        for key, value in extra_attributes.items():
            normalized = _normalize_made_from_attribute_value(value)
            if normalized in ("", None, []):
                continue
            normalized_extra[key] = normalized

        for canonical_key, aliases in MADE_FROM_USAGE_KEY_ALIASES.items():
            if canonical_key in normalized_extra:
                relation_attributes[canonical_key] = normalized_extra[canonical_key]
                continue
            for alias in aliases:
                if alias in normalized_extra:
                    relation_attributes[canonical_key] = normalized_extra[alias]
                    break

        for key, value in normalized_extra.items():
            if key not in relation_attributes:
                relation_attributes[key] = value

    return relation_attributes


def _build_made_from_structure(part: dict, extra_attributes: dict | None = None) -> list[OrderedDict]:
    """Erstellt MadeFrom als Liste flacher Objekte je Eintrag."""
    numbers = _normalize_made_from_numbers(part.get("BALMADEFROMNUMBER", ""))
    relation_attributes = _extract_made_from_relation_attributes(part, extra_attributes)

    made_from = []
    for number in numbers:
        item = OrderedDict()
        item["made_from_nummer"] = number
        for attr_key, attr_value in relation_attributes.items():
            item[attr_key] = attr_value
        made_from.append(item)

    return made_from


def _build_made_from_subtrees(
    client,
    numbers: list[str],
    relation_attributes: OrderedDict,
    depth: int,
    visited: set,
    read_wt_documents: bool,
    read_cad_documents: bool,
) -> list[OrderedDict]:
    """Erzeugt MadeFrom als zusätzliche BOM-Ebene im selben Knotenschema wie children."""
    subtrees = []

    default_quantity = relation_attributes.get("BAL_SAP_STPO_ROANZ", 1.0)
    default_unit = relation_attributes.get("BAL_SAP_STPO_ROAME", "")

    for made_from_number in numbers:
        try:
            subtree = client.build_bom_tree(
                made_from_number,
                depth=depth + 1,
                visited=visited.copy(),
                read_wt_documents=read_wt_documents,
                read_cad_documents=read_cad_documents,
            )
        except Exception:
            subtree = OrderedDict([
                ("type", "WTPart"),
                ("number", made_from_number),
                ("name", ""),
                ("error", "MadeFrom-Part konnte nicht aufgelöst werden"),
            ])

        is_cycle_placeholder = "hinweis" in subtree

        if not is_cycle_placeholder:
            usage_attrs = subtree.get("usage_attributes")
            if not isinstance(usage_attrs, dict):
                usage_attrs = OrderedDict()
            else:
                usage_attrs = OrderedDict(usage_attrs)

            for key, value in relation_attributes.items():
                if usage_attrs.get(key) in ("", None, []):
                    usage_attrs[key] = value

            if usage_attrs:
                subtree["usage_attributes"] = usage_attrs

        if "quantity" not in subtree and default_quantity not in ("", None, []):
            subtree["quantity"] = default_quantity
        if "quantity_unit" not in subtree and default_unit not in ("", None, []):
            subtree["quantity_unit"] = str(default_unit)

        subtree_children = subtree.get("children")
        if isinstance(subtree_children, list):
            if subtree_children:
                subtree["children_type"] = "makes"
            else:
                subtree["children_type"] = "no additional children"

        _reorder_usage_before_children(subtree)

        subtrees.append(subtree)

    return subtrees


def get_bom_children(client, part_id: str, debug: bool = False) -> list:
    """BOM-Kinder eines Parts abrufen."""
    nav_options = [
        "Uses",
        "UsesInterface",
        "BOMComponents",
        "PartStructure",
    ]

    if client._bom_nav_strategy:
        nav, use_expand = client._bom_nav_strategy
        url = f"{client.odata_base}/ProdMgmt/Parts('{part_id}')/{nav}"
        params = {"$expand": "Uses"} if use_expand else None
        result = client._try_get_all_pages(url, params)
        if result is not None:
            if debug:
                print(f"    BOM via '{nav}' (cached strategy): {len(result)} Einträge")
            return result
        client._bom_nav_strategy = None

    for nav in nav_options:
        url = f"{client.odata_base}/ProdMgmt/Parts('{part_id}')/{nav}"

        result = client._try_get_all_pages(url, {"$expand": "Uses"})
        if result is not None:
            if debug:
                print(f"    BOM via '{nav}' ($expand): {len(result)} Einträge")
            client._bom_nav_strategy = (nav, True)
            return result

        result = client._try_get_all_pages(url)
        if result is not None:
            if debug:
                print(f"    BOM via '{nav}': {len(result)} Einträge")
            client._bom_nav_strategy = (nav, False)
            return result

    if debug:
        print("    Keine BOM-Kinder gefunden (alle Nav-Properties versucht)")
    return []


def resolve_usage_link_child(client, link: dict) -> dict | None:
    """Child-Part aus einem UsageLink auflösen."""
    for key in ["Uses", "RoleBObject", "Child", "Part"]:
        child = link.get(key)
        if isinstance(child, dict) and ("Number" in child or "ID" in child):
            return child

    link_id = link.get("ID", "")
    if link_id:
        if client._usage_link_nav:
            url = (
                f"{client.odata_base}/ProdMgmt/UsageLinks('{link_id}')"
                f"/{client._usage_link_nav}"
            )
            try:
                data = client._get_json(url)
                if "value" in data and isinstance(data["value"], list):
                    return data["value"][0] if data["value"] else None
                if "ID" in data or "Number" in data:
                    return data
            except Exception:
                client._usage_link_nav = None

        for nav in ["Uses", "RoleBObject", "Child"]:
            url = f"{client.odata_base}/ProdMgmt/UsageLinks('{link_id}')/{nav}"
            try:
                data = client._get_json(url)
                if "value" in data and isinstance(data["value"], list):
                    if data["value"]:
                        client._usage_link_nav = nav
                        return data["value"][0]
                    continue
                if "ID" in data or "Number" in data:
                    client._usage_link_nav = nav
                    return data
            except Exception:
                continue

    return None


def build_bom_tree(
    client,
    part_number: str,
    progress,
    max_bom_depth: int,
    depth: int = 0,
    visited: set = None,
    read_wt_documents: bool = True,
    read_cad_documents: bool = True,
    debug: bool = False,
) -> OrderedDict:
    """Rekursiv die BOM-Hierarchie aufbauen. Dokumente/CAD optional."""
    if visited is None:
        visited = set()

    indent = "  " * depth
    print(f"\n{indent}{'━' * 50}")
    print(f"{indent}├─ Part: {part_number}")
    progress.set_phase(f"Part {part_number}")
    if not debug:
        progress.print_status()

    try:
        part = client.find_part(part_number)
    except ValueError as e:
        print(f"{indent}   ✗ {e}")
        return OrderedDict([
            ("action", "undefined"),
            ("type", "WTPart"),
            ("number", part_number),
            ("name", ""),
            ("error", str(e)),
        ])

    part_id = part.get("ID", part.get("id", ""))
    if not part_id:
        odata_id = part.get("@odata.id", "")
        if "Parts('" in odata_id:
            part_id = odata_id.split("Parts('")[1].rstrip("')")

    number = part.get("Number", part.get("PartNumber", part_number))
    name = part.get("Name", part.get("DisplayName", ""))
    version = part.get("Version", part.get("VersionID", ""))
    iteration = part.get("Iteration", part.get("IterationID", ""))

    state_raw = part.get("State", part.get("LifeCycleState", ""))
    if isinstance(state_raw, dict):
        state = state_raw.get("Value", state_raw.get("Display", str(state_raw)))
    else:
        state = str(state_raw) if state_raw else ""

    identity = part.get("Identity", part.get("DisplayIdentity", ""))

    print(f"{indent}   Name: {name}")
    print(f"{indent}   Version: {version}.{iteration}")
    print(f"{indent}   State: {state}")
    print(f"{indent}   ID: {part_id}")

    if part_id and part_id in visited:
        print(f"{indent}   ⚠ Zirkuläre Referenz – übersprungen")
        return OrderedDict([
            ("action", "undefined"),
            ("type", "WTPart"),
            ("number", number),
            ("name", name),
            ("version", version),
            ("hinweis", "Zirkuläre Referenz – nicht erneut aufgelöst"),
        ])

    if part_id:
        visited.add(part_id)

    if depth >= max_bom_depth:
        print(f"{indent}   ⚠ Max. Tiefe erreicht")
        return OrderedDict([
            ("action", "undefined"),
            ("type", "WTPart"),
            ("number", number),
            ("name", name),
            ("version", version),
            ("hinweis", "Maximale BOM-Tiefe erreicht"),
        ])

    node = OrderedDict()
    node["type"] = "WTPart"
    node["number"] = number
    node["name"] = name
    node["version"] = version
    node["iteration"] = iteration
    node["state"] = state
    node["identity"] = identity

    suffix_raw = part.get("BALSUFFIX", part.get("BAL_SUFFIX", ""))
    binding_raw = part.get("BALBINDING", part.get("BAL_BINDING", ""))

    if isinstance(suffix_raw, list):
        suffix_raw = suffix_raw[0] if suffix_raw else ""
    if isinstance(binding_raw, list):
        binding_raw = binding_raw[0] if binding_raw else ""
    if isinstance(suffix_raw, dict):
        suffix_raw = suffix_raw.get("Value", str(suffix_raw))
    if isinstance(binding_raw, dict):
        binding_raw = binding_raw.get("Value", str(binding_raw))

    node["suffix"] = str(suffix_raw) if suffix_raw else ""
    node["binding"] = str(binding_raw) if binding_raw else ""
    print(
        f"{indent}   BALSUFFIX raw={part.get('BALSUFFIX', '?')} "
        f"→ suffix='{node['suffix']}'"
    )
    print(
        f"{indent}   BALBINDING raw={part.get('BALBINDING', '?')} "
        f"→ binding='{node['binding']}'"
    )

    made_from_soft_attrs = {}
    if part_id:
        try:
            made_from_soft_attrs = client.get_soft_attributes(
                part_id,
                MADE_FROM_INTERNAL_ATTRIBUTE_KEYS,
            )
        except Exception:
            made_from_soft_attrs = {}

    made_from_numbers = _normalize_made_from_numbers(part.get("BALMADEFROMNUMBER", ""))
    current_number_norm = str(number).strip().upper() if number else ""
    if current_number_norm:
        made_from_numbers = [
            mf_number
            for mf_number in made_from_numbers
            if str(mf_number).strip().upper() != current_number_norm
        ]
    made_from_relation_attrs = _extract_made_from_relation_attributes(part, made_from_soft_attrs)
    made_from_subtrees = _build_made_from_subtrees(
        client,
        numbers=made_from_numbers,
        relation_attributes=made_from_relation_attrs,
        depth=depth,
        visited=visited,
        read_wt_documents=read_wt_documents,
        read_cad_documents=read_cad_documents,
    )
    node["is_variant"] = part.get("BALISVARIANT", "")

    if part_id:
        progress.set_phase(f"BOM {number}")
        if not debug:
            progress.print_status()
        print(f"{indent}   Lade BOM-Kinder...")
        usage_links = client.get_bom_children(part_id)
        children = []

        if usage_links and depth == 0:
            progress.set_total_parts(len(usage_links) + 1)
            progress.tick_part(number)
            progress.print_status()

        for link in usage_links:
            qty_raw = link.get("Quantity", None)
            if isinstance(qty_raw, dict):
                quantity = qty_raw.get("Value", 1)
                unit = qty_raw.get("Unit", "")
            elif qty_raw is not None:
                quantity = qty_raw
                unit = ""
            else:
                quantity = 1
                unit = ""

            line_number = link.get("LineNumber", link.get("FindNumber", ""))

            child_part = client.resolve_usage_link_child(link)

            if child_part:
                child_number = None
                for key in ["Number", "PartNumber", "Name"]:
                    if key in child_part and child_part[key]:
                        child_number = child_part[key]
                        break

                child_id = child_part.get("ID", child_part.get("id", ""))

                if child_number:
                    progress.tick_part(child_number)
                    if not debug:
                        progress.print_status()
                    child_node = client.build_bom_tree(
                        child_number,
                        depth=depth + 1,
                        visited=visited.copy(),
                        read_wt_documents=read_wt_documents,
                        read_cad_documents=read_cad_documents,
                    )
                elif child_id:
                    detail = client.get_part_by_id(child_id)
                    if detail:
                        child_num = detail.get("Number", detail.get("PartNumber", ""))
                        if child_num:
                            child_node = client.build_bom_tree(
                                child_num,
                                depth=depth + 1,
                                visited=visited.copy(),
                                read_wt_documents=read_wt_documents,
                                read_cad_documents=read_cad_documents,
                            )
                        else:
                            child_node = OrderedDict([
                                ("type", "WTPart"),
                                ("id", child_id),
                                ("hinweis", "Part-Nummer nicht ermittelbar"),
                            ])
                    else:
                        child_node = OrderedDict([
                            ("type", "WTPart"),
                            ("id", child_id),
                            ("hinweis", "Part-Details nicht ladbar"),
                        ])
                else:
                    child_node = OrderedDict([
                        ("type", "WTPart"),
                        (
                            "raw_link",
                            {
                                k: str(v)[:80]
                                for k, v in link.items()
                                if not k.startswith("@")
                            },
                        ),
                        ("hinweis", "Child konnte nicht aufgelöst werden"),
                    ])
            else:
                child_node = OrderedDict([
                    ("type", "WTPart"),
                    (
                        "raw_link",
                        {
                            k: str(v)[:80]
                            for k, v in link.items()
                            if not k.startswith("@")
                        },
                    ),
                    ("hinweis", "Child konnte nicht aufgelöst werden"),
                ])

            child_node["quantity"] = quantity
            qty_unit = unit or ""
            if not qty_unit:
                qty_unit = link.get("Unit", link.get("QuantityUnit", ""))
                if isinstance(qty_unit, dict):
                    qty_unit = qty_unit.get("Value", str(qty_unit))
            child_node["quantity_unit"] = str(qty_unit)

            if line_number:
                child_node["line_number"] = str(line_number)

            usage_attrs = {}
            for key, value in link.items():
                if (
                    key not in ("Quantity", "Unit", "LineNumber", "FindNumber")
                    and not key.startswith("@")
                ):
                    if not isinstance(value, (dict, list)):
                        usage_attrs[key] = value
            if usage_attrs:
                child_node["usage_attributes"] = usage_attrs

            children.append(child_node)

        def _sort_key(c):
            ln = c.get("line_number", "")
            try:
                return (0, int(ln))
            except (ValueError, TypeError):
                return (1, ln)

        children.sort(key=_sort_key)

        node["children"] = made_from_subtrees + children

        if read_wt_documents:
            progress.set_phase(f"Docs {number}")
            if not debug:
                progress.print_status()
            docs = client.get_described_documents(part_id, part_number=number)
            if docs:
                by_source = {}
                for doc in docs:
                    src = doc.get("_source_nav", "unknown")
                    by_source[src] = by_source.get(src, 0) + 1
                src_detail = ", ".join(f"{k}: {v}" for k, v in by_source.items())
                print(f"{indent}   📄 {len(docs)} Dokument(e) ({src_detail})")
                doc_list = []
                for doc in docs:
                    d_state = doc.get("State", "")
                    if isinstance(d_state, dict):
                        d_state = d_state.get("Value", str(d_state))
                    doc_list.append(OrderedDict([
                        ("type", "WTDocument"),
                        ("number", doc.get("Number", "")),
                        ("name", doc.get("Name", "")),
                        ("version", doc.get("Version", "")),
                        ("state", str(d_state)),
                        ("identity", doc.get("Identity", "")),
                        ("source", doc.get("_source_nav", "")),
                    ]))
                node["documents"] = doc_list
                progress.tick_docs(len(doc_list))
            else:
                print(f"{indent}   📄 0 Dokument(e)")
                node["documents"] = []
        else:
            node["documents"] = []

        if read_cad_documents:
            progress.set_phase(f"CAD {number}")
            if not debug:
                progress.print_status()
            cad_docs = client.get_cad_documents(part_id)
            if cad_docs:
                by_source = {}
                for cad in cad_docs:
                    src = cad.get("_source_nav", "unknown")
                    by_source[src] = by_source.get(src, 0) + 1
                src_detail = ", ".join(f"{k}: {v}" for k, v in by_source.items())
                print(f"{indent}   📐 {len(cad_docs)} CAD-Dokument(e) ({src_detail})")
                cad_list = []
                for cad in cad_docs:
                    c_state = cad.get("State", "")
                    if isinstance(c_state, dict):
                        c_state = c_state.get("Value", str(c_state))
                    cad_list.append(OrderedDict([
                        ("type", "CADDocument"),
                        ("number", cad.get("Number", "")),
                        ("name", cad.get("Name", "")),
                        ("version", cad.get("Version", "")),
                        ("cad_name", cad.get("CADName", cad.get("FileName", ""))),
                        ("state", str(c_state)),
                        ("identity", cad.get("Identity", "")),
                        ("source", cad.get("_source_nav", "")),
                    ]))
                node["cad_documents"] = cad_list
                progress.tick_cad_docs(len(cad_list))
            else:
                print(f"{indent}   📐 0 CAD-Dokument(e)")
                node["cad_documents"] = []
        else:
            node["cad_documents"] = []
    else:
        node["documents"] = []
        node["cad_documents"] = []
        node["children"] = made_from_subtrees
        print(f"{indent}   ⚠ Keine Part-ID – Kinder/Dokumente können nicht geladen werden")

    _reorder_usage_before_children(node)
    return node

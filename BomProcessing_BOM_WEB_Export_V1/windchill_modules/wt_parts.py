import json

import requests


def find_part(client, part_number: str, debug: bool = False) -> dict:
    """WTPart anhand der Nummer finden (neueste Version)."""
    if part_number in client._part_cache:
        if debug:
            print(f"  Part '{part_number}' aus Cache")
        return client._part_cache[part_number]

    url = f"{client.odata_base}/ProdMgmt/Parts"

    filter_strategies = [
        f"Number eq '{part_number}'",
        f"Number eq '{part_number}' and LatestIteration eq true",
    ]

    if client._part_properties:
        number_candidates = [
            p for p in client._part_properties
            if "number" in p.lower() or "nummer" in p.lower()
        ]
        if number_candidates and "Number" not in number_candidates:
            for nc in number_candidates:
                filter_strategies.insert(0, f"{nc} eq '{part_number}'")
                filter_strategies.insert(1, f"contains({nc},'{part_number}')")

    print(f"  Suche Part '{part_number}'...")
    items = None
    successful_filter = None

    for i, flt in enumerate(filter_strategies):
        params = {"$filter": flt}
        if debug:
            print(f"    Strategie {i+1}: $filter={flt}")

        try:
            resp = client._get(url, params)
            if resp.status_code == 200:
                data = resp.json()
                result_items = data.get("value", [])
                if result_items:
                    items = result_items
                    successful_filter = flt
                    print(f"    → {len(items)} Ergebnis(se) gefunden!")
                    break
                elif debug:
                    print("    → 0 Ergebnisse")
            elif resp.status_code in (400, 501):
                if debug:
                    print(f"    → HTTP {resp.status_code} (Filter nicht unterstützt)")
                continue
            elif resp.status_code == 401:
                raise PermissionError("Authentifizierung fehlgeschlagen.")
            elif debug:
                print(f"    → HTTP {resp.status_code}")
        except requests.exceptions.HTTPError:
            continue

    if not items:
        fuzzy_strategies = [
            f"contains(Number,'{part_number}')",
            f"startswith(Number,'{part_number}')",
        ]
        if client._part_properties:
            number_candidates = [
                p for p in client._part_properties
                if "number" in p.lower() or "nummer" in p.lower()
            ]
            for nc in number_candidates:
                if nc != "Number":
                    fuzzy_strategies.insert(0, f"contains({nc},'{part_number}')")

        for i2, flt in enumerate(fuzzy_strategies):
            params = {"$filter": flt}
            if debug:
                print(f"    Fuzzy-Strategie {i2+1}: $filter={flt}")
            try:
                resp = client._get(url, params)
                if resp.status_code == 200:
                    data = resp.json()
                    result_items = data.get("value", [])
                    if result_items:
                        exact = [
                            p for p in result_items
                            if any(str(v) == part_number for v in p.values())
                        ]
                        if exact:
                            items = exact
                            successful_filter = f"{flt} (exakter Treffer)"
                        else:
                            items = result_items
                            successful_filter = flt
                        print(
                            f"    → {len(items)} Ergebnis(se) "
                            f"(davon {len(exact)} exakt)"
                        )
                        break
            except (requests.exceptions.HTTPError, Exception):
                continue

    if not items:
        print("    Fallback: Lade Parts und filtere clientseitig...")
        try:
            all_parts = client._get_all_pages(url, {"$top": "500"})
            print(f"    → {len(all_parts)} Parts geladen")
            if all_parts and debug:
                first = all_parts[0]
                print(
                    f"    Beispiel-Part: "
                    f"{json.dumps(first, indent=6, default=str)[:500]}"
                )

            for part in all_parts:
                for key, val in part.items():
                    if str(val) == part_number:
                        items = [part]
                        successful_filter = f"clientside: {key} == {part_number}"
                        print(f"    → Gefunden via Property '{key}'!")
                        break
                if items:
                    break

            if not items:
                for part in all_parts:
                    for key, val in part.items():
                        if isinstance(val, str) and part_number in val:
                            items = [part]
                            successful_filter = (
                                f"clientside-contains: {key} contains {part_number}"
                            )
                            print(f"    → Gefunden via Property '{key}' (contains)!")
                            break
                    if items:
                        break

        except Exception as e:
            print(f"    Fallback fehlgeschlagen: {e}")

    if not items:
        raise ValueError(
            f"Part '{part_number}' nicht gefunden. "
            f"Alle Filter-Strategien erfolglos. "
            f"Bekannte Properties: {', '.join(client._part_properties)}"
        )

    if successful_filter and debug:
        print(f"    Erfolgreicher Filter: {successful_filter}")

    items.sort(
        key=lambda p: (
            p.get("Version", p.get("VersionID", "")),
            p.get("Iteration", p.get("IterationID", "")),
        ),
        reverse=True,
    )
    selected = items[0]
    if debug:
        print(
            f"    Gewählte Version: "
            f"{selected.get('Version', '?')}.{selected.get('Iteration', '?')}"
        )

    client._part_cache[part_number] = selected
    return selected


def get_part_by_id(client, part_id: str) -> dict | None:
    """Part anhand seiner ID laden."""
    url = f"{client.odata_base}/ProdMgmt/Parts('{part_id}')"
    try:
        return client._get_json(url)
    except requests.exceptions.HTTPError:
        return None


def get_soft_attributes(
    client,
    part_id: str,
    attr_names: list[str],
    debug: bool = False,
) -> dict:
    """Soft-Attribute (IBAs / kundenspezifische Attribute) eines Parts laden."""
    result = {name: "" for name in attr_names}

    if not hasattr(client, "_soft_attr_strategy_support"):
        client._soft_attr_strategy_support = {
            "select": None,
            "expand": None,
            "nav": {
                "TypedAttributes": None,
                "Attributes": None,
                "IBAValues": None,
            },
        }

    select_str = ",".join(attr_names)
    url = f"{client.odata_base}/ProdMgmt/Parts('{part_id}')"
    if client._soft_attr_strategy_support["select"] is not False:
        try:
            resp = client._get(
                url,
                {"$select": select_str},
                suppress_http_error_log=True,
            )
            if resp.status_code == 200:
                client._soft_attr_strategy_support["select"] = True
                data = resp.json()
                for name in attr_names:
                    val = data.get(name, "")
                    if isinstance(val, dict):
                        val = val.get("Value", val.get("Display", str(val)))
                    if val:
                        result[name] = str(val)
                if any(result[n] for n in attr_names):
                    if debug:
                        print(f"      Soft-Attribute via $select: {result}")
                    return result
            elif resp.status_code in (400, 404, 405):
                client._soft_attr_strategy_support["select"] = False
        except Exception:
            pass

    try:
        resp = client._get(url)
        if resp.status_code == 200:
            data = resp.json()
            for name in attr_names:
                val = data.get(name, "")
                if isinstance(val, dict):
                    val = val.get("Value", val.get("Display", str(val)))
                if val:
                    result[name] = str(val)
            if any(result[n] for n in attr_names):
                if debug:
                    print(f"      Soft-Attribute via Part-Detail: {result}")
                return result
    except Exception:
        pass

    if client._soft_attr_strategy_support["expand"] is not False:
        try:
            resp = client._get(
                url,
                {"$expand": "SoftAttributes"},
                suppress_http_error_log=True,
            )
            if resp.status_code == 200:
                client._soft_attr_strategy_support["expand"] = True
                data = resp.json()
                soft_attrs = data.get("SoftAttributes", [])
                if isinstance(soft_attrs, list):
                    for attr in soft_attrs:
                        attr_name = attr.get("Name", attr.get("InternalName", ""))
                        attr_val = attr.get("Value", "")
                        if attr_name in attr_names and attr_val:
                            result[attr_name] = str(attr_val)
                elif isinstance(soft_attrs, dict):
                    for name in attr_names:
                        val = soft_attrs.get(name, "")
                        if val:
                            result[name] = str(val)
                for name in attr_names:
                    val = data.get(name, "")
                    if isinstance(val, dict):
                        val = val.get("Value", val.get("Display", str(val)))
                    if val and not result.get(name):
                        result[name] = str(val)
                if any(result[n] for n in attr_names):
                    if debug:
                        print(f"      Soft-Attribute via $expand=SoftAttributes: {result}")
                    return result
            elif resp.status_code in (400, 404, 405):
                client._soft_attr_strategy_support["expand"] = False
        except Exception:
            pass

    for nav in ["TypedAttributes", "Attributes", "IBAValues"]:
        if client._soft_attr_strategy_support["nav"].get(nav) is False:
            continue
        attr_url = f"{client.odata_base}/ProdMgmt/Parts('{part_id}')/{nav}"
        try:
            resp = client._get(attr_url, suppress_http_error_log=True)
            if resp.status_code == 200:
                client._soft_attr_strategy_support["nav"][nav] = True
                data = resp.json()
                items = data.get("value", [])
                if isinstance(items, list):
                    for attr in items:
                        attr_name = attr.get(
                            "Name",
                            attr.get("InternalName", attr.get("Definition", "")),
                        )
                        attr_val = attr.get("Value", attr.get("StringValue", ""))
                        if attr_name in attr_names and attr_val:
                            result[attr_name] = str(attr_val)
                if any(result[n] for n in attr_names):
                    if debug:
                        print(f"      Soft-Attribute via {nav}: {result}")
                    return result
            elif resp.status_code in (400, 404, 405):
                client._soft_attr_strategy_support["nav"][nav] = False
        except Exception:
            continue

    if debug:
        print(f"      Soft-Attribute nicht gefunden: {attr_names}")
    return result

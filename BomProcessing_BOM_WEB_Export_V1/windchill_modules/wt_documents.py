import requests


def is_valid_document(doc: dict) -> bool:
    """Prüft ob ein Dokument-Objekt tatsächlich Daten enthält."""
    for key in ("Number", "Name", "Identity"):
        val = doc.get(key, "")
        if val and str(val).strip():
            return True
    return False


def get_part_reference_link_ids(client, part_id: str, debug: bool = False) -> set:
    """Holt die IDs aller WTPartReferenceLink-Objekte eines Parts."""
    link_ids = set()
    url = f"{client.odata_base}/ProdMgmt/Parts('{part_id}')/References"
    ref_links = client._try_get_all_pages(url)
    if ref_links:
        for link in ref_links:
            lid = link.get("ID", "")
            if lid:
                link_ids.add(lid)
    if debug:
        print(f"      Part Reference-Links: {len(link_ids)} Stück")
    return link_ids


def doc_has_reference_link(
    client,
    doc_id: str,
    part_link_ids: set,
    max_pages: int,
) -> bool:
    """Prüft ob ein Dokument über ReferencedBy einen der Part-Links hat."""
    if not part_link_ids:
        return False

    doc_service = getattr(client, "_doc_service_path", "DocMgmt")
    url = f"{client.odata_base}/{doc_service}/Documents('{doc_id}')/ReferencedBy"

    try:
        data = client._get_json(url, {"$select": "ID"})
    except requests.exceptions.HTTPError:
        return False

    page = 1
    while True:
        for link in data.get("value", []):
            if link.get("ID", "") in part_link_ids:
                return True

        if "@odata.nextLink" not in data:
            break
        page += 1
        if page > max_pages:
            break
        try:
            data = client._get_json(data["@odata.nextLink"])
        except requests.exceptions.HTTPError:
            break

    return False


def get_described_documents(
    client,
    part_id: str,
    part_number: str = "",
    debug: bool = False,
) -> list:
    """Dokumente, die mit einem Part verknüpft sind."""
    all_docs = []
    seen_ids = set()

    url = f"{client.odata_base}/ProdMgmt/Parts('{part_id}')/DescribedBy"
    result = client._try_get_all_pages(url)
    if result:
        for item in result:
            if is_valid_document(item):
                doc_id = item.get("ID", item.get("id", id(item)))
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    item["_source_nav"] = "DescribedBy"
                    all_docs.append(item)
        if debug and result:
            valid = sum(1 for d in all_docs if d.get("_source_nav") == "DescribedBy")
            print(f"      DescribedBy: {valid} Dokument(e)")

    if part_number and client._doc_service_available:
        doc_service = getattr(client, "_doc_service_path", "DocMgmt")
        filt = f"BALREFERENCEPART/any(s:s eq '{part_number}')"
        url = f"{client.odata_base}/{doc_service}/Documents?$filter={filt}"
        result = client._try_get_all_pages(url)
        if result:
            new_count = 0
            for item in result:
                if not is_valid_document(item):
                    continue
                doc_id = item.get("ID", item.get("id", ""))
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    item["_source_nav"] = "DocMgmt/BALREFERENCEPART"
                    all_docs.append(item)
                    new_count += 1
            if debug:
                print(
                    f"      DocMgmt BALREFERENCEPART: {len(result)} Kandidat(en), "
                    f"{new_count} neu (ohne Duplikate zu DescribedBy)"
                )

    if not all_docs:
        url = f"{client.odata_base}/ProdMgmt/Parts('{part_id}')/References"
        ref_links = client._try_get_all_pages(url)
        if ref_links:
            for link in ref_links:
                if is_valid_document(link):
                    doc_id = link.get("ID", link.get("id", id(link)))
                    if doc_id not in seen_ids:
                        seen_ids.add(doc_id)
                        link["_source_nav"] = "References"
                        all_docs.append(link)
                elif debug:
                    print(
                        f"      [References] Link: {link.get('ObjectType', '?')} "
                        f"ID={link.get('ID', '?')} "
                        f"(nicht auflösbar, HTTP 500 Bug)"
                    )

    if debug:
        print(f"      Dokumente gesamt: {len(all_docs)}")
    return all_docs


def get_cad_documents(client, part_id: str, debug: bool = False) -> list:
    """CAD-Dokumente eines Parts abrufen."""
    all_cads = []
    seen_ids = set()

    url = (
        f"{client.odata_base}/ProdMgmt/Parts('{part_id}')"
        f"/PartDocAssociations?$expand=RelatedCADDoc"
    )
    result = client._try_get_all_pages(url)
    if result:
        for assoc in result:
            cad = assoc.get("RelatedCADDoc", {})
            if not cad or not is_valid_document(cad):
                if debug:
                    assoc_type = assoc.get("AssociationType", {})
                    if isinstance(assoc_type, dict):
                        assoc_type = assoc_type.get("Display", str(assoc_type))
                    print(
                        f"      [PartDocAssociations] Link ({assoc_type})"
                        f" ohne gültiges CAD-Dokument"
                    )
                continue
            cad_id = cad.get("ID", cad.get("id", id(cad)))
            if cad_id not in seen_ids:
                seen_ids.add(cad_id)
                assoc_type = assoc.get("AssociationType", {})
                if isinstance(assoc_type, dict):
                    assoc_type = assoc_type.get("Display", str(assoc_type))
                cad["_source_nav"] = f"PartDocAssociations/{assoc_type}"
                all_cads.append(cad)
        if debug:
            print(f"      PartDocAssociations: {len(all_cads)} CAD-Dokument(e)")

    if not all_cads:
        url = f"{client.odata_base}/ProdMgmt/Parts('{part_id}')/Representations"
        result = client._try_get_all_pages(url)
        if result:
            valid_count = 0
            for cad in result:
                if not is_valid_document(cad):
                    continue
                cad_id = cad.get("ID", cad.get("id", id(cad)))
                if cad_id not in seen_ids:
                    seen_ids.add(cad_id)
                    cad["_source_nav"] = "Representations"
                    all_cads.append(cad)
                    valid_count += 1
            if debug and valid_count:
                print(f"      Representations: {valid_count} CAD-Dokument(e)")

    return all_cads

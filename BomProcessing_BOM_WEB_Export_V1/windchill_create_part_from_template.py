"""
windchill_create_part_from_template.py
=====================================
Calls BalluffCustom/CreateProductFromtemplate using credentials and login
helpers from fetch_swagger_docs.py.

Usage:
    python windchill_create_part_from_template.py
    python windchill_create_part_from_template.py --input create_product_from_template_input.json
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import sys
import time
from pathlib import Path

from fetch_swagger_docs import (
    build_session,
    derive_windchill_base_from_odata_url,
    form_login,
    get_credentials,
)

CONFIG_FILE = Path(__file__).parent / "config.json"
DEFAULT_INPUT_FILE = Path(__file__).parent / "create_product_from_template_input.json"

REQUIRED_FIELDS = (
    "ProductTemplateNumber",
    "ProductNumber",
    "SAPName",
    "Suffix",
    "Binding",
    "OrderCodeFamily",
)

CREATE_VISIBILITY_TIMEOUT_SECONDS = 30
CREATE_VISIBILITY_POLL_INTERVAL_SECONDS = 2
CURRENT_TIMESTAMP_TOKEN = "__CURRENT_TIMESTAMP__"


def load_json(file_path: Path) -> dict:
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Input JSON must be a JSON object.")

    return data


def validate_payload(payload: dict) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    invalid = []
    for field in REQUIRED_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            invalid.append(field)

    if invalid:
        raise ValueError(
            "These fields must be non-empty strings: " + ", ".join(invalid)
        )

    update_attributes = payload.get("UpdateAttributes")
    if update_attributes is None:
        return

    if not isinstance(update_attributes, list) or not update_attributes:
        raise ValueError("UpdateAttributes must be a non-empty array when provided.")

    for index, entry in enumerate(update_attributes, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"UpdateAttributes[{index}] must be an object.")

        attr_name = entry.get("AttrName")
        attr_value = entry.get("AttrValue")

        if not isinstance(attr_name, str) or not attr_name.strip():
            raise ValueError(
                f"UpdateAttributes[{index}].AttrName must be a non-empty string."
            )

        if not isinstance(attr_value, str) or not attr_value.strip():
            raise ValueError(
                f"UpdateAttributes[{index}].AttrValue must be a non-empty string."
            )


def build_create_payload(payload: dict) -> dict:
    return {field: payload[field] for field in REQUIRED_FIELDS}


def load_urls_from_config() -> tuple[str, str]:
    config = load_json(CONFIG_FILE)

    custom_odata_url = str(config.get("balluff_custom_odata_base_url", "")).rstrip("/")
    if not custom_odata_url:
        raise ValueError(
            "Missing 'balluff_custom_odata_base_url' in config.json."
        )

    fallback_base_url = str(config.get("windchill_base_url", "")).rstrip("/")
    auth_base = derive_windchill_base_from_odata_url(custom_odata_url) or fallback_base_url

    if not auth_base:
        raise ValueError("Could not determine authentication base URL.")

    return custom_odata_url, auth_base


def _response_body(resp) -> dict:
    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}
    return {"raw": resp.text}


def _assert_balluff_action_succeeded(action_name: str, body: dict) -> None:
    if not isinstance(body, dict):
        raise RuntimeError(f"{action_name} returned an unexpected response body: {body}")

    if body.get("created") is False:
        raise RuntimeError(
            f"{action_name} reported no success: {body.get('message') or body}"
        )


def refresh_csrf_nonce(session, custom_odata_url: str, auth_base: str) -> str | None:
    """
    Fetch a fresh CSRF nonce by probing Windchill OData bootstrap endpoints.
    Some endpoints emit CSRF_NONCE only after service bootstrap.
    """
    candidates = [
        f"{auth_base}/servlet/odata/v6/ProdMgmt",
        f"{auth_base}/servlet/odata/v6/ProdMgmt?_ts={int(time.time() * 1000)}",
        f"{auth_base}/servlet/odata/v6/ProdMgmt/Parts?$top=1",
        custom_odata_url,
    ]

    for url in candidates:
        # Ask server explicitly for a fresh nonce.
        session.headers["CSRF_NONCE"] = "Fetch"
        probe_resp = session.get(
            url,
            timeout=30,
            verify=False,
            headers={"Accept": "application/json, */*"},
        )
        nonce = probe_resp.headers.get("CSRF_NONCE")
        if nonce:
            session.headers["CSRF_NONCE"] = nonce
            return nonce

    return None


def _post_balluff_action(
    session,
    endpoint: str,
    payload: dict,
    custom_odata_url: str,
    auth_base: str,
    action_name: str,
) -> tuple[object, dict]:
    def do_post():
        return session.post(
            endpoint,
            json=payload,
            timeout=60,
            verify=False,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

    resp = do_post()
    body = _response_body(resp)

    err_code = body.get("error", {}).get("code") if isinstance(body, dict) else None
    if resp.status_code in (400, 403) and err_code == "INVALID_NONCE":
        print(f"  {action_name}: INVALID_NONCE received. Refreshing nonce and retrying once...")
        refresh_csrf_nonce(session, custom_odata_url, auth_base)
        resp = do_post()
        body = _response_body(resp)

    if not resp.ok:
        raise RuntimeError(
            f"{action_name} failed with HTTP {resp.status_code}: {body}"
        )

    _assert_balluff_action_succeeded(action_name, body)

    return resp, body


def current_balversion_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_update_attributes(payload: dict) -> list[dict]:
    update_attributes = payload.get("UpdateAttributes")
    if not update_attributes:
        return [
            {
                "AttrName": "BAL_VERSION",
                "AttrValue": current_balversion_timestamp(),
            }
        ]

    resolved_attributes = []
    for entry in update_attributes:
        attr_value = entry["AttrValue"]
        if attr_value == CURRENT_TIMESTAMP_TOKEN:
            attr_value = current_balversion_timestamp()

        resolved_attributes.append(
            {
                "AttrName": entry["AttrName"],
                "AttrValue": attr_value,
            }
        )

    return resolved_attributes


def update_product_attributes(
    session,
    custom_odata_url: str,
    auth_base: str,
    product_number: str,
    attribute_list: list[dict],
) -> dict:
    endpoint = f"{custom_odata_url}/UpdateProduct"
    payload = {
        "ProductNumber": product_number,
        "attributeList": attribute_list,
    }

    resp, body = _post_balluff_action(
        session,
        endpoint,
        payload,
        custom_odata_url,
        auth_base,
        "UpdateProduct",
    )

    return {
        "endpoint": endpoint,
        "status_code": resp.status_code,
        "ok": resp.ok,
        "request_payload": payload,
        "response": body,
    }


def _normalize_view_value(raw_view) -> str:
    """Extract a comparable view value from different response shapes."""
    if isinstance(raw_view, dict):
        # Windchill often returns enum-like objects with Value/Display
        for key in ("Value", "Display", "Name", "name", "value"):
            if key in raw_view and raw_view[key] is not None:
                return str(raw_view[key]).strip()
        return ""
    if raw_view is None:
        return ""
    return str(raw_view).strip()


def _is_manufacturing_view(view_text: str) -> bool:
    value = view_text.lower()
    return any(token in value for token in ("manufacturing", "mfg"))


def ensure_template_part_is_manufacturing_view(
    session,
    auth_base: str,
    template_number: str,
) -> dict:
    """
    Validate that the template part exists and belongs to a manufacturing view.
    Raises RuntimeError if no part is found or if the view is not manufacturing.
    """
    escaped_template_number = template_number.replace("'", "''")
    url = f"{auth_base}/servlet/odata/v6/ProdMgmt/Parts"
    params = {
        "$filter": f"Number eq '{escaped_template_number}'",
        "$top": "5",
    }

    resp = session.get(
        url,
        params=params,
        timeout=30,
        verify=False,
        headers={"Accept": "application/json"},
    )

    body = _response_body(resp)
    if not resp.ok:
        raise RuntimeError(
            f"Template pre-check failed with HTTP {resp.status_code}: {body}"
        )

    items = body.get("value", []) if isinstance(body, dict) else []
    if not items:
        raise RuntimeError(
            f"Template part '{template_number}' wurde in ProdMgmt/Parts nicht gefunden."
        )

    # Evaluate candidate entries and accept any matching manufacturing view
    candidate_views = []
    for item in items:
        normalized = _normalize_view_value(item.get("View"))
        candidate_views.append(normalized or "<leer>")
        if _is_manufacturing_view(normalized):
            return item

    raise RuntimeError(
        "Template part ist keine Manufacturing View. "
        f"Gefundene View-Werte: {', '.join(candidate_views)}"
    )


def wait_for_created_product(
    session,
    auth_base: str,
    product_number: str,
    timeout_seconds: int = CREATE_VISIBILITY_TIMEOUT_SECONDS,
    poll_interval_seconds: int = CREATE_VISIBILITY_POLL_INTERVAL_SECONDS,
) -> dict:
    """
    Poll ProdMgmt/Parts until the newly created product becomes queryable.
    Windchill can acknowledge the create action before the object is immediately
    visible for follow-up update actions.
    """
    escaped_product_number = product_number.replace("'", "''")
    url = f"{auth_base}/servlet/odata/v6/ProdMgmt/Parts"
    params = {
        "$filter": f"Number eq '{escaped_product_number}'",
        "$top": "5",
    }

    deadline = time.time() + timeout_seconds
    last_body = None

    while time.time() < deadline:
        resp = session.get(
            url,
            params=params,
            timeout=30,
            verify=False,
            headers={"Accept": "application/json"},
        )
        body = _response_body(resp)
        last_body = body

        if resp.ok and isinstance(body, dict):
            items = body.get("value", [])
            if items:
                return items[0]

        time.sleep(poll_interval_seconds)

    raise RuntimeError(
        "Created product is not yet available in ProdMgmt/Parts for follow-up update. "
        f"ProductNumber='{product_number}', last response: {last_body}"
    )


def create_from_template(custom_odata_url: str, auth_base: str, payload: dict) -> dict:
    username, password = get_credentials()
    if not username:
        raise RuntimeError("Login canceled by user.")

    session = build_session(auth_base, username, password)
    form_login(session, auth_base, username, password)

    template_number = payload["ProductTemplateNumber"]
    template_part = ensure_template_part_is_manufacturing_view(
        session,
        auth_base,
        template_number,
    )
    template_view = _normalize_view_value(template_part.get("View")) or "<unbekannt>"
    print(
        f"  Template pre-check OK: {template_number} (View: {template_view})"
    )

    # Windchill requires a valid CSRF nonce for action POSTs.
    nonce = refresh_csrf_nonce(session, custom_odata_url, auth_base)
    if nonce:
        print("  CSRF nonce loaded.")
    else:
        print("  Warning: no CSRF nonce found on initial probe.")

    create_payload = build_create_payload(payload)
    endpoint = f"{custom_odata_url}/CreateProductFromtemplate"
    resp, body = _post_balluff_action(
        session,
        endpoint,
        create_payload,
        custom_odata_url,
        auth_base,
        "CreateProductFromtemplate",
    )

    product_number = payload["ProductNumber"]
    wait_for_created_product(session, auth_base, product_number)
    update_attributes = build_update_attributes(payload)
    update_names = ", ".join(attribute["AttrName"] for attribute in update_attributes)
    print(f"  Product created successfully. Updating attributes for {product_number}: {update_names}...")
    update_result = update_product_attributes(
        session,
        custom_odata_url,
        auth_base,
        product_number,
        update_attributes,
    )

    result = {
        "endpoint": endpoint,
        "status_code": resp.status_code,
        "ok": resp.ok,
        "response": body,
        "update_product": update_result,
    }

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Call BalluffCustom CreateProductFromtemplate action."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT_FILE),
        help="Path to JSON payload file (default: create_product_from_template_input.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_file = Path(args.input)
    if not input_file.is_absolute():
        input_file = (Path(__file__).parent / input_file).resolve()

    payload = load_json(input_file)
    validate_payload(payload)

    custom_odata_url, auth_base = load_urls_from_config()

    print("Calling CreateProductFromtemplate...")
    print(f"  Auth base : {auth_base}")
    print(f"  OData base: {custom_odata_url}")
    print(f"  Input     : {input_file}")

    result = create_from_template(custom_odata_url, auth_base, payload)
    update_result = result.get("update_product", {})

    print("\nSuccess:")
    print(f"  CreateProductFromtemplate HTTP Status: {result['status_code']}")
    print("\nCreateProductFromtemplate response:")
    print(json.dumps(result["response"], indent=2, ensure_ascii=False))

    if update_result:
        print(f"\nUpdateProduct HTTP Status: {update_result.get('status_code')}")
        print("UpdateProduct request payload:")
        print(json.dumps(update_result.get("request_payload"), indent=2, ensure_ascii=False))
        print("UpdateProduct response:")
        print(json.dumps(update_result.get("response"), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)

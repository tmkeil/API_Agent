"""
OData-Feldnamen — Zentrale Zuordnung.
======================================

Windchill OData liefert Attributnamen ohne Underscores:
  Schema (definitions.json):  BAL_SAP_STPO_RFORM   (mit _)
  Response (JSON):            BALSAPSTPORFORM       (ohne _)

Dieses Modul definiert alle Balluff-spezifischen OData-Feldnamen
als benannte Konstanten, gruppiert nach Entitaet/Kontext.
So sind die kryptischen Strings zentral dokumentiert und auffindbar.

Verwendung:
    from src.core.odata_fields import F
    val = part_raw.get(F.Part.MADE_FROM_NUMBER)

Abkuerzungen in "Verwendet in":
    BET  = Balluff Export Tabelle      (bom_export_service.py → BalluffExportTable.tsx)
    BOM  = BOM Tree Views              (bom_views.py → BomTreeNode.tsx)
    DET  = Detail-Seite / Ext. Export  (admin_service.py → DetailPage.tsx)
    SAP  = SAP Export                  (sap_export_service.py)
    WRT  = Schreib-Operationen         (write_service.py → Create/Update)
"""

from __future__ import annotations


class _PartFields:
    """Felder auf PTC.ProdMgmt.Part (WTPart)."""

    MADE_FROM_NUMBER   = "BALMADEFROMNUMBER"           # BAL_MADE_FROM_NUMBER     — Verwendet in: BET, BOM, DET
    DISCON_TYPE        = "BALSAPMARAZZROLLUSEUAS"       # BAL_SAP_MARA_ZZROLLUSEUAS — Verwendet in: BET
    MATERIAL_TYPE      = "BALSAPMATERIALTYPE"           # BAL_SAP_MATERIAL_TYPE    — Verwendet in: BOM
    SAP_NAME           = "BALSAPNAME"                   # BAL_SAP_NAME             — Verwendet in: BOM
    SAP_SUFFIX         = "BALSAPSUFFIX"                 # BAL_SAP_SUFFIX           — Verwendet in: DET
    SUFFIX             = "BALSUFFIX"                    # BAL_SUFFIX               — Verwendet in: BOM
    BINDING            = "BALBINDING"                   # BAL_BINDING              — Verwendet in: BOM
    SAP_ORDER_CODE     = "BALSAPORDERCODE"              # BAL_SAP_ORDER_CODE       — Verwendet in: BOM
    SAP_ASSIGNED_PLANTS = "BALSAPASSIGNEDPLANTS"        # BAL_SAP_ASSIGNED_PLANTS  — Verwendet in: BOM
    CP_ORDER_PREFIX    = "BALCPORDERPREFIX"              # BAL_CP_ORDER_PREFIX      — Verwendet in: WRT
    DESCRIPTION_1      = "BALDESCRIPTION1"              # BAL_DESCRIPTION_1        — Verwendet in: BOM
    IS_VARIANT         = "BALISVARIANT"                 # BAL_IS_VARIANT           — Verwendet in: BOM
    VARIANT_DERIVED_FROM = "BALVARIANTDERIVEDFROMNUMBER" # BAL_VARIANT_DERIVED_FROM — Verwendet in: BOM
    DOWNSTREAM         = "BALDOWNSTREAM"                # BAL_DOWNSTREAM           — Verwendet in: DET, WRT
    UPSTREAM           = "BALUPSTREAM"                  # BAL_UPSTREAM             — Verwendet in: BOM


class _PartSubtypes:
    """ObjectType-Werte fuer Part-Subtypen.                                       — Verwendet in: BET (Collection-Erkennung), WRT"""

    COLLECTION              = "BALCOLLECTIONPART"
    PRODUCT                 = "BALPRODUCTPART"
    RAW_MATERIAL            = "BALRAWMATERIAL"
    PACKAGE                 = "BALPACKAGEPART"
    EQUIPMENT               = "BALEQUIPMENTPART"
    REFERENCE               = "BALREFERENCEPART"
    AUX                     = "BALAUXPART"
    MECHATRONIC             = "BALMECHATRONICPART"
    BINDING                 = "BALBINDING"
    CLASSIFICATION_BINDING  = "BALCLASSIFICATIONBINDINGWTPART"  # Verwendet in: WRT (Part-Anlage)


class _UsageLinkFields:
    """Felder auf PTC.ProdMgmt.PartUse (UsageLink / BOM-Beziehung)."""

    # Standard-OData-Felder
    FIND_NUMBER         = "FindNumber"                  #                          — Verwendet in: BET
    LINE_NUMBER         = "LineNumber"                  #                          — Verwendet in: BET (Fallback)
    QUANTITY            = "Quantity"                    #                          — Verwendet in: BET
    QUANTITY_UNIT       = "QuantityUnit"                #                          — Verwendet in: BET
    UNIT                = "Unit"                        #                          — Verwendet in: BET (Fallback)
    REF_DESIGNATOR_RANGE = "ReferenceDesignatorRange"   #                          — Verwendet in: BET
    REF_DESIGNATOR      = "ReferenceDesignator"         #                          — Verwendet in: BET (Fallback)

    # Balluff-spezifische UsageLink-Felder
    DISCON_DATE         = "BALSAPSTPONFEAG"             # BAL_SAP_STPO_NFEAG      — Verwendet in: BET, BOM
    DISCON_GRP          = "BALSAPSTPONFGRP"             # BAL_SAP_STPO_NFGRP      — Verwendet in: BET, BOM
    ALT_GROUP           = "BALSAPSTPOALPGR"             # BAL_SAP_STPO_ALPGR      — Verwendet in: BOM
    ALT_PRIORITY        = "BALSAPSTPOALPRF"             # BAL_SAP_STPO_ALPRF      — Verwendet in: BOM
    ALT_STRATEGY        = "BALSAPSTPOALPST"             # BAL_SAP_STPO_ALPST      — Verwendet in: BOM
    USAGE_PROBABILITY   = "BALSAPSTPOEWAHR"             # BAL_SAP_STPO_EWAHR      — Verwendet in: BOM
    ERP_POSITION_TEXT   = "BALERPBOMPOSITIONTEXT"       # BAL_ERP_BOM_POSITION_TEXT — Verwendet in: BET, BOM
    BY_PRODUCT          = "BALBYPRODUCT"                # BAL_BY_PRODUCT           — Verwendet in: BOM


class _RawMaterialLinkFields:
    """Felder auf PTC.BomTransformation.RawMaterialLink (Made-From-Beziehung).
    OData-Endpoint: GET /Parts('{id}')/MadeFromLink"""

    FORMULA_KEY         = "BALSAPSTPORFORM"             # BAL_SAP_STPO_RFORM (Enum) — Verwendet in: BET
    RAW_DIM_1           = "BALSAPSTPOROMS1"             # BAL_SAP_STPO_ROMS1       — Verwendet in: BET, BOM, DET
    RAW_DIM_2           = "BALSAPSTPOROMS2"             # BAL_SAP_STPO_ROMS2       — Verwendet in: BET, BOM, DET
    RAW_DIM_3           = "BALSAPSTPOROMS3"             # BAL_SAP_STPO_ROMS3       — Verwendet in: BET, BOM, DET
    RAW_DIM_UNIT        = "BALSAPSTPOROMEI"             # BAL_SAP_STPO_ROMEI (Enum) — Verwendet in: BET, BOM, DET
    RAW_AMOUNT          = "BALSAPSTPOROMEN"             # BAL_SAP_STPO_ROMEN       — Verwendet in: BET, BOM, DET
    RAW_AMOUNT_UNIT     = "BALSAPSTPOROAME"             # BAL_SAP_STPO_ROAME (Enum) — Verwendet in: BET, BOM, DET
    RAW_QUANTITY        = "BALSAPSTPOROANZ"             # BAL_SAP_STPO_ROANZ       — Verwendet in: BET, BOM, DET
    RAW_QUANTITY_UNIT   = "BALSAPSTPOROKME"             # BAL_SAP_STPO_ROKME (Enum) — Verwendet in: BET, BOM, DET


class _DocumentFields:
    """Felder auf PTC.DocMgmt.* (WTDocument / EPMDocument)."""

    DOC_TYPE            = "BALDOCUMENTTYPE"             # BAL_DOCUMENT_TYPE (Enum)  — Verwendet in: BET
    SAP_RELEVANCE       = "BALSAPRELEVANCE"             # BAL_SAP_RELEVANCE (bool)  — Verwendet in: BET, BOM
    PRINTING_GOOD       = "BALPRINTINGGOOD"             # BAL_PRINTING_GOOD         — Verwendet in: BET
    ENC_DOC_PART        = "BALENCDOCPART"               # BAL_ENC_DOC_PART          — (Subtyp-Erkennung)


class F:
    """Zentrale Feldnamen-Registry.

    Verwendung:
        from src.core.odata_fields import F

        part_raw.get(F.Part.MADE_FROM_NUMBER)
        usage_link.get(F.UsageLink.DISCON_DATE)
        made_from_link.get(F.RawMaterialLink.FORMULA_KEY)
        doc_raw.get(F.Doc.DOC_TYPE)
    """

    Part = _PartFields
    PartSubtype = _PartSubtypes
    UsageLink = _UsageLinkFields
    RawMaterialLink = _RawMaterialLinkFields
    Doc = _DocumentFields

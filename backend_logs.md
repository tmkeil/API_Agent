2026-04-02 15:37:13,794 [INFO] src.routers.auth: Login-Versuch: system=dev url=https://plm-dev.neuhausen.balluff.net/Windchill user=keilt
2026-04-02 15:37:13,796 [INFO] src.adapters.base: Connecting to https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6
2026-04-02 15:37:14,692 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt "HTTP/1.1 307 307"
2026-04-02 15:37:14,747 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ "HTTP/1.1 200 200"
2026-04-02 15:37:14,748 [INFO] src.adapters.base: Auth-Probe: status=200 url=https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ content-type=application/json;odata.metadata=minimal www-authenticate=
2026-04-02 15:37:14,748 [INFO] src.adapters.base: Basic Auth akzeptiert (status=200)
2026-04-02 15:37:14,794 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/PTC/GetCSRFToken() "HTTP/1.1 200 200"
2026-04-02 15:37:14,795 [INFO] src.adapters.base: CSRF-Token erhalten: CSRF_NONCE=GiKPQsPQNLr1…
2026-04-02 15:37:14,797 [INFO] api: POST /api/auth/login → 200 (1005.5 ms)
INFO:     127.0.0.1:52111 - "POST /api/auth/login HTTP/1.1" 200 OK
2026-04-02 15:37:25,989 [INFO] src.adapters.parts_mixin: Trying ClfNodes at: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ClfStructure/ClfNodes
2026-04-02 15:37:26,088 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ClfStructure/ClfNodes "HTTP/1.1 404 404"
2026-04-02 15:37:26,089 [INFO] src.adapters.parts_mixin: ClfNodes https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ClfStructure/ClfNodes → HTTP 404
2026-04-02 15:37:26,089 [INFO] src.adapters.parts_mixin: Trying ClfNodes at: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes
2026-04-02 15:37:26,105 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24filter=ContainerType%20eq%20%27Product%27 "HTTP/1.1 400 400"
2026-04-02 15:37:26,106 [INFO] src.adapters.parts_mixin: Container $filter fehlgeschlagen – lade alle Container ungefiltert
2026-04-02 15:37:26,158 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes "HTTP/1.1 200 200"
2026-04-02 15:37:26,159 [INFO] src.adapters.parts_mixin: ClfNodes https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes → HTTP 200
2026-04-02 15:37:26,159 [INFO] src.adapters.parts_mixin: ClfNodes loaded 1 items from https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes
2026-04-02 15:37:26,160 [INFO] src.adapters.parts_mixin: ClfNode sample keys: ['ID', 'DisplayName', 'InternalName', 'Description', 'HierarchicalPath', 'Keywords', 'Instantiable', 'Image', 'ClfNodeAttributes']
2026-04-02 15:37:26,160 [INFO] src.adapters.parts_mixin: ClfNode[0]: {'ID': 'Balluff', 'DisplayName': 'Balluff', 'InternalName': 'Balluff', 'Description': None, 'HierarchicalPath': 'Balluff', 'Keywords': None, 'Instantiable': False, 'Image': None, 'ClfNodeAttributes': []}
2026-04-02 15:37:26,161 [INFO] api: GET /api/classification-nodes → 200 (174.4 ms)
INFO:     127.0.0.1:62172 - "GET /api/classification-nodes HTTP/1.1" 200 OK
2026-04-02 15:37:26,212 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24select=Number&%24top=200 "HTTP/1.1 200 200"
2026-04-02 15:37:26,240 [INFO] src.adapters.parts_mixin: Trying ClfNodes at: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ClfStructure/ClfNodes
2026-04-02 15:37:26,260 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ClfStructure/ClfNodes "HTTP/1.1 404 404"
2026-04-02 15:37:26,261 [INFO] src.adapters.parts_mixin: ClfNodes https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ClfStructure/ClfNodes → HTTP 404
2026-04-02 15:37:26,261 [INFO] src.adapters.parts_mixin: Trying ClfNodes at: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes
2026-04-02 15:37:26,323 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes "HTTP/1.1 200 200"
2026-04-02 15:37:26,324 [INFO] src.adapters.parts_mixin: ClfNodes https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes → HTTP 200
2026-04-02 15:37:26,324 [INFO] src.adapters.parts_mixin: ClfNodes loaded 1 items from https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes
2026-04-02 15:37:26,325 [INFO] src.adapters.parts_mixin: ClfNode sample keys: ['ID', 'DisplayName', 'InternalName', 'Description', 'HierarchicalPath', 'Keywords', 'Instantiable', 'Image', 'ClfNodeAttributes']
2026-04-02 15:37:26,325 [INFO] src.adapters.parts_mixin: ClfNode[0]: {'ID': 'Balluff', 'DisplayName': 'Balluff', 'InternalName': 'Balluff', 'Description': None, 'HierarchicalPath': 'Balluff', 'Keywords': None, 'Instantiable': False, 'Image': None, 'ClfNodeAttributes': []}
2026-04-02 15:37:26,327 [INFO] api: GET /api/classification-nodes → 200 (87.5 ms)
INFO:     127.0.0.1:63946 - "GET /api/classification-nodes HTTP/1.1" 200 OK
2026-04-02 15:37:26,511 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 15:37:26,640 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 15:37:26,712 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers "HTTP/1.1 200 200"
2026-04-02 15:37:26,771 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 15:37:26,794 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 15:37:26,899 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 15:37:26,939 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 15:37:27,032 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 15:37:27,051 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 15:37:27,165 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 15:37:27,184 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 15:37:27,311 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 15:37:27,313 [INFO] src.adapters.parts_mixin: Found 8 Part subtypes from 200 parts: ['BALAUXPART', 'BALCOLLECTIONPART', 'BALENCDOCPART', 'BALEQUIPMENTPART', 'BALMECHATRONICPART', 'BALPACKAGEPART', 'BALPRODUCTPART', 'BALRAWMATERIAL']
2026-04-02 15:37:27,315 [INFO] api: GET /api/part-subtypes → 200 (1328.0 ms)
INFO:     127.0.0.1:62171 - "GET /api/part-subtypes HTTP/1.1" 200 OK
2026-04-02 15:37:27,344 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 15:37:27,469 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 15:37:27,502 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24select=Number&%24top=200 "HTTP/1.1 200 200"
2026-04-02 15:37:27,602 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 15:37:27,645 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 15:37:27,708 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=200 "HTTP/1.1 200 200"
2026-04-02 15:37:27,808 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 15:37:27,809 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=225 "HTTP/1.1 200 200"
2026-04-02 15:37:27,899 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=250 "HTTP/1.1 200 200"
2026-04-02 15:37:27,931 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 15:37:28,017 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=275 "HTTP/1.1 200 200"
2026-04-02 15:37:28,090 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 15:37:28,193 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=300 "HTTP/1.1 200 200"
2026-04-02 15:37:28,241 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 15:37:28,370 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 15:37:28,375 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=325 "HTTP/1.1 200 200"
2026-04-02 15:37:28,519 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 15:37:28,520 [INFO] src.adapters.parts_mixin: Found 8 Part subtypes from 200 parts: ['BALAUXPART', 'BALCOLLECTIONPART', 'BALENCDOCPART', 'BALEQUIPMENTPART', 'BALMECHATRONICPART', 'BALPACKAGEPART', 'BALPRODUCTPART', 'BALRAWMATERIAL']
2026-04-02 15:37:28,522 [INFO] api: GET /api/part-subtypes → 200 (1200.2 ms)
INFO:     127.0.0.1:53672 - "GET /api/part-subtypes HTTP/1.1" 200 OK
2026-04-02 15:37:28,532 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=350 "HTTP/1.1 200 200"
2026-04-02 15:37:28,774 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=375 "HTTP/1.1 200 200"
2026-04-02 15:37:28,988 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=400 "HTTP/1.1 200 200"
2026-04-02 15:37:29,161 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=425 "HTTP/1.1 200 200"
2026-04-02 15:37:29,299 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=450 "HTTP/1.1 200 200"
2026-04-02 15:37:29,545 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=475 "HTTP/1.1 200 200"
2026-04-02 15:37:29,774 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=500 "HTTP/1.1 200 200"
2026-04-02 15:37:29,859 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=525 "HTTP/1.1 200 200"
2026-04-02 15:37:29,961 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=550 "HTTP/1.1 200 200"
2026-04-02 15:37:30,091 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=575 "HTTP/1.1 200 200"
2026-04-02 15:37:30,301 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=600 "HTTP/1.1 200 200"
2026-04-02 15:37:30,493 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=625 "HTTP/1.1 200 200"
2026-04-02 15:37:30,605 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=650 "HTTP/1.1 200 200"
2026-04-02 15:37:30,694 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=675 "HTTP/1.1 200 200"
2026-04-02 15:37:30,819 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=700 "HTTP/1.1 200 200"
2026-04-02 15:37:30,912 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=725 "HTTP/1.1 200 200"
2026-04-02 15:37:31,103 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=750 "HTTP/1.1 200 200"
2026-04-02 15:37:31,281 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=775 "HTTP/1.1 200 200"
2026-04-02 15:37:31,406 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=800 "HTTP/1.1 200 200"
2026-04-02 15:37:31,581 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=825 "HTTP/1.1 200 200"
2026-04-02 15:37:31,761 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=850 "HTTP/1.1 200 200"
2026-04-02 15:37:31,985 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=875 "HTTP/1.1 200 200"
2026-04-02 15:37:32,154 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=900 "HTTP/1.1 200 200"
2026-04-02 15:37:32,333 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=925 "HTTP/1.1 200 200"
2026-04-02 15:37:32,514 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=950 "HTTP/1.1 200 200"
2026-04-02 15:37:32,612 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=975 "HTTP/1.1 200 200"
2026-04-02 15:37:32,861 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=1000 "HTTP/1.1 200 200"
2026-04-02 15:37:33,076 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=1025 "HTTP/1.1 200 200"
2026-04-02 15:37:33,352 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=1050 "HTTP/1.1 200 200"
2026-04-02 15:37:33,587 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=1075 "HTTP/1.1 200 200"
2026-04-02 15:37:33,589 [INFO] src.services.parts_service: Container-Record Felder: ['@odata.type', 'CreatedOn', 'ID', 'LastModified', 'CreatedBy', 'Description', 'Name', 'OrganizationID', 'OrganizationName', 'PrivateAccess']
2026-04-02 15:37:33,589 [INFO] src.services.parts_service: Container[0] komplett: {'@odata.type': '#PTC.DataAdmin.Site', 'CreatedOn': '2021-07-08T16:41:51+02:00', 'ID': 'OR:wt.inf.container.ExchangeContainer:6', 'LastModified': '2021-07-08T16:43:10+02:00', 'CreatedBy': 'Site, Administrator', 'Description': 'Windchill system site', 'Name': 'Site', 'OrganizationID': {'CodingSystem': None, 'UniqueIdentifier': None}, 'OrganizationName': 'BALLUFF', 'PrivateAccess': True}
2026-04-02 15:37:33,590 [INFO] src.services.parts_service: Container[1] komplett: {'@odata.type': '#PTC.DataAdmin.OrganizationContainer', 'CreatedOn': '2021-07-08T16:47:17+02:00', 'ID': 'OR:wt.inf.container.OrgContainer:93622', 'LastModified': '2022-09-13T18:21:56+02:00', 'CreatedBy': 'Site, Administrator', 'Description': 'Context for the organization hosting this Windchill installation.', 'Name': 'BALLUFF', 'OrganizationID': {'CodingSystem': None, 'UniqueIdentifier': None}, 'OrganizationName': 'BALLUFF', 'PrivateAccess': True}
2026-04-02 15:37:33,591 [INFO] src.services.parts_service: Container[2] komplett: {'@odata.type': '#PTC.DataAdmin.LibraryContainer', 'CreatedOn': '2021-07-30T14:37:08+02:00', 'ID': 'OR:wt.inf.library.WTLibrary:133606', 'LastModified': '2025-02-13T08:22:50+01:00', 'CreatedBy': 'Sibylle Hebenstreit', 'Description': 'P - Auxiliary Material', 'Name': 'P - Auxiliary Material', 'OrganizationID': {'CodingSystem': None, 'UniqueIdentifier': None}, 'OrganizationName': 'BALLUFF', 'PrivateAccess': False}
2026-04-02 15:37:33,601 [INFO] api: GET /api/containers → 200 (7614.5 ms)
INFO:     127.0.0.1:62170 - "GET /api/containers HTTP/1.1" 200 OK
2026-04-02 15:37:33,973 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24filter=ContainerType%20eq%20%27Product%27 "HTTP/1.1 400 400"
2026-04-02 15:37:33,975 [INFO] src.adapters.parts_mixin: Container $filter fehlgeschlagen – lade alle Container ungefiltert
2026-04-02 15:37:34,195 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers "HTTP/1.1 200 200"
2026-04-02 15:37:34,326 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 15:37:34,436 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 15:37:34,604 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 15:37:34,746 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 15:37:34,897 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 15:37:35,027 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 15:37:35,122 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 15:37:35,315 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=200 "HTTP/1.1 200 200"
2026-04-02 15:37:35,440 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=225 "HTTP/1.1 200 200"
2026-04-02 15:37:35,544 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=250 "HTTP/1.1 200 200"
2026-04-02 15:37:35,708 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=275 "HTTP/1.1 200 200"
2026-04-02 15:37:35,911 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=300 "HTTP/1.1 200 200"
2026-04-02 15:37:36,111 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=325 "HTTP/1.1 200 200"
2026-04-02 15:37:36,229 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=350 "HTTP/1.1 200 200"
2026-04-02 15:37:36,320 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=375 "HTTP/1.1 200 200"
2026-04-02 15:37:36,534 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=400 "HTTP/1.1 200 200"
2026-04-02 15:37:36,691 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=425 "HTTP/1.1 200 200"
2026-04-02 15:37:36,874 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=450 "HTTP/1.1 200 200"
2026-04-02 15:37:37,035 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=475 "HTTP/1.1 200 200"
2026-04-02 15:37:37,180 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=500 "HTTP/1.1 200 200"
2026-04-02 15:37:37,370 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=525 "HTTP/1.1 200 200"
2026-04-02 15:37:37,580 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=550 "HTTP/1.1 200 200"
2026-04-02 15:37:37,726 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=575 "HTTP/1.1 200 200"
2026-04-02 15:37:37,951 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=600 "HTTP/1.1 200 200"
2026-04-02 15:37:38,109 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=625 "HTTP/1.1 200 200"
2026-04-02 15:37:38,239 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=650 "HTTP/1.1 200 200"
2026-04-02 15:37:38,475 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=675 "HTTP/1.1 200 200"
2026-04-02 15:37:38,728 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=700 "HTTP/1.1 200 200"
2026-04-02 15:37:38,910 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=725 "HTTP/1.1 200 200"
2026-04-02 15:37:39,027 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=750 "HTTP/1.1 200 200"
2026-04-02 15:37:39,125 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=775 "HTTP/1.1 200 200"
2026-04-02 15:37:39,330 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=800 "HTTP/1.1 200 200"
2026-04-02 15:37:39,437 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=825 "HTTP/1.1 200 200"
2026-04-02 15:37:39,596 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=850 "HTTP/1.1 200 200"
2026-04-02 15:37:39,691 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=875 "HTTP/1.1 200 200"
2026-04-02 15:37:39,890 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=900 "HTTP/1.1 200 200"
2026-04-02 15:37:40,025 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=925 "HTTP/1.1 200 200"
2026-04-02 15:37:40,188 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=950 "HTTP/1.1 200 200"
2026-04-02 15:37:40,436 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=975 "HTTP/1.1 200 200"
2026-04-02 15:37:40,582 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=1000 "HTTP/1.1 200 200"
2026-04-02 15:37:40,723 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=1025 "HTTP/1.1 200 200"
2026-04-02 15:37:40,886 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=1050 "HTTP/1.1 200 200"
2026-04-02 15:37:40,982 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$skiptoken=1075 "HTTP/1.1 200 200"
2026-04-02 15:37:40,983 [INFO] src.services.parts_service: Container-Record Felder: ['@odata.type', 'CreatedOn', 'ID', 'LastModified', 'CreatedBy', 'Description', 'Name', 'OrganizationID', 'OrganizationName', 'PrivateAccess']
2026-04-02 15:37:40,984 [INFO] src.services.parts_service: Container[0] komplett: {'@odata.type': '#PTC.DataAdmin.Site', 'CreatedOn': '2021-07-08T16:41:51+02:00', 'ID': 'OR:wt.inf.container.ExchangeContainer:6', 'LastModified': '2021-07-08T16:43:10+02:00', 'CreatedBy': 'Site, Administrator', 'Description': 'Windchill system site', 'Name': 'Site', 'OrganizationID': {'CodingSystem': None, 'UniqueIdentifier': None}, 'OrganizationName': 'BALLUFF', 'PrivateAccess': True}
2026-04-02 15:37:40,985 [INFO] src.services.parts_service: Container[1] komplett: {'@odata.type': '#PTC.DataAdmin.OrganizationContainer', 'CreatedOn': '2021-07-08T16:47:17+02:00', 'ID': 'OR:wt.inf.container.OrgContainer:93622', 'LastModified': '2022-09-13T18:21:56+02:00', 'CreatedBy': 'Site, Administrator', 'Description': 'Context for the organization hosting this Windchill installation.', 'Name': 'BALLUFF', 'OrganizationID': {'CodingSystem': None, 'UniqueIdentifier': None}, 'OrganizationName': 'BALLUFF', 'PrivateAccess': True}
2026-04-02 15:37:40,985 [INFO] src.services.parts_service: Container[2] komplett: {'@odata.type': '#PTC.DataAdmin.LibraryContainer', 'CreatedOn': '2021-07-30T14:37:08+02:00', 'ID': 'OR:wt.inf.library.WTLibrary:133606', 'LastModified': '2025-02-13T08:22:50+01:00', 'CreatedBy': 'Sibylle Hebenstreit', 'Description': 'P - Auxiliary Material', 'Name': 'P - Auxiliary Material', 'OrganizationID': {'CodingSystem': None, 'UniqueIdentifier': None}, 'OrganizationName': 'BALLUFF', 'PrivateAccess': False}
2026-04-02 15:37:40,998 [INFO] api: GET /api/containers → 200 (7076.1 ms)
INFO:     127.0.0.1:55113 - "GET /api/containers HTTP/1.1" 200 OK
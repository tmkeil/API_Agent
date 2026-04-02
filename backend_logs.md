INFO:     Will watch for changes in these directories: ['C:\\Users\\keilt\\azure_api_agent\\windchill-api']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [20264] using WatchFiles
INFO:     Started server process [24568]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2026-04-02 15:44:58,871 [INFO] watchfiles.main: 1 change detected
2026-04-02 15:44:59,049 [INFO] api: GET /api/auth/me → 401 (1.0 ms)
INFO:     127.0.0.1:52474 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-02 15:44:59,053 [INFO] api: GET /api/auth/me → 401 (0.6 ms)
INFO:     127.0.0.1:52476 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-02 15:44:59,068 [INFO] api: GET /api/auth/systems → 200 (0.5 ms)
INFO:     127.0.0.1:52478 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-02 15:44:59,072 [INFO] api: GET /api/auth/systems → 200 (0.4 ms)
INFO:     127.0.0.1:52480 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-02 15:44:59,791 [INFO] watchfiles.main: 13 changes detected
2026-04-02 15:45:05,785 [INFO] src.routers.auth: Login-Versuch: system=dev url=https://plm-dev.neuhausen.balluff.net/Windchill user=keilt
2026-04-02 15:45:05,789 [INFO] src.adapters.base: Connecting to https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6
2026-04-02 15:45:06,718 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt "HTTP/1.1 307 307"
2026-04-02 15:45:06,763 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ "HTTP/1.1 200 200"
2026-04-02 15:45:06,764 [INFO] src.adapters.base: Auth-Probe: status=200 url=https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ content-type=application/json;odata.metadata=minimal www-authenticate=
2026-04-02 15:45:06,764 [INFO] src.adapters.base: Basic Auth akzeptiert (status=200)
2026-04-02 15:45:06,800 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/PTC/GetCSRFToken() "HTTP/1.1 200 200"
2026-04-02 15:45:06,801 [INFO] src.adapters.base: CSRF-Token erhalten: CSRF_NONCE=yOLKkyGmagEt…
2026-04-02 15:45:06,803 [INFO] api: POST /api/auth/login → 200 (1021.2 ms)
INFO:     127.0.0.1:56250 - "POST /api/auth/login HTTP/1.1" 200 OK
2026-04-02 15:45:09,620 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers/PTC.DataAdmin.PDMLinkProduct "HTTP/1.1 400 400"
2026-04-02 15:45:09,743 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24filter=ContainerType%20eq%20%27Product%27 "HTTP/1.1 400 400"
2026-04-02 15:45:09,744 [INFO] src.adapters.parts_mixin: Container-Filter fehlgeschlagen – lade alle mit $select
2026-04-02 15:45:09,881 [INFO] src.adapters.parts_mixin: Trying ClfNodes at: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes
2026-04-02 15:45:09,922 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24select=ID%2CName "HTTP/1.1 200 200"
2026-04-02 15:45:09,967 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes?%24expand=Children%28%24levels%3Dmax%29 "HTTP/1.1 400 400"
2026-04-02 15:45:09,968 [INFO] src.adapters.parts_mixin: ClfNodes https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes ($expand) → HTTP 400
2026-04-02 15:45:09,992 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 15:45:10,045 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24select=Number&%24top=200 "HTTP/1.1 200 200"
2026-04-02 15:45:10,060 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 15:45:10,103 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes "HTTP/1.1 200 200"
2026-04-02 15:45:10,104 [INFO] src.adapters.parts_mixin: ClfNodes https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes (plain) → HTTP 200
2026-04-02 15:45:10,105 [INFO] src.adapters.parts_mixin: ClfNodes root: 1 items from https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes
2026-04-02 15:45:10,118 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 15:45:10,126 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes('Balluff')/Children "HTTP/1.1 404 404"
2026-04-02 15:45:10,127 [INFO] src.adapters.parts_mixin: ClfNodes total (flat): 1 Knoten
2026-04-02 15:45:10,128 [INFO] src.adapters.parts_mixin: ClfNode sample keys: ['ID', 'DisplayName', 'InternalName', 'Description', 'HierarchicalPath', 'Keywords', 'Instantiable', 'Image', 'ClfNodeAttributes']
2026-04-02 15:45:10,128 [INFO] src.adapters.parts_mixin: ClfNode[0]: {'ID': 'Balluff', 'DisplayName': 'Balluff', 'InternalName': 'Balluff', 'Description': None, 'HierarchicalPath': 'Balluff', 'Keywords': None, 'Instantiable': False, 'Image': None}
2026-04-02 15:45:10,129 [INFO] src.services.parts_service: Classification raw items: 1
2026-04-02 15:45:10,129 [INFO] src.services.parts_service: Classification nodes (instantiable): 0
2026-04-02 15:45:10,131 [INFO] api: GET /api/classification-nodes → 200 (251.9 ms)
INFO:     127.0.0.1:51388 - "GET /api/classification-nodes HTTP/1.1" 200 OK
2026-04-02 15:45:10,159 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 15:45:10,184 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 15:45:10,257 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 15:45:10,270 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 15:45:10,318 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 15:45:10,449 [INFO] src.adapters.parts_mixin: Trying ClfNodes at: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes
2026-04-02 15:45:10,483 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes?%24expand=Children%28%24levels%3Dmax%29 "HTTP/1.1 400 400"
2026-04-02 15:45:10,484 [INFO] src.adapters.parts_mixin: ClfNodes https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes ($expand) → HTTP 400
2026-04-02 15:45:10,509 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 15:45:10,547 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 15:45:10,627 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes "HTTP/1.1 200 200"
2026-04-02 15:45:10,628 [INFO] src.adapters.parts_mixin: ClfNodes https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes (plain) → HTTP 200
2026-04-02 15:45:10,629 [INFO] src.adapters.parts_mixin: ClfNodes root: 1 items from https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes
2026-04-02 15:45:10,639 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=200 "HTTP/1.1 200 200"
2026-04-02 15:45:10,658 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/ClfStructure/ClfNodes('Balluff')/Children "HTTP/1.1 404 404"
2026-04-02 15:45:10,659 [INFO] src.adapters.parts_mixin: ClfNodes total (flat): 1 Knoten
2026-04-02 15:45:10,659 [INFO] src.adapters.parts_mixin: ClfNode sample keys: ['ID', 'DisplayName', 'InternalName', 'Description', 'HierarchicalPath', 'Keywords', 'Instantiable', 'Image', 'ClfNodeAttributes']
2026-04-02 15:45:10,660 [INFO] src.adapters.parts_mixin: ClfNode[0]: {'ID': 'Balluff', 'DisplayName': 'Balluff', 'InternalName': 'Balluff', 'Description': None, 'HierarchicalPath': 'Balluff', 'Keywords': None, 'Instantiable': False, 'Image': None}
2026-04-02 15:45:10,661 [INFO] src.services.parts_service: Classification raw items: 1
2026-04-02 15:45:10,661 [INFO] src.services.parts_service: Classification nodes (instantiable): 0
2026-04-02 15:45:10,663 [INFO] api: GET /api/classification-nodes → 200 (215.3 ms)
INFO:     127.0.0.1:64107 - "GET /api/classification-nodes HTTP/1.1" 200 OK
2026-04-02 15:45:10,687 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 15:45:10,778 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=225 "HTTP/1.1 200 200"
2026-04-02 15:45:10,875 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 15:45:10,890 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=250 "HTTP/1.1 200 200"
2026-04-02 15:45:10,978 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=275 "HTTP/1.1 200 200"
2026-04-02 15:45:11,046 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 15:45:11,092 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=300 "HTTP/1.1 200 200"
2026-04-02 15:45:11,155 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 15:45:11,156 [INFO] src.adapters.parts_mixin: Found 8 Part subtypes from 200 parts: ['BALAUXPART', 'BALCOLLECTIONPART', 'BALENCDOCPART', 'BALEQUIPMENTPART', 'BALMECHATRONICPART', 'BALPACKAGEPART', 'BALPRODUCTPART', 'BALRAWMATERIAL']
2026-04-02 15:45:11,159 [INFO] api: GET /api/part-subtypes → 200 (1279.4 ms)
INFO:     127.0.0.1:51387 - "GET /api/part-subtypes HTTP/1.1" 200 OK
2026-04-02 15:45:11,177 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=325 "HTTP/1.1 200 200"
2026-04-02 15:45:11,257 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=350 "HTTP/1.1 200 200"
2026-04-02 15:45:11,363 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=375 "HTTP/1.1 200 200"
2026-04-02 15:45:11,499 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=400 "HTTP/1.1 200 200"
2026-04-02 15:45:11,617 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24select=Number&%24top=200 "HTTP/1.1 200 200"
2026-04-02 15:45:11,638 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=425 "HTTP/1.1 200 200"
2026-04-02 15:45:11,721 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=450 "HTTP/1.1 200 200"
2026-04-02 15:45:11,738 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 15:45:11,776 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=475 "HTTP/1.1 200 200"
2026-04-02 15:45:11,845 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 15:45:11,846 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=500 "HTTP/1.1 200 200"
2026-04-02 15:45:11,958 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=525 "HTTP/1.1 200 200"
2026-04-02 15:45:11,978 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 15:45:12,039 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=550 "HTTP/1.1 200 200"
2026-04-02 15:45:12,139 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=575 "HTTP/1.1 200 200"
2026-04-02 15:45:12,251 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=600 "HTTP/1.1 200 200"
2026-04-02 15:45:12,344 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=625 "HTTP/1.1 200 200"
2026-04-02 15:45:12,347 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 15:45:12,461 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 15:45:12,480 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=650 "HTTP/1.1 200 200"
2026-04-02 15:45:12,583 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 15:45:12,621 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=675 "HTTP/1.1 200 200"
2026-04-02 15:45:12,714 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=700 "HTTP/1.1 200 200"
2026-04-02 15:45:12,718 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 15:45:12,719 [INFO] src.adapters.parts_mixin: Found 8 Part subtypes from 200 parts: ['BALAUXPART', 'BALCOLLECTIONPART', 'BALENCDOCPART', 'BALEQUIPMENTPART', 'BALMECHATRONICPART', 'BALPACKAGEPART', 'BALPRODUCTPART', 'BALRAWMATERIAL']
2026-04-02 15:45:12,721 [INFO] api: GET /api/part-subtypes → 200 (1239.8 ms)
INFO:     127.0.0.1:65272 - "GET /api/part-subtypes HTTP/1.1" 200 OK
2026-04-02 15:45:12,815 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=725 "HTTP/1.1 200 200"
2026-04-02 15:45:12,900 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=750 "HTTP/1.1 200 200"
2026-04-02 15:45:13,023 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=775 "HTTP/1.1 200 200"
2026-04-02 15:45:13,127 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=800 "HTTP/1.1 200 200"
2026-04-02 15:45:13,206 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=825 "HTTP/1.1 200 200"
2026-04-02 15:45:13,272 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=850 "HTTP/1.1 200 200"
2026-04-02 15:45:13,392 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=875 "HTTP/1.1 200 200"
2026-04-02 15:45:13,469 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=900 "HTTP/1.1 200 200"
2026-04-02 15:45:13,568 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=925 "HTTP/1.1 200 200"
2026-04-02 15:45:13,732 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=950 "HTTP/1.1 200 200"
2026-04-02 15:45:13,902 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=975 "HTTP/1.1 200 200"
2026-04-02 15:45:14,039 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1000 "HTTP/1.1 200 200"
2026-04-02 15:45:14,175 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1025 "HTTP/1.1 200 200"
2026-04-02 15:45:14,285 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1050 "HTTP/1.1 200 200"
2026-04-02 15:45:14,375 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1075 "HTTP/1.1 200 200"
2026-04-02 15:45:14,376 [INFO] src.services.parts_service: Container-Record Felder: ['@odata.type', 'ID', 'Name']
2026-04-02 15:45:14,377 [INFO] src.services.parts_service: Container[0] komplett: {'@odata.type': '#PTC.DataAdmin.Site', 'ID': 'OR:wt.inf.container.ExchangeContainer:6', 'Name': 'Site'}
2026-04-02 15:45:14,377 [INFO] src.services.parts_service: Container[1] komplett: {'@odata.type': '#PTC.DataAdmin.OrganizationContainer', 'ID': 'OR:wt.inf.container.OrgContainer:93622', 'Name': 'BALLUFF'}
2026-04-02 15:45:14,377 [INFO] src.services.parts_service: Container[2] komplett: {'@odata.type': '#PTC.DataAdmin.LibraryContainer', 'ID': 'OR:wt.inf.library.WTLibrary:133606', 'Name': 'P - Auxiliary Material'}
2026-04-02 15:45:14,386 [INFO] api: GET /api/containers → 200 (4817.2 ms)
INFO:     127.0.0.1:51196 - "GET /api/containers HTTP/1.1" 200 OK
2026-04-02 15:45:14,739 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers/PTC.DataAdmin.PDMLinkProduct "HTTP/1.1 400 400"
2026-04-02 15:45:14,785 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24filter=ContainerType%20eq%20%27Product%27 "HTTP/1.1 400 400"
2026-04-02 15:45:14,786 [INFO] src.adapters.parts_mixin: Container-Filter fehlgeschlagen – lade alle mit $select
2026-04-02 15:45:14,967 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24select=ID%2CName "HTTP/1.1 200 200"
2026-04-02 15:45:15,020 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 15:45:15,097 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 15:45:15,173 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 15:45:15,271 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 15:45:15,352 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 15:45:15,466 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 15:45:15,538 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 15:45:15,650 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=200 "HTTP/1.1 200 200"
2026-04-02 15:45:15,739 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=225 "HTTP/1.1 200 200"
2026-04-02 15:45:15,870 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=250 "HTTP/1.1 200 200"
2026-04-02 15:45:15,969 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=275 "HTTP/1.1 200 200"
2026-04-02 15:45:16,049 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=300 "HTTP/1.1 200 200"
2026-04-02 15:45:16,187 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=325 "HTTP/1.1 200 200"
2026-04-02 15:45:16,309 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=350 "HTTP/1.1 200 200"
2026-04-02 15:45:16,407 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=375 "HTTP/1.1 200 200"
2026-04-02 15:45:16,522 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=400 "HTTP/1.1 200 200"
2026-04-02 15:45:16,628 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=425 "HTTP/1.1 200 200"
2026-04-02 15:45:16,749 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=450 "HTTP/1.1 200 200"
2026-04-02 15:45:16,874 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=475 "HTTP/1.1 200 200"
2026-04-02 15:45:16,942 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=500 "HTTP/1.1 200 200"
2026-04-02 15:45:17,052 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=525 "HTTP/1.1 200 200"
2026-04-02 15:45:17,146 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=550 "HTTP/1.1 200 200"
2026-04-02 15:45:17,285 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=575 "HTTP/1.1 200 200"
2026-04-02 15:45:17,401 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=600 "HTTP/1.1 200 200"
2026-04-02 15:45:17,581 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=625 "HTTP/1.1 200 200"
2026-04-02 15:45:17,766 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=650 "HTTP/1.1 200 200"
2026-04-02 15:45:17,914 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=675 "HTTP/1.1 200 200"
2026-04-02 15:45:17,999 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=700 "HTTP/1.1 200 200"
2026-04-02 15:45:18,066 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=725 "HTTP/1.1 200 200"
2026-04-02 15:45:18,258 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=750 "HTTP/1.1 200 200"
2026-04-02 15:45:18,418 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=775 "HTTP/1.1 200 200"
2026-04-02 15:45:18,512 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=800 "HTTP/1.1 200 200"
2026-04-02 15:45:18,596 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=825 "HTTP/1.1 200 200"
2026-04-02 15:45:18,744 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=850 "HTTP/1.1 200 200"
2026-04-02 15:45:18,869 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=875 "HTTP/1.1 200 200"
2026-04-02 15:45:18,948 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=900 "HTTP/1.1 200 200"
2026-04-02 15:45:19,080 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=925 "HTTP/1.1 200 200"
2026-04-02 15:45:19,223 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=950 "HTTP/1.1 200 200"
2026-04-02 15:45:19,292 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=975 "HTTP/1.1 200 200"
2026-04-02 15:45:19,365 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1000 "HTTP/1.1 200 200"
2026-04-02 15:45:19,437 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1025 "HTTP/1.1 200 200"
2026-04-02 15:45:19,530 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1050 "HTTP/1.1 200 200"
2026-04-02 15:45:19,601 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1075 "HTTP/1.1 200 200"
2026-04-02 15:45:19,602 [INFO] src.services.parts_service: Container-Record Felder: ['@odata.type', 'ID', 'Name']
2026-04-02 15:45:19,603 [INFO] src.services.parts_service: Container[0] komplett: {'@odata.type': '#PTC.DataAdmin.Site', 'ID': 'OR:wt.inf.container.ExchangeContainer:6', 'Name': 'Site'}
2026-04-02 15:45:19,603 [INFO] src.services.parts_service: Container[1] komplett: {'@odata.type': '#PTC.DataAdmin.OrganizationContainer', 'ID': 'OR:wt.inf.container.OrgContainer:93622', 'Name': 'BALLUFF'}
2026-04-02 15:45:19,604 [INFO] src.services.parts_service: Container[2] komplett: {'@odata.type': '#PTC.DataAdmin.LibraryContainer', 'ID': 'OR:wt.inf.library.WTLibrary:133606', 'Name': 'P - Auxiliary Material'}
2026-04-02 15:45:19,612 [INFO] api: GET /api/containers → 200 (4914.4 ms)
INFO:     127.0.0.1:51160 - "GET /api/containers HTTP/1.1" 200 OK
INFO:     Will watch for changes in these directories: ['C:\\Users\\keilt\\azure_api_agent\\windchill-api']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [15364] using WatchFiles
INFO:     Started server process [24144]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2026-04-02 15:57:41,765 [INFO] api: GET /api/auth/me → 401 (0.9 ms)
INFO:     127.0.0.1:62735 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-02 15:57:41,769 [INFO] api: GET /api/auth/me → 401 (0.5 ms)
INFO:     127.0.0.1:62737 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-02 15:57:41,776 [INFO] api: GET /api/auth/systems → 200 (0.6 ms)
INFO:     127.0.0.1:62739 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-02 15:57:41,779 [INFO] api: GET /api/auth/systems → 200 (0.4 ms)
INFO:     127.0.0.1:62741 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-02 15:57:42,339 [INFO] src.routers.auth: Login-Versuch: system=dev url=https://plm-dev.neuhausen.balluff.net/Windchill user=keilt
2026-04-02 15:57:42,341 [INFO] src.adapters.base: Connecting to https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6
2026-04-02 15:57:42,478 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt "HTTP/1.1 307 307"
2026-04-02 15:57:42,527 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ "HTTP/1.1 200 200"
2026-04-02 15:57:42,528 [INFO] src.adapters.base: Auth-Probe: status=200 url=https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ content-type=application/json;odata.metadata=minimal www-authenticate=
2026-04-02 15:57:42,529 [INFO] src.adapters.base: Basic Auth akzeptiert (status=200)
2026-04-02 15:57:42,563 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/PTC/GetCSRFToken() "HTTP/1.1 200 200"
2026-04-02 15:57:42,563 [INFO] src.adapters.base: CSRF-Token erhalten: CSRF_NONCE=OmiWw+se7bXY…
2026-04-02 15:57:42,565 [INFO] api: POST /api/auth/login → 200 (228.1 ms)
INFO:     127.0.0.1:62743 - "POST /api/auth/login HTTP/1.1" 200 OK
2026-04-02 15:57:54,765 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers/PTC.DataAdmin.PDMLinkProduct "HTTP/1.1 400 400"
2026-04-02 15:57:54,797 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24select=Number%2CBALCLASSIFICATIONBINDINGWTPART&%24top=500 "HTTP/1.1 400 400"
2026-04-02 15:57:54,798 [WARNING] src.adapters.parts_mixin: get_classification_nodes: Keine Parts geladen
2026-04-02 15:57:54,798 [INFO] src.services.parts_service: Classification raw items: 0
2026-04-02 15:57:54,799 [INFO] src.services.parts_service: Classification nodes: 0
2026-04-02 15:57:54,801 [INFO] api: GET /api/classification-nodes → 200 (150.6 ms)
INFO:     127.0.0.1:62736 - "GET /api/classification-nodes HTTP/1.1" 200 OK
2026-04-02 15:57:54,898 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24filter=ContainerType%20eq%20%27Product%27 "HTTP/1.1 400 400"
2026-04-02 15:57:54,899 [INFO] src.adapters.parts_mixin: Container-Filter fehlgeschlagen – lade alle mit $select
2026-04-02 15:57:54,943 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24select=Number&%24top=200 "HTTP/1.1 200 200"
2026-04-02 15:57:55,053 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24select=ID%2CName "HTTP/1.1 200 200"
2026-04-02 15:57:55,057 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24select=Number%2CBALCLASSIFICATIONBINDINGWTPART&%24top=500 "HTTP/1.1 400 400"
2026-04-02 15:57:55,058 [WARNING] src.adapters.parts_mixin: get_classification_nodes: Keine Parts geladen
2026-04-02 15:57:55,058 [INFO] src.services.parts_service: Classification raw items: 0
2026-04-02 15:57:55,059 [INFO] src.services.parts_service: Classification nodes: 0
2026-04-02 15:57:55,061 [INFO] api: GET /api/classification-nodes → 200 (152.0 ms)
INFO:     127.0.0.1:57310 - "GET /api/classification-nodes HTTP/1.1" 200 OK
2026-04-02 15:57:55,149 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 15:57:55,157 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 15:57:55,231 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 15:57:55,312 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 15:57:55,331 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 15:57:55,393 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 15:57:55,490 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 15:57:55,517 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 15:57:55,596 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 15:57:55,699 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 15:57:55,789 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=200 "HTTP/1.1 200 200"
2026-04-02 15:57:55,871 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 15:57:55,899 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=225 "HTTP/1.1 200 200"
2026-04-02 15:57:56,025 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=250 "HTTP/1.1 200 200"
2026-04-02 15:57:56,037 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 15:57:56,114 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=275 "HTTP/1.1 200 200"
2026-04-02 15:57:56,214 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=300 "HTTP/1.1 200 200"
2026-04-02 15:57:56,235 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 15:57:56,319 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=325 "HTTP/1.1 200 200"
2026-04-02 15:57:56,421 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=350 "HTTP/1.1 200 200"
2026-04-02 15:57:56,434 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 15:57:56,435 [INFO] src.adapters.parts_mixin: Found 8 Part subtypes from 200 parts: ['BALAUXPART', 'BALCOLLECTIONPART', 'BALENCDOCPART', 'BALEQUIPMENTPART', 'BALMECHATRONICPART', 'BALPACKAGEPART', 'BALPRODUCTPART', 'BALRAWMATERIAL']
2026-04-02 15:57:56,437 [INFO] api: GET /api/part-subtypes → 200 (1786.8 ms)
INFO:     127.0.0.1:62735 - "GET /api/part-subtypes HTTP/1.1" 200 OK
2026-04-02 15:57:56,526 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=375 "HTTP/1.1 200 200"
2026-04-02 15:57:56,558 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24select=Number&%24top=200 "HTTP/1.1 200 200"
2026-04-02 15:57:56,646 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=400 "HTTP/1.1 200 200"
2026-04-02 15:57:56,715 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 15:57:56,758 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=425 "HTTP/1.1 200 200"
2026-04-02 15:57:56,816 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=450 "HTTP/1.1 200 200"
2026-04-02 15:57:56,823 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 15:57:56,947 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=475 "HTTP/1.1 200 200"
2026-04-02 15:57:57,003 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 15:57:57,058 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=500 "HTTP/1.1 200 200"
2026-04-02 15:57:57,161 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=525 "HTTP/1.1 200 200"
2026-04-02 15:57:57,176 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 15:57:57,253 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 15:57:57,292 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=550 "HTTP/1.1 200 200"
2026-04-02 15:57:57,375 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 15:57:57,376 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=575 "HTTP/1.1 200 200"
2026-04-02 15:57:57,446 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=600 "HTTP/1.1 200 200"
2026-04-02 15:57:57,522 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=625 "HTTP/1.1 200 200"
2026-04-02 15:57:57,549 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 15:57:57,550 [INFO] src.adapters.parts_mixin: Found 8 Part subtypes from 200 parts: ['BALAUXPART', 'BALCOLLECTIONPART', 'BALENCDOCPART', 'BALEQUIPMENTPART', 'BALMECHATRONICPART', 'BALPACKAGEPART', 'BALPRODUCTPART', 'BALRAWMATERIAL']
2026-04-02 15:57:57,552 [INFO] api: GET /api/part-subtypes → 200 (1109.4 ms)
INFO:     127.0.0.1:52674 - "GET /api/part-subtypes HTTP/1.1" 200 OK
2026-04-02 15:57:57,663 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=650 "HTTP/1.1 200 200"
2026-04-02 15:57:57,826 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=675 "HTTP/1.1 200 200"
2026-04-02 15:57:57,993 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=700 "HTTP/1.1 200 200"
2026-04-02 15:57:58,115 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=725 "HTTP/1.1 200 200"
2026-04-02 15:57:58,235 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=750 "HTTP/1.1 200 200"
2026-04-02 15:57:58,400 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=775 "HTTP/1.1 200 200"
2026-04-02 15:57:58,527 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=800 "HTTP/1.1 200 200"
2026-04-02 15:57:58,591 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=825 "HTTP/1.1 200 200"
2026-04-02 15:57:58,699 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=850 "HTTP/1.1 200 200"
2026-04-02 15:57:58,859 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=875 "HTTP/1.1 200 200"
2026-04-02 15:57:58,949 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=900 "HTTP/1.1 200 200"
2026-04-02 15:57:59,061 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=925 "HTTP/1.1 200 200"
2026-04-02 15:57:59,186 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=950 "HTTP/1.1 200 200"
2026-04-02 15:57:59,324 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=975 "HTTP/1.1 200 200"
2026-04-02 15:57:59,443 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1000 "HTTP/1.1 200 200"
2026-04-02 15:57:59,550 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1025 "HTTP/1.1 200 200"
2026-04-02 15:57:59,696 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1050 "HTTP/1.1 200 200"
2026-04-02 15:57:59,819 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1075 "HTTP/1.1 200 200"
2026-04-02 15:57:59,820 [INFO] src.services.parts_service: Container-Record Felder: ['@odata.type', 'ID', 'Name']
2026-04-02 15:57:59,821 [INFO] src.services.parts_service: Container[0] komplett: {'@odata.type': '#PTC.DataAdmin.Site', 'ID': 'OR:wt.inf.container.ExchangeContainer:6', 'Name': 'Site'}
2026-04-02 15:57:59,821 [INFO] src.services.parts_service: Container[1] komplett: {'@odata.type': '#PTC.DataAdmin.OrganizationContainer', 'ID': 'OR:wt.inf.container.OrgContainer:93622', 'Name': 'BALLUFF'}
2026-04-02 15:57:59,822 [INFO] src.services.parts_service: Container[2] komplett: {'@odata.type': '#PTC.DataAdmin.LibraryContainer', 'ID': 'OR:wt.inf.library.WTLibrary:133606', 'Name': 'P - Auxiliary Material'}
2026-04-02 15:57:59,828 [INFO] api: GET /api/containers → 200 (5179.1 ms)
INFO:     127.0.0.1:62734 - "GET /api/containers HTTP/1.1" 200 OK
2026-04-02 15:58:00,197 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers/PTC.DataAdmin.PDMLinkProduct "HTTP/1.1 400 400"
2026-04-02 15:58:00,239 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24filter=ContainerType%20eq%20%27Product%27 "HTTP/1.1 400 400"
2026-04-02 15:58:00,240 [INFO] src.adapters.parts_mixin: Container-Filter fehlgeschlagen – lade alle mit $select
2026-04-02 15:58:00,424 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24select=ID%2CName "HTTP/1.1 200 200"
2026-04-02 15:58:00,489 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 15:58:00,555 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 15:58:00,622 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 15:58:00,746 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 15:58:00,836 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 15:58:00,968 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 15:58:01,054 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 15:58:01,127 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=200 "HTTP/1.1 200 200"
2026-04-02 15:58:01,202 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=225 "HTTP/1.1 200 200"
2026-04-02 15:58:01,272 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=250 "HTTP/1.1 200 200"
2026-04-02 15:58:01,375 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=275 "HTTP/1.1 200 200"
2026-04-02 15:58:01,446 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=300 "HTTP/1.1 200 200"
2026-04-02 15:58:01,564 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=325 "HTTP/1.1 200 200"
2026-04-02 15:58:01,645 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=350 "HTTP/1.1 200 200"
2026-04-02 15:58:01,746 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=375 "HTTP/1.1 200 200"
2026-04-02 15:58:01,827 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=400 "HTTP/1.1 200 200"
2026-04-02 15:58:01,933 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=425 "HTTP/1.1 200 200"
2026-04-02 15:58:02,030 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=450 "HTTP/1.1 200 200"
2026-04-02 15:58:02,171 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=475 "HTTP/1.1 200 200"
2026-04-02 15:58:02,238 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=500 "HTTP/1.1 200 200"
2026-04-02 15:58:02,317 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=525 "HTTP/1.1 200 200"
2026-04-02 15:58:02,460 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=550 "HTTP/1.1 200 200"
2026-04-02 15:58:02,607 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=575 "HTTP/1.1 200 200"
2026-04-02 15:58:02,659 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=600 "HTTP/1.1 200 200"
2026-04-02 15:58:02,741 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=625 "HTTP/1.1 200 200"
2026-04-02 15:58:02,816 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=650 "HTTP/1.1 200 200"
2026-04-02 15:58:02,930 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=675 "HTTP/1.1 200 200"
2026-04-02 15:58:03,082 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=700 "HTTP/1.1 200 200"
2026-04-02 15:58:03,239 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=725 "HTTP/1.1 200 200"
2026-04-02 15:58:03,353 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=750 "HTTP/1.1 200 200"
2026-04-02 15:58:03,492 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=775 "HTTP/1.1 200 200"
2026-04-02 15:58:03,697 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=800 "HTTP/1.1 200 200"
2026-04-02 15:58:03,906 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=825 "HTTP/1.1 200 200"
2026-04-02 15:58:04,034 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=850 "HTTP/1.1 200 200"
2026-04-02 15:58:04,143 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=875 "HTTP/1.1 200 200"
2026-04-02 15:58:04,273 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=900 "HTTP/1.1 200 200"
2026-04-02 15:58:04,421 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=925 "HTTP/1.1 200 200"
2026-04-02 15:58:04,564 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=950 "HTTP/1.1 200 200"
2026-04-02 15:58:04,689 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=975 "HTTP/1.1 200 200"
2026-04-02 15:58:04,800 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1000 "HTTP/1.1 200 200"
2026-04-02 15:58:04,939 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1025 "HTTP/1.1 200 200"
2026-04-02 15:58:05,127 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1050 "HTTP/1.1 200 200"
2026-04-02 15:58:05,255 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1075 "HTTP/1.1 200 200"
2026-04-02 15:58:05,256 [INFO] src.services.parts_service: Container-Record Felder: ['@odata.type', 'ID', 'Name']
2026-04-02 15:58:05,256 [INFO] src.services.parts_service: Container[0] komplett: {'@odata.type': '#PTC.DataAdmin.Site', 'ID': 'OR:wt.inf.container.ExchangeContainer:6', 'Name': 'Site'}
2026-04-02 15:58:05,257 [INFO] src.services.parts_service: Container[1] komplett: {'@odata.type': '#PTC.DataAdmin.OrganizationContainer', 'ID': 'OR:wt.inf.container.OrgContainer:93622', 'Name': 'BALLUFF'}
2026-04-02 15:58:05,258 [INFO] src.services.parts_service: Container[2] komplett: {'@odata.type': '#PTC.DataAdmin.LibraryContainer', 'ID': 'OR:wt.inf.library.WTLibrary:133606', 'Name': 'P - Auxiliary Material'}
2026-04-02 15:58:05,267 [INFO] api: GET /api/containers → 200 (5124.3 ms)
INFO:     127.0.0.1:61075 - "GET /api/containers HTTP/1.1" 200 OK

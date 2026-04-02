INFO:     Will watch for changes in these directories: ['C:\\Users\\keilt\\azure_api_agent\\windchill-api']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [17428] using WatchFiles
INFO:     Started server process [27040]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2026-04-02 16:22:31,698 [INFO] api: GET /api/auth/me → 401 (1.1 ms)
INFO:     127.0.0.1:63926 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-02 16:22:31,703 [INFO] api: GET /api/auth/me → 401 (0.6 ms)
INFO:     127.0.0.1:63928 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-02 16:22:31,720 [INFO] api: GET /api/auth/systems → 200 (0.5 ms)
INFO:     127.0.0.1:63930 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-02 16:22:31,724 [INFO] api: GET /api/auth/systems → 200 (0.6 ms)
INFO:     127.0.0.1:63932 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-02 16:22:41,173 [INFO] src.routers.auth: Login-Versuch: system=dev url=https://plm-dev.neuhausen.balluff.net/Windchill user=keilt
2026-04-02 16:22:41,176 [INFO] src.adapters.base: Connecting to https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6
2026-04-02 16:22:42,141 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt "HTTP/1.1 307 307"
2026-04-02 16:22:42,207 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ "HTTP/1.1 200 200"
2026-04-02 16:22:42,208 [INFO] src.adapters.base: Auth-Probe: status=200 url=https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ content-type=application/json;odata.metadata=minimal www-authenticate=
2026-04-02 16:22:42,209 [INFO] src.adapters.base: Basic Auth akzeptiert (status=200)
2026-04-02 16:22:42,244 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/PTC/GetCSRFToken() "HTTP/1.1 200 200"
2026-04-02 16:22:42,245 [INFO] src.adapters.base: CSRF-Token erhalten: CSRF_NONCE=D6tNGCf69Jca…
2026-04-02 16:22:42,247 [INFO] api: POST /api/auth/login → 200 (1076.4 ms)
INFO:     127.0.0.1:53657 - "POST /api/auth/login HTTP/1.1" 200 OK
2026-04-02 16:23:27,117 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers/PTC.DataAdmin.PDMLinkProduct "HTTP/1.1 400 400"
2026-04-02 16:23:27,260 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24filter=ContainerType%20eq%20%27Product%27 "HTTP/1.1 400 400"
2026-04-02 16:23:27,261 [INFO] src.adapters.parts_mixin: Container-Filter fehlgeschlagen – lade alle mit $select
2026-04-02 16:23:27,499 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24select=Number&%24top=200 "HTTP/1.1 200 200"
2026-04-02 16:23:27,908 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24select=ID%2CName "HTTP/1.1 200 200"
2026-04-02 16:23:27,971 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 16:23:28,059 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 16:23:28,092 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 16:23:28,150 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 16:23:28,215 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 16:23:28,229 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 16:23:28,308 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 16:23:28,340 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 16:23:28,398 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 16:23:28,474 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 16:23:28,520 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 16:23:28,569 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=200 "HTTP/1.1 200 200"
2026-04-02 16:23:28,618 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 16:23:28,745 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=225 "HTTP/1.1 200 200"
2026-04-02 16:23:28,815 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 16:23:28,987 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 16:23:28,989 [INFO] src.adapters.parts_mixin: Found 8 Part subtypes from 200 parts: ['BALAUXPART', 'BALCOLLECTIONPART', 'BALENCDOCPART', 'BALEQUIPMENTPART', 'BALMECHATRONICPART', 'BALPACKAGEPART', 'BALPRODUCTPART', 'BALRAWMATERIAL']
2026-04-02 16:23:28,991 [INFO] api: GET /api/part-subtypes → 200 (1739.9 ms)
INFO:     127.0.0.1:63938 - "GET /api/part-subtypes HTTP/1.1" 200 OK
2026-04-02 16:23:29,094 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=250 "HTTP/1.1 200 200"
2026-04-02 16:23:29,170 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=275 "HTTP/1.1 200 200"
2026-04-02 16:23:29,226 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=50 "HTTP/1.1 200 200"
2026-04-02 16:23:29,233 [INFO] src.adapters.parts_mixin: Found 3 distinct classifications from 25 parts: ['BAL_CL_ADDITIVE', 'BAL_CL_NATURAL_MATERIALS', 'WTPartComponentTBD']
2026-04-02 16:23:29,233 [INFO] src.services.parts_service: Classification raw items: 3
2026-04-02 16:23:29,234 [INFO] src.services.parts_service: Classification nodes: 3
2026-04-02 16:23:29,235 [INFO] api: GET /api/classification-nodes → 200 (1982.5 ms)
INFO:     127.0.0.1:63939 - "GET /api/classification-nodes HTTP/1.1" 200 OK
2026-04-02 16:23:29,298 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=300 "HTTP/1.1 200 200"
2026-04-02 16:23:29,403 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=325 "HTTP/1.1 200 200"
2026-04-02 16:23:29,418 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24select=Number&%24top=200 "HTTP/1.1 200 200"
2026-04-02 16:23:29,480 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=350 "HTTP/1.1 200 200"
2026-04-02 16:23:29,557 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=375 "HTTP/1.1 200 200"
2026-04-02 16:23:29,569 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 16:23:29,623 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=400 "HTTP/1.1 200 200"
2026-04-02 16:23:29,702 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=425 "HTTP/1.1 200 200"
2026-04-02 16:23:29,746 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 16:23:29,808 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=450 "HTTP/1.1 200 200"
2026-04-02 16:23:29,885 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=475 "HTTP/1.1 200 200"
2026-04-02 16:23:29,963 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=500 "HTTP/1.1 200 200"
2026-04-02 16:23:30,045 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=525 "HTTP/1.1 200 200"
2026-04-02 16:23:30,077 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 16:23:30,135 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=550 "HTTP/1.1 200 200"
2026-04-02 16:23:30,402 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 16:23:30,494 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 16:23:30,508 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=575 "HTTP/1.1 200 200"
2026-04-02 16:23:30,623 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=600 "HTTP/1.1 200 200"
2026-04-02 16:23:30,738 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=625 "HTTP/1.1 200 200"
2026-04-02 16:23:30,886 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=650 "HTTP/1.1 200 200"
2026-04-02 16:23:30,959 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 16:23:31,021 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=675 "HTTP/1.1 200 200"
2026-04-02 16:23:31,129 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=700 "HTTP/1.1 200 200"
2026-04-02 16:23:31,130 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 16:23:31,133 [INFO] src.adapters.parts_mixin: Found 8 Part subtypes from 200 parts: ['BALAUXPART', 'BALCOLLECTIONPART', 'BALENCDOCPART', 'BALEQUIPMENTPART', 'BALMECHATRONICPART', 'BALPACKAGEPART', 'BALPRODUCTPART', 'BALRAWMATERIAL']
2026-04-02 16:23:31,135 [INFO] api: GET /api/part-subtypes → 200 (1829.7 ms)
INFO:     127.0.0.1:61184 - "GET /api/part-subtypes HTTP/1.1" 200 OK
2026-04-02 16:23:31,240 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=50 "HTTP/1.1 200 200"
2026-04-02 16:23:31,243 [INFO] src.adapters.parts_mixin: Found 3 distinct classifications from 25 parts: ['BAL_CL_ADDITIVE', 'BAL_CL_NATURAL_MATERIALS', 'WTPartComponentTBD']
2026-04-02 16:23:31,244 [INFO] src.services.parts_service: Classification raw items: 3
2026-04-02 16:23:31,244 [INFO] src.services.parts_service: Classification nodes: 3
2026-04-02 16:23:31,246 [INFO] api: GET /api/classification-nodes → 200 (1694.4 ms)
INFO:     127.0.0.1:62140 - "GET /api/classification-nodes HTTP/1.1" 200 OK
2026-04-02 16:23:31,317 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=725 "HTTP/1.1 200 200"
2026-04-02 16:23:31,449 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=750 "HTTP/1.1 200 200"
2026-04-02 16:23:31,574 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=775 "HTTP/1.1 200 200"
2026-04-02 16:23:31,717 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=800 "HTTP/1.1 200 200"
2026-04-02 16:23:31,822 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=825 "HTTP/1.1 200 200"
2026-04-02 16:23:31,996 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=850 "HTTP/1.1 200 200"
2026-04-02 16:23:32,158 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=875 "HTTP/1.1 200 200"
2026-04-02 16:23:32,310 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=900 "HTTP/1.1 200 200"
2026-04-02 16:23:32,502 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=925 "HTTP/1.1 200 200"
2026-04-02 16:23:32,726 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=950 "HTTP/1.1 200 200"
2026-04-02 16:23:32,895 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=975 "HTTP/1.1 200 200"
2026-04-02 16:23:33,079 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1000 "HTTP/1.1 200 200"
2026-04-02 16:23:33,250 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1025 "HTTP/1.1 200 200"
2026-04-02 16:23:33,372 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1050 "HTTP/1.1 200 200"
2026-04-02 16:23:33,521 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1075 "HTTP/1.1 200 200"
2026-04-02 16:23:33,522 [INFO] src.services.parts_service: Container-Record Felder: ['@odata.type', 'ID', 'Name']
2026-04-02 16:23:33,522 [INFO] src.services.parts_service: Container[0] komplett: {'@odata.type': '#PTC.DataAdmin.Site', 'ID': 'OR:wt.inf.container.ExchangeContainer:6', 'Name': 'Site'}
2026-04-02 16:23:33,523 [INFO] src.services.parts_service: Container[1] komplett: {'@odata.type': '#PTC.DataAdmin.OrganizationContainer', 'ID': 'OR:wt.inf.container.OrgContainer:93622', 'Name': 'BALLUFF'}
2026-04-02 16:23:33,523 [INFO] src.services.parts_service: Container[2] komplett: {'@odata.type': '#PTC.DataAdmin.LibraryContainer', 'ID': 'OR:wt.inf.library.WTLibrary:133606', 'Name': 'P - Auxiliary Material'}
2026-04-02 16:23:33,533 [INFO] api: GET /api/containers → 200 (6598.1 ms)
INFO:     127.0.0.1:52337 - "GET /api/containers HTTP/1.1" 200 OK
2026-04-02 16:23:33,895 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers/PTC.DataAdmin.PDMLinkProduct "HTTP/1.1 400 400"
2026-04-02 16:23:33,955 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24filter=ContainerType%20eq%20%27Product%27 "HTTP/1.1 400 400"
2026-04-02 16:23:33,956 [INFO] src.adapters.parts_mixin: Container-Filter fehlgeschlagen – lade alle mit $select
2026-04-02 16:23:34,045 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24select=ID%2CName "HTTP/1.1 200 200"
2026-04-02 16:23:34,160 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 16:23:34,274 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 16:23:34,363 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 16:23:34,426 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 16:23:34,495 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 16:23:34,591 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 16:23:34,731 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 16:23:34,835 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=200 "HTTP/1.1 200 200"
2026-04-02 16:23:34,920 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=225 "HTTP/1.1 200 200"
2026-04-02 16:23:35,039 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=250 "HTTP/1.1 200 200"
2026-04-02 16:23:35,161 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=275 "HTTP/1.1 200 200"
2026-04-02 16:23:35,300 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=300 "HTTP/1.1 200 200"
2026-04-02 16:23:35,402 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=325 "HTTP/1.1 200 200"
2026-04-02 16:23:35,550 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=350 "HTTP/1.1 200 200"
2026-04-02 16:23:35,684 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=375 "HTTP/1.1 200 200"
2026-04-02 16:23:35,840 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=400 "HTTP/1.1 200 200"
2026-04-02 16:23:35,931 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=425 "HTTP/1.1 200 200"
2026-04-02 16:23:36,066 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=450 "HTTP/1.1 200 200"
2026-04-02 16:23:36,161 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=475 "HTTP/1.1 200 200"
2026-04-02 16:23:36,222 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=500 "HTTP/1.1 200 200"
2026-04-02 16:23:36,326 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=525 "HTTP/1.1 200 200"
2026-04-02 16:23:36,387 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=550 "HTTP/1.1 200 200"
2026-04-02 16:23:36,513 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=575 "HTTP/1.1 200 200"
2026-04-02 16:23:36,663 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=600 "HTTP/1.1 200 200"
2026-04-02 16:23:36,854 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=625 "HTTP/1.1 200 200"
2026-04-02 16:23:36,977 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=650 "HTTP/1.1 200 200"
2026-04-02 16:23:37,121 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=675 "HTTP/1.1 200 200"
2026-04-02 16:23:37,292 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=700 "HTTP/1.1 200 200"
2026-04-02 16:23:37,430 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=725 "HTTP/1.1 200 200"
2026-04-02 16:23:37,602 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=750 "HTTP/1.1 200 200"
2026-04-02 16:23:37,711 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=775 "HTTP/1.1 200 200"
2026-04-02 16:23:37,869 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=800 "HTTP/1.1 200 200"
2026-04-02 16:23:37,996 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=825 "HTTP/1.1 200 200"
2026-04-02 16:23:38,146 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=850 "HTTP/1.1 200 200"
2026-04-02 16:23:38,238 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=875 "HTTP/1.1 200 200"
2026-04-02 16:23:38,355 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=900 "HTTP/1.1 200 200"
2026-04-02 16:23:38,470 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=925 "HTTP/1.1 200 200"
2026-04-02 16:23:38,647 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=950 "HTTP/1.1 200 200"
2026-04-02 16:23:38,742 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=975 "HTTP/1.1 200 200"
2026-04-02 16:23:38,805 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1000 "HTTP/1.1 200 200"
2026-04-02 16:23:38,959 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1025 "HTTP/1.1 200 200"
2026-04-02 16:23:39,076 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1050 "HTTP/1.1 200 200"
2026-04-02 16:23:39,206 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1075 "HTTP/1.1 200 200"
2026-04-02 16:23:39,207 [INFO] src.services.parts_service: Container-Record Felder: ['@odata.type', 'ID', 'Name']
2026-04-02 16:23:39,208 [INFO] src.services.parts_service: Container[0] komplett: {'@odata.type': '#PTC.DataAdmin.Site', 'ID': 'OR:wt.inf.container.ExchangeContainer:6', 'Name': 'Site'}
2026-04-02 16:23:39,208 [INFO] src.services.parts_service: Container[1] komplett: {'@odata.type': '#PTC.DataAdmin.OrganizationContainer', 'ID': 'OR:wt.inf.container.OrgContainer:93622', 'Name': 'BALLUFF'}
2026-04-02 16:23:39,209 [INFO] src.services.parts_service: Container[2] komplett: {'@odata.type': '#PTC.DataAdmin.LibraryContainer', 'ID': 'OR:wt.inf.library.WTLibrary:133606', 'Name': 'P - Auxiliary Material'}
2026-04-02 16:23:39,216 [INFO] api: GET /api/containers → 200 (5366.8 ms)
INFO:     127.0.0.1:53622 - "GET /api/containers HTTP/1.1" 200 OK
2026-04-02 16:24:49,287 [INFO] src.services.write_service: Create Part body: {'@odata.type': '#PTC.ProdMgmt.BALAUXPART', 'Name': 'abc2', 'Source': {'Value': 'notapplicable'}, 'DefaultUnit': {'Value': 'ea'}, 'AssemblyMode': {'Value': 'separable'}, 'GatheringPart': False, 'PhantomManufacturingPart': False, 'DefaultTraceCode': {'Value': '0'}, 'Context@odata.bind': "Containers('OR:wt.pdmlink.PDMLinkProduct:131530')", 'BALCLASSIFICATIONBINDINGWTPART': {'ClfNodeInternalName': 'WTPartComponentTBD'}}
2026-04-02 16:24:49,288 [INFO] src.services.write_service: Post-create PATCH body: {'View': 'Design', 'BALCPORDERPREFIX': 'PIU'}
2026-04-02 16:24:49,418 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/PTC/GetCSRFToken() "HTTP/1.1 200 200"
2026-04-02 16:24:49,419 [INFO] src.adapters.base: CSRF-Token erhalten: CSRF_NONCE=79QhtlyINDbD…
2026-04-02 16:24:49,420 [INFO] src.adapters.write_mixin: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts — Headers: {'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'python-httpx/0.27.2', 'accept': 'application/json', 'x-requested-with': 'XMLHttpRequest', 'csrf_nonce': '79QhtlyINDbDDa8htZVx…'}
2026-04-02 16:24:49,430 [INFO] src.adapters.write_mixin: POST body keys: ['@odata.type', 'Name', 'Source', 'DefaultUnit', 'AssemblyMode', 'GatheringPart', 'PhantomManufacturingPart', 'DefaultTraceCode', 'Context@odata.bind', 'BALCLASSIFICATIONBINDINGWTPART']
2026-04-02 16:24:49,583 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts "HTTP/1.1 400 400"
2026-04-02 16:24:49,585 [WARNING] src.adapters.write_mixin: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts → 400 — Full response: {"error":{"code":null,"message":"The value for attribute Classification violates the constraints defined for this attribute."}}
2026-04-02 16:24:49,586 [INFO] api: POST /api/write/create → 400 (304.3 ms)
INFO:     127.0.0.1:53797 - "POST /api/write/create HTTP/1.1" 400 Bad Request
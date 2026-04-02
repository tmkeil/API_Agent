INFO:     Will watch for changes in these directories: ['C:\\Users\\keilt\\azure_api_agent\\windchill-api']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [15952] using WatchFiles
INFO:     Started server process [26988]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2026-04-02 16:04:43,076 [INFO] watchfiles.main: 1 change detected
2026-04-02 16:04:44,340 [INFO] watchfiles.main: 11 changes detected
2026-04-02 16:04:47,963 [INFO] api: GET /api/auth/me → 401 (1.2 ms)
INFO:     127.0.0.1:63005 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-02 16:04:47,968 [INFO] api: GET /api/auth/me → 401 (0.7 ms)
INFO:     127.0.0.1:63007 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-02 16:04:47,985 [INFO] api: GET /api/auth/systems → 200 (0.7 ms)
INFO:     127.0.0.1:63009 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-02 16:04:47,990 [INFO] api: GET /api/auth/systems → 200 (0.5 ms)
INFO:     127.0.0.1:63011 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-02 16:04:48,844 [INFO] src.routers.auth: Login-Versuch: system=dev url=https://plm-dev.neuhausen.balluff.net/Windchill user=keilt
2026-04-02 16:04:48,846 [INFO] src.adapters.base: Connecting to https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6
2026-04-02 16:04:49,786 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt "HTTP/1.1 307 307"
2026-04-02 16:04:49,831 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ "HTTP/1.1 200 200"
2026-04-02 16:04:49,832 [INFO] src.adapters.base: Auth-Probe: status=200 url=https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ content-type=application/json;odata.metadata=minimal www-authenticate=
2026-04-02 16:04:49,833 [INFO] src.adapters.base: Basic Auth akzeptiert (status=200)
2026-04-02 16:04:49,879 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/PTC/GetCSRFToken() "HTTP/1.1 200 200"
2026-04-02 16:04:49,880 [INFO] src.adapters.base: CSRF-Token erhalten: CSRF_NONCE=/pK2++vKVk6n…
2026-04-02 16:04:49,881 [INFO] api: POST /api/auth/login → 200 (1039.6 ms)
INFO:     127.0.0.1:52968 - "POST /api/auth/login HTTP/1.1" 200 OK
2026-04-02 16:04:51,235 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers/PTC.DataAdmin.PDMLinkProduct "HTTP/1.1 400 400"
2026-04-02 16:04:51,349 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24filter=ContainerType%20eq%20%27Product%27 "HTTP/1.1 400 400"
2026-04-02 16:04:51,350 [INFO] src.adapters.parts_mixin: Container-Filter fehlgeschlagen – lade alle mit $select
2026-04-02 16:04:51,509 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24select=ID%2CName "HTTP/1.1 200 200"
2026-04-02 16:04:51,580 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 16:04:51,648 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24select=Number&%24top=200 "HTTP/1.1 200 200"
2026-04-02 16:04:51,681 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 16:04:51,772 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 16:04:51,848 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 16:04:51,904 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 16:04:52,006 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 16:04:52,029 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 16:04:52,110 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 16:04:52,195 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 16:04:52,201 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=200 "HTTP/1.1 200 200"
2026-04-02 16:04:52,434 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=225 "HTTP/1.1 200 200"
2026-04-02 16:04:52,477 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 16:04:52,555 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=250 "HTTP/1.1 200 200"
2026-04-02 16:04:52,654 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=275 "HTTP/1.1 200 200"
2026-04-02 16:04:52,745 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=300 "HTTP/1.1 200 200"
2026-04-02 16:04:52,792 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 16:04:52,868 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=325 "HTTP/1.1 200 200"
2026-04-02 16:04:52,905 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 16:04:52,977 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=350 "HTTP/1.1 200 200"
2026-04-02 16:04:53,100 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=375 "HTTP/1.1 200 200"
2026-04-02 16:04:53,176 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=400 "HTTP/1.1 200 200"
2026-04-02 16:04:53,179 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 16:04:53,251 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=425 "HTTP/1.1 200 200"
2026-04-02 16:04:53,341 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 16:04:53,342 [INFO] src.adapters.parts_mixin: Found 8 Part subtypes from 200 parts: ['BALAUXPART', 'BALCOLLECTIONPART', 'BALENCDOCPART', 'BALEQUIPMENTPART', 'BALMECHATRONICPART', 'BALPACKAGEPART', 'BALPRODUCTPART', 'BALRAWMATERIAL']
2026-04-02 16:04:53,344 [INFO] api: GET /api/part-subtypes → 200 (1881.2 ms)
INFO:     127.0.0.1:59113 - "GET /api/part-subtypes HTTP/1.1" 200 OK
2026-04-02 16:04:53,363 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=450 "HTTP/1.1 200 200"
2026-04-02 16:04:53,498 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=475 "HTTP/1.1 200 200"
2026-04-02 16:04:53,655 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=500 "HTTP/1.1 200 200"
2026-04-02 16:04:53,784 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=525 "HTTP/1.1 200 200"
2026-04-02 16:04:53,816 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24select=Number&%24top=200 "HTTP/1.1 200 200"
2026-04-02 16:04:53,857 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=550 "HTTP/1.1 200 200"
2026-04-02 16:04:53,954 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=575 "HTTP/1.1 200 200"
2026-04-02 16:04:54,129 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=600 "HTTP/1.1 200 200"
2026-04-02 16:04:54,155 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 16:04:54,268 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=625 "HTTP/1.1 200 200"
2026-04-02 16:04:54,285 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 16:04:54,365 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=650 "HTTP/1.1 200 200"
2026-04-02 16:04:54,411 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 16:04:54,451 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=675 "HTTP/1.1 200 200"
2026-04-02 16:04:54,550 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=700 "HTTP/1.1 200 200"
2026-04-02 16:04:54,707 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=725 "HTTP/1.1 200 200"
2026-04-02 16:04:54,777 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 16:04:54,806 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=750 "HTTP/1.1 200 200"
2026-04-02 16:04:54,904 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=775 "HTTP/1.1 200 200"
2026-04-02 16:04:54,936 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 16:04:55,058 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=800 "HTTP/1.1 200 200"
2026-04-02 16:04:55,144 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=825 "HTTP/1.1 200 200"
2026-04-02 16:04:55,171 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 16:04:55,333 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=850 "HTTP/1.1 200 200"
2026-04-02 16:04:55,338 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$select=Number&$top=200&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 16:04:55,340 [INFO] src.adapters.parts_mixin: Found 8 Part subtypes from 200 parts: ['BALAUXPART', 'BALCOLLECTIONPART', 'BALENCDOCPART', 'BALEQUIPMENTPART', 'BALMECHATRONICPART', 'BALPACKAGEPART', 'BALPRODUCTPART', 'BALRAWMATERIAL']
2026-04-02 16:04:55,342 [INFO] api: GET /api/part-subtypes → 200 (1683.2 ms)
INFO:     127.0.0.1:58089 - "GET /api/part-subtypes HTTP/1.1" 200 OK
2026-04-02 16:04:55,508 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=875 "HTTP/1.1 200 200"
2026-04-02 16:04:55,626 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=900 "HTTP/1.1 200 200"
2026-04-02 16:04:55,799 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=925 "HTTP/1.1 200 200"
2026-04-02 16:04:55,870 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=950 "HTTP/1.1 200 200"
2026-04-02 16:04:56,047 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=975 "HTTP/1.1 200 200"
2026-04-02 16:04:56,237 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1000 "HTTP/1.1 200 200"
2026-04-02 16:04:56,465 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1025 "HTTP/1.1 200 200"
2026-04-02 16:04:56,671 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1050 "HTTP/1.1 200 200"
2026-04-02 16:04:56,852 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1075 "HTTP/1.1 200 200"
2026-04-02 16:04:56,853 [INFO] src.services.parts_service: Container-Record Felder: ['@odata.type', 'ID', 'Name']
2026-04-02 16:04:56,853 [INFO] src.services.parts_service: Container[0] komplett: {'@odata.type': '#PTC.DataAdmin.Site', 'ID': 'OR:wt.inf.container.ExchangeContainer:6', 'Name': 'Site'}
2026-04-02 16:04:56,853 [INFO] src.services.parts_service: Container[1] komplett: {'@odata.type': '#PTC.DataAdmin.OrganizationContainer', 'ID': 'OR:wt.inf.container.OrgContainer:93622', 'Name': 'BALLUFF'}
2026-04-02 16:04:56,854 [INFO] src.services.parts_service: Container[2] komplett: {'@odata.type': '#PTC.DataAdmin.LibraryContainer', 'ID': 'OR:wt.inf.library.WTLibrary:133606', 'Name': 'P - Auxiliary Material'}
2026-04-02 16:04:56,864 [INFO] api: GET /api/containers → 200 (5706.4 ms)
INFO:     127.0.0.1:52209 - "GET /api/containers HTTP/1.1" 200 OK
2026-04-02 16:04:57,232 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers/PTC.DataAdmin.PDMLinkProduct "HTTP/1.1 400 400"
2026-04-02 16:04:57,275 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24filter=ContainerType%20eq%20%27Product%27 "HTTP/1.1 400 400"
2026-04-02 16:04:57,276 [INFO] src.adapters.parts_mixin: Container-Filter fehlgeschlagen – lade alle mit $select
2026-04-02 16:04:57,425 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?%24select=ID%2CName "HTTP/1.1 200 200"
2026-04-02 16:04:57,495 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 16:04:57,591 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 16:04:57,688 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 16:04:57,759 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 16:04:57,851 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 16:04:57,977 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 16:04:58,060 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 16:04:58,180 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=200 "HTTP/1.1 200 200"
2026-04-02 16:04:58,287 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=225 "HTTP/1.1 200 200"
2026-04-02 16:04:58,371 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=250 "HTTP/1.1 200 200"
2026-04-02 16:04:58,513 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=275 "HTTP/1.1 200 200"
2026-04-02 16:04:58,626 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=300 "HTTP/1.1 200 200"
2026-04-02 16:04:58,727 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=325 "HTTP/1.1 200 200"
2026-04-02 16:04:58,849 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=350 "HTTP/1.1 200 200"
2026-04-02 16:04:58,898 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=200 "HTTP/1.1 200 200"
2026-04-02 16:04:58,984 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=375 "HTTP/1.1 200 200"
2026-04-02 16:04:59,106 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=400 "HTTP/1.1 200 200"
2026-04-02 16:04:59,221 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=425 "HTTP/1.1 200 200"
2026-04-02 16:04:59,347 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=450 "HTTP/1.1 200 200"
2026-04-02 16:04:59,434 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=475 "HTTP/1.1 200 200"
2026-04-02 16:04:59,553 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=500 "HTTP/1.1 200 200"
2026-04-02 16:04:59,725 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=525 "HTTP/1.1 200 200"
2026-04-02 16:04:59,818 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=550 "HTTP/1.1 200 200"
2026-04-02 16:04:59,978 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=575 "HTTP/1.1 200 200"
2026-04-02 16:05:00,051 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=600 "HTTP/1.1 200 200"
2026-04-02 16:05:00,129 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=625 "HTTP/1.1 200 200"
2026-04-02 16:05:00,270 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=650 "HTTP/1.1 200 200"
2026-04-02 16:05:00,344 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=675 "HTTP/1.1 200 200"
2026-04-02 16:05:00,416 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=700 "HTTP/1.1 200 200"
2026-04-02 16:05:00,514 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=725 "HTTP/1.1 200 200"
2026-04-02 16:05:00,668 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=750 "HTTP/1.1 200 200"
2026-04-02 16:05:00,772 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=775 "HTTP/1.1 200 200"
2026-04-02 16:05:00,902 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=800 "HTTP/1.1 200 200"
2026-04-02 16:05:01,013 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=825 "HTTP/1.1 200 200"
2026-04-02 16:05:01,099 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=850 "HTTP/1.1 200 200"
2026-04-02 16:05:01,190 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=875 "HTTP/1.1 200 200"
2026-04-02 16:05:01,297 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=900 "HTTP/1.1 200 200"
2026-04-02 16:05:01,362 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 16:05:01,387 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=925 "HTTP/1.1 200 200"
2026-04-02 16:05:01,459 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=950 "HTTP/1.1 200 200"
2026-04-02 16:05:01,568 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=975 "HTTP/1.1 200 200"
2026-04-02 16:05:01,646 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1000 "HTTP/1.1 200 200"
2026-04-02 16:05:01,741 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1025 "HTTP/1.1 200 200"
2026-04-02 16:05:01,824 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1050 "HTTP/1.1 200 200"
2026-04-02 16:05:01,885 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DataAdmin/Containers?$select=ID,Name&$skiptoken=1075 "HTTP/1.1 200 200"
2026-04-02 16:05:01,886 [INFO] src.services.parts_service: Container-Record Felder: ['@odata.type', 'ID', 'Name']
2026-04-02 16:05:01,886 [INFO] src.services.parts_service: Container[0] komplett: {'@odata.type': '#PTC.DataAdmin.Site', 'ID': 'OR:wt.inf.container.ExchangeContainer:6', 'Name': 'Site'}
2026-04-02 16:05:01,886 [INFO] src.services.parts_service: Container[1] komplett: {'@odata.type': '#PTC.DataAdmin.OrganizationContainer', 'ID': 'OR:wt.inf.container.OrgContainer:93622', 'Name': 'BALLUFF'}
2026-04-02 16:05:01,887 [INFO] src.services.parts_service: Container[2] komplett: {'@odata.type': '#PTC.DataAdmin.LibraryContainer', 'ID': 'OR:wt.inf.library.WTLibrary:133606', 'Name': 'P - Auxiliary Material'}
2026-04-02 16:05:01,892 [INFO] api: GET /api/containers → 200 (4711.5 ms)
INFO:     127.0.0.1:56196 - "GET /api/containers HTTP/1.1" 200 OK
2026-04-02 16:05:03,537 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 16:05:05,916 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 16:05:07,745 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 16:05:10,520 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 16:05:12,321 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 16:05:13,100 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=200 "HTTP/1.1 200 200"
2026-04-02 16:05:14,228 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 16:05:14,243 [INFO] src.adapters.parts_mixin: Part sample keys (non-odata): ['CreatedOn', 'ID', 'LastModified', 'AlternateNumber', 'AssemblyMode', 'BALAPPROVEDPLANTS', 'BALBINDING', 'BALCONFIDENTIALITY', 'BALCPORDERPREFIX', 'BALCREATEDBY', 'BALDESCRIPTION1', 'BALDMSCR3AEHEDGFLAG', 'BALDMSCRCCCFLAG', 'BALDMSCRCUSTFLAG', 'BALDMSCRDISPLAY', 'BALDMSCRECOLABFLAG', 'BALDMSCREXPLFLAG', 'BALDMSCRFCMFLAG', 'BALDMSCRRADIOFLAG', 'BALDMSCRSAFETYFLAG', 'BALDMSCRTRACEFLAG', 'BALDMSCRULFLAG', 'BALDMSCRZULANFFLAG', 'BALDOWNSTREAM', 'BALMATURITYLEVEL', 'BALMODIFIEDBY', 'BALOLDDATAMODEL', 'BALPREDECESSORID', 'BALPROJECTNUMBERALIAS', 'BALREUSEPREDECESSORDATA', 'BALSAPASSIGNEDPLANTS', 'BALSAPMARAZZROLLUSEUAS', 'BALSAPMATERIALTYPE', 'BALSAPMMSTA', 'BALSAPMSTAE', 'BALSAPNAME', 'BALSAPORDERCODE', 'BALSAPSTATUS', 'BALSUFFIX', 'BALTAGGINGPHRASE', 'BALUPSTREAM', 'BOMType', 'CabinetName', 'ChangeStatus', 'CheckOutStatus', 'CheckoutState', 'Comments', 'ConfigurableModule', 'CreatedBy', 'DefaultTraceCode', 'DefaultUnit', 'ECNAPPROVER', 'ECNAPPROVERDATE', 'EndItem', 'FolderLocation', 'FolderName', 'GatheringPart', 'GeneralStatus', 'Identity', 'Latest', 'LifeCycleTemplateName', 'ModifiedBy', 'Name', 'Number', 'OEMPartSourcingStatus', 'ObjectType', 'OrganizationName', 'PhantomManufacturingPart', 'Revision', 'ShareStatus', 'Source', 'State', 'Supersedes', 'TypeIcon', 'Version', 'VersionID', 'View', 'WorkInProgressState', 'BALADDITIV1', 'BALADDITIV1PERCENTAGE', 'BALADDITIV2', 'BALADDITIV2PERCENTAGE', 'BALADDITIV3', 'BALADDITIV3PERCENTAGE', 'BALALTIUMCATEGORY', 'BALALTIUMCLEANUP', 'BALAUTOMATICEXCHANGE', 'BALBYAPPROVALLIMITEDCHARACTERISTICS', 'BALCLASSIFICATIONBINDINGWTPART', 'BALCUSTOMERPROVIDEDPART', 'BALCUSTOMERSPECIFIC', 'BALDEFINEDSTORECONDITION', 'BALERPmigrationdate', 'BALGxP', 'BALHAZARDOUSMATERIAL', 'BALHELPLINK', 'BALINSTRUCTIONS', 'BALISVARIANT', 'BALLegacyERPname', 'BALLegacyERPnumber', 'BALLegacyERPsource', 'BALLegacyERPstate', 'BALLegacyERPversion', 'BALMADEFROMNUMBER', 'BALMATERIAL', 'BALNOTSUITABLENEWDESIGN', 'BALOBJECTDIMENSION1', 'BALOBJECTDIMENSION2', 'BALOBJECTDIMENSION3', 'BALOBJECTDIMENSION4', 'BALSAPALLOCATEDPLANT', 'BALSAPMATCOMPLIANCESTATUS', 'BALSAPMSTAV', 'BALSAPSTPOROAME', 'BALSAPSTPOROANZ', 'BALSAPSTPOROKME', 'BALSAPSTPOROMEI', 'BALSAPSTPOROMEN', 'BALSAPSTPOROMS1', 'BALSAPSTPOROMS2', 'BALSAPSTPOROMS3', 'BALSPECIALOPERATIONALCONDITIONS', 'BALSPECIALOPERATIONALCONDITIONSTEXT', 'BALSTORAGECONDITIONTEXT', 'BALSURFACECOLOUR', 'BALSURFACEFINISH', 'BALSURFACEHARDNESS', 'BALSURFACEOTHER', 'BALSURFACETHICKNESS', 'BALUPSTREAMSOURCE', 'BALVARIANTDERIVEDFROMNUMBER', 'BALVERSION', 'BALWEIGHTBRUTTO', 'BALWEIGHTMODELED', 'BALWEIGHTNETTO']
2026-04-02 16:05:14,244 [INFO] src.adapters.parts_mixin: Part keys containing 'class/clf': ['BALCLASSIFICATIONBINDINGWTPART']
2026-04-02 16:05:14,244 [INFO] src.adapters.parts_mixin: Part[0] BALCLASSIFICATIONBINDINGWTPART = {'ClfNodeInternalName': 'WTPartComponentTBD', 'ClfNodeDisplayName': 'TBD', 'ClfNodeHierarchyDisplayName': 'Balluff > WTPart > Component > TBD', 'ClassificationAttributes': [{'InternalName': 'BAL_CLASS_REQ_COMMENT', 'DisplayName': 'Comment', 'Value': None, 'DisplayValue': None}, {'InternalName': 'BAL_CLASS_REQ_PRELIM_CAT', 'DisplayName': 'Preliminary Category', 'Value': None, 'DisplayValue': None}]} (type: dict)
2026-04-02 16:05:14,245 [INFO] src.adapters.parts_mixin: Found 10 distinct classifications from 200 parts: ['BAL_CL_ADDITIVE', 'BAL_CL_ELECTROMAGNETIC_INTERFACES', 'BAL_CL_HOUSING_ROUND', 'BAL_CL_NATURAL_MATERIALS', 'BAL_CL_STENCIL', 'WTPartAuxiliaryTBD', 'WTPartComponentTBD', 'WTPartEncDocTBD', 'WTPartEquipmentTBD', 'WTPartPackingTBD']
2026-04-02 16:05:14,247 [INFO] src.services.parts_service: Classification raw items: 10
2026-04-02 16:05:14,247 [INFO] src.services.parts_service: Classification nodes: 10
2026-04-02 16:05:14,249 [INFO] api: GET /api/classification-nodes → 200 (22787.0 ms)
INFO:     127.0.0.1:59114 - "GET /api/classification-nodes HTTP/1.1" 200 OK
2026-04-02 16:05:14,653 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=25 "HTTP/1.1 200 200"
2026-04-02 16:05:16,446 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=50 "HTTP/1.1 200 200"
2026-04-02 16:05:17,867 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=75 "HTTP/1.1 200 200"
2026-04-02 16:05:19,260 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=100 "HTTP/1.1 200 200"
2026-04-02 16:05:20,740 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=125 "HTTP/1.1 200 200"
2026-04-02 16:05:22,156 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=150 "HTTP/1.1 200 200"
2026-04-02 16:05:23,290 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?$top=200&$skiptoken=175 "HTTP/1.1 200 200"
2026-04-02 16:05:23,293 [INFO] src.adapters.parts_mixin: Part sample keys (non-odata): ['CreatedOn', 'ID', 'LastModified', 'AlternateNumber', 'AssemblyMode', 'BALAPPROVEDPLANTS', 'BALBINDING', 'BALCONFIDENTIALITY', 'BALCPORDERPREFIX', 'BALCREATEDBY', 'BALDESCRIPTION1', 'BALDMSCR3AEHEDGFLAG', 'BALDMSCRCCCFLAG', 'BALDMSCRCUSTFLAG', 'BALDMSCRDISPLAY', 'BALDMSCRECOLABFLAG', 'BALDMSCREXPLFLAG', 'BALDMSCRFCMFLAG', 'BALDMSCRRADIOFLAG', 'BALDMSCRSAFETYFLAG', 'BALDMSCRTRACEFLAG', 'BALDMSCRULFLAG', 'BALDMSCRZULANFFLAG', 'BALDOWNSTREAM', 'BALMATURITYLEVEL', 'BALMODIFIEDBY', 'BALOLDDATAMODEL', 'BALPREDECESSORID', 'BALPROJECTNUMBERALIAS', 'BALREUSEPREDECESSORDATA', 'BALSAPASSIGNEDPLANTS', 'BALSAPMARAZZROLLUSEUAS', 'BALSAPMATERIALTYPE', 'BALSAPMMSTA', 'BALSAPMSTAE', 'BALSAPNAME', 'BALSAPORDERCODE', 'BALSAPSTATUS', 'BALSUFFIX', 'BALTAGGINGPHRASE', 'BALUPSTREAM', 'BOMType', 'CabinetName', 'ChangeStatus', 'CheckOutStatus', 'CheckoutState', 'Comments', 'ConfigurableModule', 'CreatedBy', 'DefaultTraceCode', 'DefaultUnit', 'ECNAPPROVER', 'ECNAPPROVERDATE', 'EndItem', 'FolderLocation', 'FolderName', 'GatheringPart', 'GeneralStatus', 'Identity', 'Latest', 'LifeCycleTemplateName', 'ModifiedBy', 'Name', 'Number', 'OEMPartSourcingStatus', 'ObjectType', 'OrganizationName', 'PhantomManufacturingPart', 'Revision', 'ShareStatus', 'Source', 'State', 'Supersedes', 'TypeIcon', 'Version', 'VersionID', 'View', 'WorkInProgressState', 'BALADDITIV1', 'BALADDITIV1PERCENTAGE', 'BALADDITIV2', 'BALADDITIV2PERCENTAGE', 'BALADDITIV3', 'BALADDITIV3PERCENTAGE', 'BALALTIUMCATEGORY', 'BALALTIUMCLEANUP', 'BALAUTOMATICEXCHANGE', 'BALBYAPPROVALLIMITEDCHARACTERISTICS', 'BALCLASSIFICATIONBINDINGWTPART', 'BALCUSTOMERPROVIDEDPART', 'BALCUSTOMERSPECIFIC', 'BALDEFINEDSTORECONDITION', 'BALERPmigrationdate', 'BALGxP', 'BALHAZARDOUSMATERIAL', 'BALHELPLINK', 'BALINSTRUCTIONS', 'BALISVARIANT', 'BALLegacyERPname', 'BALLegacyERPnumber', 'BALLegacyERPsource', 'BALLegacyERPstate', 'BALLegacyERPversion', 'BALMADEFROMNUMBER', 'BALMATERIAL', 'BALNOTSUITABLENEWDESIGN', 'BALOBJECTDIMENSION1', 'BALOBJECTDIMENSION2', 'BALOBJECTDIMENSION3', 'BALOBJECTDIMENSION4', 'BALSAPALLOCATEDPLANT', 'BALSAPMATCOMPLIANCESTATUS', 'BALSAPMSTAV', 'BALSAPSTPOROAME', 'BALSAPSTPOROANZ', 'BALSAPSTPOROKME', 'BALSAPSTPOROMEI', 'BALSAPSTPOROMEN', 'BALSAPSTPOROMS1', 'BALSAPSTPOROMS2', 'BALSAPSTPOROMS3', 'BALSPECIALOPERATIONALCONDITIONS', 'BALSPECIALOPERATIONALCONDITIONSTEXT', 'BALSTORAGECONDITIONTEXT', 'BALSURFACECOLOUR', 'BALSURFACEFINISH', 'BALSURFACEHARDNESS', 'BALSURFACEOTHER', 'BALSURFACETHICKNESS', 'BALUPSTREAMSOURCE', 'BALVARIANTDERIVEDFROMNUMBER', 'BALVERSION', 'BALWEIGHTBRUTTO', 'BALWEIGHTMODELED', 'BALWEIGHTNETTO']
2026-04-02 16:05:23,294 [INFO] src.adapters.parts_mixin: Part keys containing 'class/clf': ['BALCLASSIFICATIONBINDINGWTPART']
2026-04-02 16:05:23,295 [INFO] src.adapters.parts_mixin: Part[0] BALCLASSIFICATIONBINDINGWTPART = {'ClfNodeInternalName': 'WTPartComponentTBD', 'ClfNodeDisplayName': 'TBD', 'ClfNodeHierarchyDisplayName': 'Balluff > WTPart > Component > TBD', 'ClassificationAttributes': [{'InternalName': 'BAL_CLASS_REQ_COMMENT', 'DisplayName': 'Comment', 'Value': None, 'DisplayValue': None}, {'InternalName': 'BAL_CLASS_REQ_PRELIM_CAT', 'DisplayName': 'Preliminary Category', 'Value': None, 'DisplayValue': None}]} (type: dict)
2026-04-02 16:05:23,295 [INFO] src.adapters.parts_mixin: Found 10 distinct classifications from 200 parts: ['BAL_CL_ADDITIVE', 'BAL_CL_ELECTROMAGNETIC_INTERFACES', 'BAL_CL_HOUSING_ROUND', 'BAL_CL_NATURAL_MATERIALS', 'BAL_CL_STENCIL', 'WTPartAuxiliaryTBD', 'WTPartComponentTBD', 'WTPartEncDocTBD', 'WTPartEquipmentTBD', 'WTPartPackingTBD']
2026-04-02 16:05:23,297 [INFO] src.services.parts_service: Classification raw items: 10
2026-04-02 16:05:23,298 [INFO] src.services.parts_service: Classification nodes: 10
2026-04-02 16:05:23,300 [INFO] api: GET /api/classification-nodes → 200 (11825.8 ms)
INFO:     127.0.0.1:60703 - "GET /api/classification-nodes HTTP/1.1" 200 OK
2026-04-02 16:10:58,187 [INFO] src.services.write_service: Create Part body: {'@odata.type': 'PTC.ProdMgmt.BALAUXPART', 'Name': 'abc2', 'Source': {'Value': 'notapplicable'}, 'DefaultUnit': {'Value': 'ea'}, 'AssemblyMode': {'Value': 'separable'}, 'GatheringPart': False, 'PhantomManufacturingPart': False, 'DefaultTraceCode': {'Value': '0'}, 'Context@odata.bind': "Containers('OR:wt.pdmlink.PDMLinkProduct:131530')", 'BALCLASSIFICATIONBINDINGWTPART': {'ClfNodeInternalName': 'WTPartAuxiliaryTBD'}}
2026-04-02 16:10:58,187 [INFO] src.services.write_service: Post-create PATCH body: {'View': 'Design', 'BALCPORDERPREFIX': 'PIU'}
2026-04-02 16:10:58,377 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/PTC/GetCSRFToken() "HTTP/1.1 200 200"
2026-04-02 16:10:58,378 [INFO] src.adapters.base: CSRF-Token erhalten: CSRF_NONCE=EidwkbiNlHAS…
2026-04-02 16:10:58,952 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts "HTTP/1.1 403 403"
2026-04-02 16:10:58,953 [INFO] api: POST /api/write/create → 403 (768.6 ms)
INFO:     127.0.0.1:58758 - "POST /api/write/create HTTP/1.1" 403 Forbidden
INFO:     Will watch for changes in these directories: ['C:\\Users\\keilt\\azure_api_agent\\windchill-api']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [3860] using WatchFiles
INFO:     Started server process [17160]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2026-04-01 12:29:41,125 [INFO] api: GET /api/auth/me → 401 (1.2 ms)
INFO:     127.0.0.1:62038 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-01 12:29:41,136 [INFO] api: GET /api/auth/me → 401 (1.0 ms)
INFO:     127.0.0.1:62040 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-01 12:29:41,145 [INFO] api: GET /api/auth/systems → 200 (0.5 ms)
INFO:     127.0.0.1:62042 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-01 12:29:41,150 [INFO] api: GET /api/auth/systems → 200 (0.6 ms)
INFO:     127.0.0.1:62044 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-01 12:29:53,388 [INFO] src.routers.auth: Login-Versuch: system=dev url=https://plm-dev.neuhausen.balluff.net/Windchill user=keilt
2026-04-01 12:29:53,392 [INFO] src.adapters.base: Connecting to https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6
2026-04-01 12:29:54,594 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt "HTTP/1.1 307 307"
2026-04-01 12:29:54,670 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ "HTTP/1.1 200 200"
2026-04-01 12:29:54,671 [INFO] src.adapters.base: Auth-Probe: status=200 url=https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ content-type=application/json;odata.metadata=minimal www-authenticate=
2026-04-01 12:29:54,672 [INFO] src.adapters.base: Basic Auth akzeptiert (status=200)
2026-04-01 12:29:54,673 [INFO] src.adapters.base: Cookies nach Auth-Probe: {}
2026-04-01 12:29:54,700 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=0&%24select=ID "HTTP/1.1 401 Unauthorized"
2026-04-01 12:29:54,700 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts): status=401, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:29:54,700 [INFO] src.adapters.base: Kein CSRF_NONCE ueber Cookie-Session — setze permanenten Basic Auth
2026-04-01 12:29:54,702 [INFO] api: POST /api/auth/login → 200 (1314.7 ms)
INFO:     127.0.0.1:60244 - "POST /api/auth/login HTTP/1.1" 200 OK
2026-04-01 12:30:46,677 [INFO] api: GET /api/search/stream → 200 (2.2 ms)
INFO:     127.0.0.1:60712 - "GET /api/search/stream?q=2200510405&mode=auto HTTP/1.1" 200 OK
2026-04-01 12:30:46,854 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeRequests?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:46,863 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ProblemReports?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:46,932 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeNotices?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:47,053 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:47,533 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:51,705 [INFO] api: GET /api/search/stream → 200 (4.7 ms)
INFO:     127.0.0.1:60642 - "GET /api/search/stream?q=2200510405 HTTP/1.1" 200 OK
2026-04-01 12:30:51,710 [INFO] api: GET /api/logs → 200 (9.6 ms)
INFO:     127.0.0.1:54271 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-01 12:30:51,870 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeNotices?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:52,033 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ProblemReports?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:52,255 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:52,276 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeRequests?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:52,692 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:52,879 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:52,901 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:54,101 [INFO] api: GET /api/logs → 200 (1.4 ms)
INFO:     127.0.0.1:58453 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-01 12:30:54,330 [INFO] api: DELETE /api/logs → 200 (0.7 ms)
INFO:     127.0.0.1:59404 - "DELETE /api/logs HTTP/1.1" 200 OK
2026-04-01 12:30:57,752 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 12:30:57,757 [INFO] api: GET /api/objects/part/2200510405 → 200 (1310.3 ms)
INFO:     127.0.0.1:61366 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
2026-04-01 12:30:57,916 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:30:58,657 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 12:30:58,659 [INFO] api: GET /api/objects/part/2200510405 → 200 (586.8 ms)
INFO:     127.0.0.1:53800 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
2026-04-01 12:30:58,684 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:31:03,471 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=0&%24select=ID "HTTP/1.1 200 200"
2026-04-01 12:31:03,473 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:31:03,584 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/app/ "HTTP/1.1 200 200"
2026-04-01 12:31:03,615 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/app/): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:31:03,616 [WARNING] src.adapters.base: CSRF refresh: konnte keinen Nonce erhalten
2026-04-01 12:31:03,616 [INFO] src.adapters.base: POST attempt 1: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut — CSRF_NONCE=(none)… Origin=https://plm-dev.neuhausen.balluff.net
2026-04-01 12:31:03,655 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut "HTTP/1.1 400 400"
2026-04-01 12:31:03,656 [WARNING] src.adapters.base: POST 400 response body: {"error":{"code":"INVALID_NONCE","message":"A potential security problem was detected. Refresh the page and try again. If the problem persists, contact your administrator."}}
Response headers: {'date': 'Wed, 01 Apr 2026 10:31:03 GMT', 'server': 'Apache', 'strict-transport-security': 'max-age=10368000; includeSubDomains;', 'x-ptc-connected': '1', 'x-frame-options': 'SAMEORIGIN', 'x-content-type-options': 'nosniff', 'x-do-not-compress-this': '1', 'vary': 'Accept-Encoding,User-Agent', 'connection': 'close', 'transfer-encoding': 'chunked', 'content-type': 'application/json'}
2026-04-01 12:31:03,657 [INFO] src.adapters.base: CSRF-Fehler erkannt — refreshe Nonce und wiederhole
2026-04-01 12:31:03,761 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=0&%24select=ID "HTTP/1.1 200 200"
2026-04-01 12:31:03,762 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:31:03,862 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/app/ "HTTP/1.1 200 200"
2026-04-01 12:31:03,894 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/app/): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:31:03,894 [WARNING] src.adapters.base: CSRF refresh: konnte keinen Nonce erhalten
2026-04-01 12:31:03,895 [INFO] src.adapters.base: POST attempt 2: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut — CSRF_NONCE=(none)… Origin=https://plm-dev.neuhausen.balluff.net
2026-04-01 12:31:03,940 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut "HTTP/1.1 400 400"
2026-04-01 12:31:03,942 [WARNING] src.adapters.base: POST 400 response body: {"error":{"code":"INVALID_NONCE","message":"A potential security problem was detected. Refresh the page and try again. If the problem persists, contact your administrator."}}
Response headers: {'date': 'Wed, 01 Apr 2026 10:31:03 GMT', 'server': 'Apache', 'strict-transport-security': 'max-age=10368000; includeSubDomains;', 'x-ptc-connected': '1', 'x-frame-options': 'SAMEORIGIN', 'x-content-type-options': 'nosniff', 'x-do-not-compress-this': '1', 'vary': 'Accept-Encoding,User-Agent', 'connection': 'close', 'transfer-encoding': 'chunked', 'content-type': 'application/json'}
2026-04-01 12:31:03,943 [INFO] api: POST /api/write/part/2200510405/checkout → 400 (576.2 ms)
INFO:     127.0.0.1:55259 - "POST /api/write/part/2200510405/checkout?objectId=OR%3Awt.part.WTPart%3A396506128 HTTP/1.1" 400 Bad Request
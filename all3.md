INFO:     Will watch for changes in these directories: ['C:\\Users\\keilt\\azure_api_agent\\windchill-api']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [24840] using WatchFiles
INFO:     Started server process [18628]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2026-04-01 12:13:57,935 [INFO] api: GET /api/logs → 401 (0.5 ms)
INFO:     127.0.0.1:52752 - "GET /api/logs?limit=120 HTTP/1.1" 401 Unauthorized
2026-04-01 12:13:58,865 [INFO] api: GET /api/auth/me → 401 (1.3 ms)
INFO:     127.0.0.1:60373 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-01 12:13:58,870 [INFO] api: GET /api/auth/me → 401 (0.8 ms)
INFO:     127.0.0.1:60375 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-01 12:13:58,886 [INFO] api: GET /api/auth/systems → 200 (0.5 ms)
INFO:     127.0.0.1:60377 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-01 12:13:58,890 [INFO] api: GET /api/auth/systems → 200 (0.7 ms)
INFO:     127.0.0.1:60379 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-01 12:14:00,471 [INFO] src.routers.auth: Login-Versuch: system=dev url=https://plm-dev.neuhausen.balluff.net/Windchill user=keilt
2026-04-01 12:14:00,472 [INFO] src.adapters.base: Connecting to https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6
2026-04-01 12:14:01,378 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt "HTTP/1.1 307 307"
2026-04-01 12:14:01,442 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ "HTTP/1.1 200 200"
2026-04-01 12:14:01,443 [INFO] src.adapters.base: Auth-Probe: status=200 url=https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ content-type=application/json;odata.metadata=minimal www-authenticate=
2026-04-01 12:14:01,443 [INFO] src.adapters.base: Basic Auth akzeptiert (status=200)
2026-04-01 12:14:01,444 [INFO] src.adapters.base: Basic Auth: Kein CSRF_NONCE in Antwort — Windchill nutzt vermutlich Custom-Header-Check (X-Requested-With)
2026-04-01 12:14:01,445 [INFO] api: POST /api/auth/login → 200 (975.3 ms)
INFO:     127.0.0.1:55201 - "POST /api/auth/login HTTP/1.1" 200 OK
2026-04-01 12:14:08,339 [INFO] api: GET /api/search/stream → 200 (1.7 ms)
INFO:     127.0.0.1:56993 - "GET /api/search/stream?q=2200510405 HTTP/1.1" 200 OK
2026-04-01 12:14:08,553 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeRequests?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:14:08,555 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ProblemReports?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:14:08,608 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeNotices?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:14:08,856 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:14:09,200 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:14:10,935 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 12:14:10,936 [INFO] api: GET /api/objects/part/2200510405 → 200 (533.8 ms)
INFO:     127.0.0.1:63523 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
2026-04-01 12:14:11,503 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 12:14:11,507 [INFO] api: GET /api/objects/part/2200510405 → 200 (566.0 ms)
INFO:     127.0.0.1:63525 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
2026-04-01 12:14:15,200 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:14:15,532 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:14:20,581 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=0&%24select=ID "HTTP/1.1 200 200"
2026-04-01 12:14:20,582 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:14:20,653 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/app/ "HTTP/1.1 200 200"
2026-04-01 12:14:20,687 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/app/): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:14:20,688 [WARNING] src.adapters.base: CSRF refresh: konnte keinen Nonce erhalten
2026-04-01 12:14:20,688 [INFO] src.adapters.base: POST attempt 1: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut — CSRF_NONCE=(none)… Origin=https://plm-dev.neuhausen.balluff.net
2026-04-01 12:14:20,729 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut "HTTP/1.1 400 400"
2026-04-01 12:14:20,731 [WARNING] src.adapters.base: POST 400 response body: {"error":{"code":"INVALID_NONCE","message":"A potential security problem was detected. Refresh the page and try again. If the problem persists, contact your administrator."}}
Response headers: {'date': 'Wed, 01 Apr 2026 10:14:20 GMT', 'server': 'Apache', 'strict-transport-security': 'max-age=10368000; includeSubDomains;', 'x-ptc-connected': '1', 'x-frame-options': 'SAMEORIGIN', 'x-content-type-options': 'nosniff', 'x-do-not-compress-this': '1', 'vary': 'Accept-Encoding,User-Agent', 'connection': 'close', 'transfer-encoding': 'chunked', 'content-type': 'application/json'}
2026-04-01 12:14:20,732 [INFO] src.adapters.base: CSRF-Fehler erkannt — refreshe Nonce und wiederhole
2026-04-01 12:14:20,900 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=0&%24select=ID "HTTP/1.1 200 200"
2026-04-01 12:14:20,901 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:14:21,007 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/app/ "HTTP/1.1 200 200"
2026-04-01 12:14:21,047 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/app/): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:14:21,048 [WARNING] src.adapters.base: CSRF refresh: konnte keinen Nonce erhalten
2026-04-01 12:14:21,049 [INFO] src.adapters.base: POST attempt 2: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut — CSRF_NONCE=(none)… Origin=https://plm-dev.neuhausen.balluff.net
2026-04-01 12:14:21,092 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut "HTTP/1.1 400 400"
2026-04-01 12:14:21,094 [WARNING] src.adapters.base: POST 400 response body: {"error":{"code":"INVALID_NONCE","message":"A potential security problem was detected. Refresh the page and try again. If the problem persists, contact your administrator."}}
Response headers: {'date': 'Wed, 01 Apr 2026 10:14:20 GMT', 'server': 'Apache', 'strict-transport-security': 'max-age=10368000; includeSubDomains;', 'x-ptc-connected': '1', 'x-frame-options': 'SAMEORIGIN', 'x-content-type-options': 'nosniff', 'x-do-not-compress-this': '1', 'vary': 'Accept-Encoding,User-Agent', 'connection': 'close', 'transfer-encoding': 'chunked', 'content-type': 'application/json'}
2026-04-01 12:14:21,095 [INFO] api: POST /api/write/part/2200510405/checkout → 400 (592.6 ms)
INFO:     127.0.0.1:51140 - "POST /api/write/part/2200510405/checkout?objectId=OR%3Awt.part.WTPart%3A396506128 HTTP/1.1" 400 Bad Request
INFO:     Will watch for changes in these directories: ['C:\\Users\\keilt\\azure_api_agent\\windchill-api']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [15388] using WatchFiles
2026-04-01 12:07:17,176 [INFO] watchfiles.main: 2 changes detected
INFO:     Started server process [27544]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2026-04-01 12:07:17,541 [INFO] watchfiles.main: 1 change detected
2026-04-01 12:07:18,096 [INFO] watchfiles.main: 6 changes detected
2026-04-01 12:07:20,213 [INFO] watchfiles.main: 11 changes detected
2026-04-01 12:07:22,670 [INFO] api: GET /api/auth/me → 401 (1.6 ms)
INFO:     127.0.0.1:50548 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-01 12:07:22,679 [INFO] api: GET /api/auth/me → 401 (1.4 ms)
INFO:     127.0.0.1:50550 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-01 12:07:22,704 [INFO] api: GET /api/auth/systems → 200 (1.0 ms)
INFO:     127.0.0.1:50552 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-01 12:07:22,709 [INFO] api: GET /api/auth/systems → 200 (0.6 ms)
INFO:     127.0.0.1:50554 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-01 12:07:24,018 [INFO] src.routers.auth: Login-Versuch: system=dev url=https://plm-dev.neuhausen.balluff.net/Windchill user=keilt
2026-04-01 12:07:24,019 [INFO] src.adapters.base: Connecting to https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6
2026-04-01 12:07:24,941 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt "HTTP/1.1 307 307"
2026-04-01 12:07:25,011 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ "HTTP/1.1 200 200"
2026-04-01 12:07:25,012 [INFO] src.adapters.base: Auth-Probe: status=200 url=https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ content-type=application/json;odata.metadata=minimal www-authenticate=
2026-04-01 12:07:25,013 [INFO] src.adapters.base: Basic Auth akzeptiert (status=200)
2026-04-01 12:07:25,014 [INFO] src.adapters.base: Basic Auth: Kein CSRF_NONCE in Antwort — Windchill nutzt vermutlich Custom-Header-Check (X-Requested-With)
2026-04-01 12:07:25,016 [INFO] api: POST /api/auth/login → 200 (999.3 ms)
INFO:     127.0.0.1:50556 - "POST /api/auth/login HTTP/1.1" 200 OK
2026-04-01 12:07:45,543 [INFO] api: GET /api/search/stream → 200 (3.7 ms)
INFO:     127.0.0.1:51558 - "GET /api/search/stream?q=2200510405 HTTP/1.1" 200 OK
2026-04-01 12:07:45,756 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeRequests?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:07:45,770 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ProblemReports?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:07:45,786 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeNotices?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:07:45,959 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:07:46,193 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:07:48,785 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 12:07:48,789 [INFO] api: GET /api/objects/part/2200510405 → 200 (723.0 ms)
INFO:     127.0.0.1:57158 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
2026-04-01 12:07:49,389 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 12:07:49,391 [INFO] api: GET /api/objects/part/2200510405 → 200 (596.1 ms)
INFO:     127.0.0.1:57162 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
2026-04-01 12:07:51,684 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:07:51,749 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 12:07:54,165 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=0&%24select=ID "HTTP/1.1 200 200"
2026-04-01 12:07:54,165 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:07:54,277 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/app/ "HTTP/1.1 200 200"
2026-04-01 12:07:54,321 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/app/): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:07:54,321 [WARNING] src.adapters.base: CSRF refresh: konnte keinen Nonce erhalten
2026-04-01 12:07:54,321 [INFO] src.adapters.base: POST attempt 1: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut — CSRF_NONCE=(none)…
2026-04-01 12:07:54,366 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut "HTTP/1.1 400 400"
2026-04-01 12:07:54,368 [INFO] src.adapters.base: POST response: status=400, resp_CSRF_NONCE=(none)
2026-04-01 12:07:54,368 [INFO] src.adapters.base: CSRF-Fehler bei POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut — refreshe Nonce und wiederhole
2026-04-01 12:07:54,487 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=0&%24select=ID "HTTP/1.1 200 200"
2026-04-01 12:07:54,488 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:07:54,600 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/app/ "HTTP/1.1 200 200"
2026-04-01 12:07:54,637 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/app/): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 12:07:54,637 [WARNING] src.adapters.base: CSRF refresh: konnte keinen Nonce erhalten
2026-04-01 12:07:54,638 [INFO] src.adapters.base: POST attempt 2: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut — CSRF_NONCE=(none)…
2026-04-01 12:07:54,681 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut "HTTP/1.1 400 400"
2026-04-01 12:07:54,682 [INFO] src.adapters.base: POST response: status=400, resp_CSRF_NONCE=(none)
2026-04-01 12:07:54,683 [INFO] api: POST /api/write/part/2200510405/checkout → 400 (634.2 ms)
INFO:     127.0.0.1:63145 - "POST /api/write/part/2200510405/checkout?objectId=OR%3Awt.part.WTPart%3A396506128 HTTP/1.1" 400 Bad Request
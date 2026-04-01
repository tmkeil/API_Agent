INFO:     Will watch for changes in these directories: ['C:\\Users\\keilt\\azure_api_agent\\windchill-api']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [7708] using WatchFiles
INFO:     Started server process [1072]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2026-04-01 11:58:03,794 [INFO] api: GET /api/auth/me → 401 (1.7 ms)
INFO:     127.0.0.1:50457 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-01 11:58:03,807 [INFO] api: GET /api/auth/me → 401 (0.7 ms)
INFO:     127.0.0.1:50459 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-01 11:58:03,818 [INFO] api: GET /api/auth/systems → 200 (0.6 ms)
INFO:     127.0.0.1:50461 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-01 11:58:03,823 [INFO] api: GET /api/auth/systems → 200 (0.8 ms)
INFO:     127.0.0.1:50463 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-01 11:58:05,177 [INFO] src.routers.auth: Login-Versuch: system=dev url=https://plm-dev.neuhausen.balluff.net/Windchill user=keilt
2026-04-01 11:58:05,179 [INFO] src.adapters.base: Connecting to https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6
2026-04-01 11:58:06,090 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt "HTTP/1.1 307 307"
2026-04-01 11:58:06,157 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ "HTTP/1.1 200 200"
2026-04-01 11:58:06,158 [INFO] src.adapters.base: Auth-Probe: status=200 url=https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ content-type=application/json;odata.metadata=minimal www-authenticate=
2026-04-01 11:58:06,158 [INFO] src.adapters.base: Basic Auth akzeptiert (status=200)
2026-04-01 11:58:06,159 [WARNING] src.adapters.base: Basic Auth: KEIN CSRF_NONCE in Antwort. Response-Headers: {}
2026-04-01 11:58:06,161 [INFO] api: POST /api/auth/login → 200 (984.9 ms)
INFO:     127.0.0.1:59821 - "POST /api/auth/login HTTP/1.1" 200 OK
2026-04-01 11:58:14,005 [INFO] api: GET /api/search/stream → 200 (1.7 ms)
INFO:     127.0.0.1:59466 - "GET /api/search/stream?q=2200510405 HTTP/1.1" 200 OK
2026-04-01 11:58:14,274 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeRequests?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 11:58:14,292 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ProblemReports?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 11:58:14,342 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeNotices?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 11:58:14,567 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 11:58:14,810 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 11:58:16,875 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 11:58:16,878 [INFO] api: GET /api/objects/part/2200510405 → 200 (639.5 ms)
INFO:     127.0.0.1:49670 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
2026-04-01 11:58:17,497 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 11:58:17,500 [INFO] api: GET /api/objects/part/2200510405 → 200 (612.4 ms)
INFO:     127.0.0.1:53639 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
2026-04-01 11:58:20,675 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 11:58:21,571 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 11:58:24,944 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=0&%24select=ID "HTTP/1.1 200 200"
2026-04-01 11:58:24,944 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 11:58:25,051 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/app/ "HTTP/1.1 200 200"
2026-04-01 11:58:25,078 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/app/): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 11:58:25,079 [WARNING] src.adapters.base: CSRF refresh: konnte keinen Nonce erhalten
2026-04-01 11:58:25,079 [INFO] src.adapters.base: POST attempt 1: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut — CSRF_NONCE=(none)…
2026-04-01 11:58:25,128 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut "HTTP/1.1 400 400"
2026-04-01 11:58:25,129 [INFO] src.adapters.base: POST response: status=400, resp_CSRF_NONCE=(none)
2026-04-01 11:58:25,130 [INFO] src.adapters.base: CSRF-Fehler bei POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut — refreshe Nonce und wiederhole
2026-04-01 11:58:25,238 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24top=0&%24select=ID "HTTP/1.1 200 200"
2026-04-01 11:58:25,239 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 11:58:25,340 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/app/ "HTTP/1.1 200 200"
2026-04-01 11:58:25,372 [INFO] src.adapters.base: _try_csrf_fetch(https://plm-dev.neuhausen.balluff.net/Windchill/app/): status=200, CSRF_NONCE=(none), all_csrf_headers={}
2026-04-01 11:58:25,373 [WARNING] src.adapters.base: CSRF refresh: konnte keinen Nonce erhalten
2026-04-01 11:58:25,373 [INFO] src.adapters.base: POST attempt 2: https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut — CSRF_NONCE=(none)…
2026-04-01 11:58:25,412 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut "HTTP/1.1 400 400"
2026-04-01 11:58:25,413 [INFO] src.adapters.base: POST response: status=400, resp_CSRF_NONCE=(none)
2026-04-01 11:58:25,415 [INFO] api: POST /api/write/part/2200510405/checkout → 400 (576.8 ms)
INFO:     127.0.0.1:51713 - "POST /api/write/part/2200510405/checkout?objectId=OR%3Awt.part.WTPart%3A396506128 HTTP/1.1" 400 Bad Request
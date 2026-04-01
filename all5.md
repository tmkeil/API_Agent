INFO:     Will watch for changes in these directories: ['C:\\Users\\keilt\\azure_api_agent\\windchill-api']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [24976] using WatchFiles
INFO:     Started server process [1016]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2026-04-01 14:33:00,613 [INFO] api: GET /api/logs → 401 (0.6 ms)
INFO:     127.0.0.1:51869 - "GET /api/logs?limit=120 HTTP/1.1" 401 Unauthorized
2026-04-01 14:33:01,583 [INFO] api: GET /api/auth/me → 401 (1.3 ms)
INFO:     127.0.0.1:60813 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-01 14:33:01,588 [INFO] api: GET /api/auth/me → 401 (0.6 ms)
INFO:     127.0.0.1:60815 - "GET /api/auth/me HTTP/1.1" 401 Unauthorized
2026-04-01 14:33:01,601 [INFO] api: GET /api/auth/systems → 200 (0.8 ms)
INFO:     127.0.0.1:60817 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-01 14:33:01,605 [INFO] api: GET /api/auth/systems → 200 (0.5 ms)
INFO:     127.0.0.1:60819 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-01 14:33:02,770 [INFO] src.routers.auth: Login-Versuch: system=dev url=https://plm-dev.neuhausen.balluff.net/Windchill user=keilt
2026-04-01 14:33:02,772 [INFO] src.adapters.base: Connecting to https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6
2026-04-01 14:33:04,084 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt "HTTP/1.1 307 307"
2026-04-01 14:33:04,131 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ "HTTP/1.1 200 200"
2026-04-01 14:33:04,132 [INFO] src.adapters.base: Auth-Probe: status=200 url=https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ content-type=application/json;odata.metadata=minimal www-authenticate=
2026-04-01 14:33:04,132 [INFO] src.adapters.base: Basic Auth akzeptiert (status=200)
2026-04-01 14:33:04,605 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/PTC/GetCSRFToken() "HTTP/1.1 200 200"
2026-04-01 14:33:04,606 [INFO] src.adapters.base: CSRF-Token erhalten: CSRF_NONCE=Jq0e0Fb1Djbs…
2026-04-01 14:33:04,606 [INFO] api: POST /api/auth/login → 200 (1837.6 ms)
INFO:     127.0.0.1:64126 - "POST /api/auth/login HTTP/1.1" 200 OK
2026-04-01 14:33:06,931 [INFO] api: GET /api/search/stream → 200 (2.0 ms)
INFO:     127.0.0.1:63446 - "GET /api/search/stream?q=2200510405&mode=auto HTTP/1.1" 200 OK
2026-04-01 14:33:07,068 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeRequests?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:07,099 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeNotices?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:07,100 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ProblemReports?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:07,431 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:07,434 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:11,950 [INFO] api: GET /api/search/stream → 200 (1.5 ms)
INFO:     127.0.0.1:49317 - "GET /api/search/stream?q=2200510405 HTTP/1.1" 200 OK
2026-04-01 14:33:12,104 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeNotices?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:12,291 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ProblemReports?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:12,327 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeRequests?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:12,418 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:12,489 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:12,524 [INFO] api: GET /api/logs → 200 (1.3 ms)
INFO:     127.0.0.1:50876 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-01 14:33:13,213 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:13,631 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:14,234 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 14:33:14,237 [INFO] api: GET /api/objects/part/2200510405 → 200 (531.7 ms)
INFO:     127.0.0.1:59009 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
2026-04-01 14:33:15,041 [INFO] api: GET /api/logs → 200 (2.3 ms)
INFO:     127.0.0.1:60749 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-01 14:33:15,131 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 14:33:15,133 [INFO] api: GET /api/objects/part/2200510405 → 200 (585.7 ms)
INFO:     127.0.0.1:63589 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
2026-04-01 14:33:17,405 [INFO] api: DELETE /api/logs → 200 (1.6 ms)
INFO:     127.0.0.1:49235 - "DELETE /api/logs HTTP/1.1" 200 OK
2026-04-01 14:33:17,541 [INFO] api: GET /api/logs → 200 (1.6 ms)
INFO:     127.0.0.1:61829 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-01 14:33:18,089 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:18,433 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%272200510405%27%20or%20contains%28Number%2C%272200510405%27%29%29 "HTTP/1.1 200 200"
2026-04-01 14:33:26,183 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/PTC/GetCSRFToken() "HTTP/1.1 200 200"
2026-04-01 14:33:26,184 [INFO] src.adapters.base: CSRF-Token erhalten: CSRF_NONCE=J8xuaKVpd4N4…
2026-04-01 14:33:27,888 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396506128')/PTC.ProdMgmt.CheckOut "HTTP/1.1 200 200"
2026-04-01 14:33:27,891 [INFO] api: POST /api/write/part/2200510405/checkout → 200 (1867.2 ms)
INFO:     127.0.0.1:65072 - "POST /api/write/part/2200510405/checkout?objectId=OR%3Awt.part.WTPart%3A396506128 HTTP/1.1" 200 OK
2026-04-01 14:33:28,609 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 14:33:28,612 [INFO] api: GET /api/objects/part/2200510405 → 200 (711.8 ms)
INFO:     127.0.0.1:52696 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
2026-04-01 14:33:46,107 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27&%24orderby=Version%20desc%2CIteration%20desc "HTTP/1.1 400 400"
2026-04-01 14:33:46,915 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27 "HTTP/1.1 200 200"
2026-04-01 14:33:46,918 [INFO] api: GET /api/objects/part/2200510405/versions → 200 (1012.9 ms)
INFO:     127.0.0.1:56391 - "GET /api/objects/part/2200510405/versions HTTP/1.1" 200 OK
2026-04-01 14:33:50,430 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/PTC/GetCSRFToken() "HTTP/1.1 200 200"
2026-04-01 14:33:50,431 [INFO] src.adapters.base: CSRF-Token erhalten: CSRF_NONCE=lKmqbtKusIXt…
2026-04-01 14:33:51,677 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396522873')/PTC.ProdMgmt.CheckOut "HTTP/1.1 200 200"
2026-04-01 14:33:51,679 [INFO] api: POST /api/write/part/2200510405/checkout → 200 (1295.3 ms)
INFO:     127.0.0.1:50335 - "POST /api/write/part/2200510405/checkout?objectId=OR%3Awt.part.WTPart%3A396522873 HTTP/1.1" 200 OK
2026-04-01 14:33:52,534 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 14:33:52,538 [INFO] api: GET /api/objects/part/2200510405 → 200 (532.7 ms)
INFO:     127.0.0.1:65214 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
2026-04-01 14:33:55,482 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/PTC/GetCSRFToken() "HTTP/1.1 200 200"
2026-04-01 14:33:55,483 [INFO] src.adapters.base: CSRF-Token erhalten: CSRF_NONCE=a1Jiq3TgL2NC…
2026-04-01 14:33:57,017 [INFO] httpx: HTTP Request: POST https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts('OR:wt.part.WTPart:396522873')/PTC.ProdMgmt.CheckIn "HTTP/1.1 200 200"
2026-04-01 14:33:57,020 [INFO] api: POST /api/write/part/2200510405/checkin → 200 (1580.9 ms)
INFO:     127.0.0.1:50551 - "POST /api/write/part/2200510405/checkin?objectId=OR%3Awt.part.WTPart%3A396522873 HTTP/1.1" 200 OK
2026-04-01 14:33:57,881 [INFO] httpx: HTTP Request: GET https://plm-dev.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=Number%20eq%20%272200510405%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-01 14:33:57,885 [INFO] api: GET /api/objects/part/2200510405 → 200 (545.8 ms)
INFO:     127.0.0.1:62257 - "GET /api/objects/part/2200510405 HTTP/1.1" 200 OK
INFO:     127.0.0.1:60002 - "GET /api/auth/systems HTTP/1.1" 200 OK
2026-04-16 18:35:37,976 [INFO] src.routers.auth: Login-Versuch: system=prod url=https://plm-prod.neuhausen.balluff.net/Windchill user=keilt
2026-04-16 18:35:37,979 [INFO] src.adapters.base: Connecting to https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt
2026-04-16 18:35:38,115 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt "HTTP/1.1 307 307"
2026-04-16 18:35:38,361 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ "HTTP/1.1 200 200"
2026-04-16 18:35:38,362 [INFO] src.adapters.base: Auth-Probe: status=200 url=https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/ content-type=application/json;odata.metadata=minimal www-authenticate=
2026-04-16 18:35:38,363 [INFO] src.adapters.base: Basic Auth akzeptiert (status=200)
2026-04-16 18:35:38,406 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/PTC/GetCSRFToken() "HTTP/1.1 200 200"
2026-04-16 18:35:38,407 [INFO] src.adapters.base: CSRF-Token erhalten: CSRF_NONCE=uhiQEJ1MkWWz…
2026-04-16 18:35:38,426 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v7/ProdMgmt "HTTP/1.1 404 404"
2026-04-16 18:35:38,427 [INFO] src.adapters.base: System unterstuetzt ProdMgmt v7 nicht (404) — verwende v6
2026-04-16 18:35:38,428 [INFO] api: POST /api/auth/login → 200 (453.5 ms)
INFO:     127.0.0.1:52960 - "POST /api/auth/login HTTP/1.1" 200 OK
2026-04-16 18:35:50,554 [INFO] api: GET /api/search/stream → 200 (6.1 ms)
INFO:     127.0.0.1:57815 - "GET /api/search/stream?q=9500000040 HTTP/1.1" 200 OK
2026-04-16 18:35:50,859 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/ProdMgmt/Parts?%24filter=%28Number%20eq%20%279500000040%27%20or%20contains%28Number%2C%279500000040%27%29%29 "HTTP/1.1 200 200"
2026-04-16 18:35:51,161 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeRequests?%24filter=%28Number%20eq%20%279500000040%27%20or%20contains%28Number%2C%279500000040%27%29%29 "HTTP/1.1 200 200"
2026-04-16 18:35:51,939 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeNotices?%24filter=%28Number%20eq%20%279500000040%27%20or%20contains%28Number%2C%279500000040%27%29%29 "HTTP/1.1 200 200"
2026-04-16 18:35:51,991 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ProblemReports?%24filter=%28Number%20eq%20%279500000040%27%20or%20contains%28Number%2C%279500000040%27%29%29 "HTTP/1.1 200 200"
2026-04-16 18:35:52,323 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments?%24filter=%28Number%20eq%20%279500000040%27%20or%20contains%28Number%2C%279500000040%27%29%29 "HTTP/1.1 200 200"
2026-04-16 18:35:55,756 [INFO] api: GET /api/logs → 200 (3.3 ms)
INFO:     127.0.0.1:52649 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-16 18:35:56,616 [INFO] api: DELETE /api/logs → 200 (1.5 ms)
INFO:     127.0.0.1:52652 - "DELETE /api/logs HTTP/1.1" 200 OK
2026-04-16 18:35:56,862 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%279500000040%27%20or%20contains%28Number%2C%279500000040%27%29%29 "HTTP/1.1 200 200"
2026-04-16 18:35:58,320 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/DocMgmt/Documents?%24filter=%28Number%20eq%20%279500000040%27%20or%20contains%28Number%2C%279500000040%27%29%29 "HTTP/1.1 200 200"
2026-04-16 18:35:58,569 [INFO] api: GET /api/logs → 200 (2.3 ms)
INFO:     127.0.0.1:53733 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-16 18:36:01,076 [INFO] api: GET /api/logs → 200 (0.8 ms)
INFO:     127.0.0.1:59995 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-16 18:36:03,289 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeNotices?%24filter=Number%20eq%20%279500000040%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-16 18:36:03,293 [INFO] api: GET /api/objects/change_notice/9500000040 → 200 (219.6 ms)
INFO:     127.0.0.1:51889 - "GET /api/objects/change_notice/9500000040 HTTP/1.1" 200 OK
2026-04-16 18:36:03,568 [INFO] api: GET /api/logs → 200 (2.1 ms)
INFO:     127.0.0.1:59906 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-16 18:36:03,799 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeNotices?%24filter=Number%20eq%20%279500000040%27%20and%20Latest%20eq%20true "HTTP/1.1 200 200"
2026-04-16 18:36:03,801 [INFO] api: GET /api/objects/change_notice/9500000040 → 200 (196.2 ms)
INFO:     127.0.0.1:50915 - "GET /api/objects/change_notice/9500000040 HTTP/1.1" 200 OK
2026-04-16 18:36:05,095 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeNotices?%24filter=Number%20eq%20%279500000040%27 "HTTP/1.1 200 200"
2026-04-16 18:36:05,419 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v6/ChangeMgmt/ChangeNotices('OR:wt.change2.WTChangeOrder2:16093826')/AffectedObjects "HTTP/1.1 200 200"
2026-04-16 18:36:05,422 [INFO] api: GET /api/changes/change_notice/9500000040/affected → 200 (484.0 ms)
INFO:     127.0.0.1:53840 - "GET /api/changes/change_notice/9500000040/affected HTTP/1.1" 200 OK
2026-04-16 18:36:05,767 [INFO] api: GET /api/logs → 200 (2.4 ms)
INFO:     127.0.0.1:53843 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-16 18:36:07,664 [INFO] api: DELETE /api/logs → 200 (2.1 ms)
INFO:     127.0.0.1:55093 - "DELETE /api/logs HTTP/1.1" 200 OK
2026-04-16 18:36:08,272 [INFO] api: GET /api/logs → 200 (1.9 ms)
INFO:     127.0.0.1:63628 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-16 18:36:09,107 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments?%24filter=Number%20eq%20%277100159502%27 "HTTP/1.1 200 200"
2026-04-16 18:36:09,111 [INFO] api: GET /api/objects/cad_document/7100159502 → 200 (505.7 ms)
INFO:     127.0.0.1:56879 - "GET /api/objects/cad_document/7100159502 HTTP/1.1" 200 OK
2026-04-16 18:36:10,762 [INFO] api: GET /api/logs → 200 (2.2 ms)
INFO:     127.0.0.1:56362 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-16 18:36:13,258 [INFO] api: GET /api/logs → 200 (2.1 ms)
INFO:     127.0.0.1:56383 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-16 18:36:13,979 [INFO] api: DELETE /api/logs → 200 (1.9 ms)
INFO:     127.0.0.1:62675 - "DELETE /api/logs HTTP/1.1" 200 OK
2026-04-16 18:36:15,754 [INFO] api: GET /api/logs → 200 (1.6 ms)
INFO:     127.0.0.1:57778 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-16 18:36:16,806 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments?%24filter=Number%20eq%20%277100159502%27 "HTTP/1.1 200 200"
2026-04-16 18:36:17,160 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments('OR:wt.epm.EPMDocument:51431687')/Uses "HTTP/1.1 200 200"
2026-04-16 18:36:17,322 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments?%24filter=FileName%20eq%20%27950190-I1_V1-1%27%20or%20FileName%20eq%20%27DECKEL_BCM_30x38x12%2C7_metal_mod-1%27%20or%20FileName%20eq%20%27HRDKBNGL_D1476-1%2C4X4-ST-A2-3%27%20or%20FileName%20eq%20%27612490%20Steckereinsatz%20bearbeitet-1%27%20or%20FileName%20eq%20%27HRDKBNGL_D1476-1%2C4X4-ST-A2-5%27%20or%20FileName%20eq%20%27HRDKBNGL_D1476-1%2C4X4-ST-A2-1%27%20or%20FileName%20eq%20%27HRDKBNGL_D1476-1%2C4X4-ST-A2-2%27%20or%20FileName%20eq%20%27HRDKBNGL_D1476-1%2C4X4-ST-A2-4%27%20or%20FileName%20eq%20%27950190-I1-20211215_v2-1%27%20or%20FileName%20eq%20%27Lichtleiter_BCM%20V2_M12_inside-1%27&%24select=Number%2CName%2CFileName%2CVersion%2CState%2CID "HTTP/1.1 200 200"
2026-04-16 18:36:17,435 [INFO] httpx: HTTP Request: GET https://plm-prod.neuhausen.balluff.net/Windchill/servlet/odata/v4/CADDocumentMgmt/CADDocuments?%24filter=FileName%20eq%20%27GEHAEUSE%20BCM%20V2_30x38x12%2C7_M12_MOD-1%27%20or%20FileName%20eq%20%27BCM%20V2_holder-1%27%20or%20FileName%20eq%20%27137030%20Ver%202%20modif%20f%C3%BCr%20BIC-1%27%20or%20FileName%20eq%20%27HRDKBNGL_D1476-1%2C4X4-ST-A2-6%27%20or%20FileName%20eq%20%27PCBA_BCM_V2_210929_PROTO2_b_2mm-1%27&%24select=Number%2CName%2CFileName%2CVersion%2CState%2CID "HTTP/1.1 200 200"
INFO:     127.0.0.1:65511 - "GET /api/documents/cad/7100159502/structure HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
  + Exception Group Traceback (most recent call last):
  |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\_utils.py", line 77, in collapse_excgroups
  |     yield
  |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\base.py", line 186, in __call__
  |     async with anyio.create_task_group() as task_group:
  |                ~~~~~~~~~~~~~~~~~~~~~~~^^
  |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\anyio\_backends\_asyncio.py", line 783, in __aexit__
  |     raise BaseExceptionGroup(
  |         "unhandled errors in a TaskGroup", self._exceptions
  |     ) from None
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 401, in run_asgi
    |     result = await app(  # type: ignore[func-returns-value]
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |         self.scope, self.receive, self.send
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |     )
    |     ^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 70, in __call__
    |     return await self.app(scope, receive, send)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\fastapi\applications.py", line 1054, in __call__
    |     await super().__call__(scope, receive, send)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\applications.py", line 113, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\errors.py", line 187, in __call__
    |     raise exc
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\base.py", line 185, in __call__
    |     with collapse_excgroups():
    |          ~~~~~~~~~~~~~~~~~~^^
    |   File "C:\Program Files\Python313\Lib\contextlib.py", line 162, in __exit__
    |     self.gen.throw(value)
    |     ~~~~~~~~~~~~~~^^^^^^^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\_utils.py", line 83, in collapse_excgroups
    |     raise exc
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\base.py", line 187, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\api.py", line 75, in add_timing_headers
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\base.py", line 163, in call_next
    |     raise app_exc
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\base.py", line 149, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\_exception_handler.py", line 62, in wrapped_app
    |     raise exc
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\_exception_handler.py", line 51, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\routing.py", line 715, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\routing.py", line 735, in app
    |     await route.handle(scope, receive, send)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\_exception_handler.py", line 62, in wrapped_app
    |     raise exc
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\_exception_handler.py", line 51, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\fastapi\routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |     ...<3 lines>...
    |     )
    |     ^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\fastapi\routing.py", line 214, in run_endpoint_function
    |     return await run_in_threadpool(dependant.call, **values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\concurrency.py", line 39, in run_in_threadpool
    |     return await anyio.to_thread.run_sync(func, *args)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\anyio\to_thread.py", line 63, in run_sync
    |     return await get_async_backend().run_sync_in_worker_thread(
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |         func, args, abandon_on_cancel=abandon_on_cancel, limiter=limiter
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |     )
    |     ^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\anyio\_backends\_asyncio.py", line 2502, in run_sync_in_worker_thread
    |     return await future
    |            ^^^^^^^^^^^^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\anyio\_backends\_asyncio.py", line 986, in run
    |     result = context.run(func, *args)
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\src\routers\documents.py", line 108, in cad_structure
    |     return document_service.get_cad_structure(client, code)
    |            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\src\services\document_service.py", line 181, in get_cad_structure
    |     nodes.append(CadStructureNode(
    |                  ~~~~~~~~~~~~~~~~^
    |         cadDocId=item.get("cadDocId", ""),
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |     ...<8 lines>...
    |         hasChildren=item.get("hasChildren", False),
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |     ))
    |     ^
    |   File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\pydantic\main.py", line 212, in __init__
    |     validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
    | pydantic_core._pydantic_core.ValidationError: 1 validation error for CadStructureNode
    | dependencyType
    |   Input should be a valid string [type=string_type, input_value=32768, input_type=int]
    |     For further information visit https://errors.pydantic.dev/2.9/v/string_type
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 401, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self.scope, self.receive, self.send
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 70, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\fastapi\applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\applications.py", line 113, in __call__
    await self.middleware_stack(scope, receive, send)
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\errors.py", line 187, in __call__
    raise exc
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\base.py", line 185, in __call__
    with collapse_excgroups():
         ~~~~~~~~~~~~~~~~~~^^
  File "C:\Program Files\Python313\Lib\contextlib.py", line 162, in __exit__
    self.gen.throw(value)
    ~~~~~~~~~~~~~~^^^^^^^
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\_utils.py", line 83, in collapse_excgroups
    raise exc
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\base.py", line 187, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\keilt\azure_api_agent\windchill-api\api.py", line 75, in add_timing_headers
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\base.py", line 163, in call_next
    raise app_exc
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\base.py", line 149, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\middleware\exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\_exception_handler.py", line 62, in wrapped_app
    raise exc
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\_exception_handler.py", line 51, in wrapped_app
    await app(scope, receive, sender)
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\routing.py", line 715, in __call__
    await self.middleware_stack(scope, receive, send)
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\routing.py", line 735, in app
    await route.handle(scope, receive, send)
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\_exception_handler.py", line 62, in wrapped_app
    raise exc
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\_exception_handler.py", line 51, in wrapped_app
    await app(scope, receive, sender)
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\fastapi\routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\fastapi\routing.py", line 214, in run_endpoint_function
    return await run_in_threadpool(dependant.call, **values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\starlette\concurrency.py", line 39, in run_in_threadpool
    return await anyio.to_thread.run_sync(func, *args)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\anyio\to_thread.py", line 63, in run_sync
    return await get_async_backend().run_sync_in_worker_thread(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        func, args, abandon_on_cancel=abandon_on_cancel, limiter=limiter
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\anyio\_backends\_asyncio.py", line 2502, in run_sync_in_worker_thread
    return await future
           ^^^^^^^^^^^^
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\anyio\_backends\_asyncio.py", line 986, in run
    result = context.run(func, *args)
  File "C:\Users\keilt\azure_api_agent\windchill-api\src\routers\documents.py", line 108, in cad_structure
    return document_service.get_cad_structure(client, code)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "C:\Users\keilt\azure_api_agent\windchill-api\src\services\document_service.py", line 181, in get_cad_structure
    nodes.append(CadStructureNode(
                 ~~~~~~~~~~~~~~~~^
        cadDocId=item.get("cadDocId", ""),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<8 lines>...
        hasChildren=item.get("hasChildren", False),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ))
    ^
  File "C:\Users\keilt\azure_api_agent\windchill-api\venv\Lib\site-packages\pydantic\main.py", line 212, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
pydantic_core._pydantic_core.ValidationError: 1 validation error for CadStructureNode
dependencyType
  Input should be a valid string [type=string_type, input_value=32768, input_type=int]
    For further information visit https://errors.pydantic.dev/2.9/v/string_type
2026-04-16 18:36:18,261 [INFO] api: GET /api/logs → 200 (2.3 ms)
INFO:     127.0.0.1:65514 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-16 18:36:21,077 [INFO] api: GET /api/logs → 200 (2.3 ms)
INFO:     127.0.0.1:54552 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
2026-04-16 18:36:23,257 [INFO] api: GET /api/logs → 200 (2.1 ms)
INFO:     127.0.0.1:53035 - "GET /api/logs?limit=120 HTTP/1.1" 200 OK
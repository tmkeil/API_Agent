https://support.ptc.com/help/windchill_rest_services/r1.6

Containers ist ein Entity Set der DataAdmin-Domain, nicht ProdMgmt.

Das heißt, es muss mit /servlet/odata/v6/DataAdmin/Containers abgefragt werden, nicht mit /servlet/odata/v6/ProdMgmt/Containers, was 404 liefert. Das offizielle Create-Part-Beispiel der PTC Doku nutzt /servlet/odata/ProdMgmt/ ohne Versions-Prefix, aber das scheint nicht zu funktionieren. Deshalb wird hier der unversionierte Pfad verwendet.

Das heißt, die offizielle Doku ist hier irreführend, da sie zwar den unversionierten Pfad nutzt, aber nicht klarstellt, dass es sich dabei um eine Ausnahme handelt. In der Regel sollten die versionierten Pfade verwendet werden, aber in diesem Fall muss der unversionierte Pfad genutzt werden, um die Container abzufragen.
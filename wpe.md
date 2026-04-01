Die Felder im WIndchill System, wenn ich ein Part erstellen will:
**Identity**
Product: P - Design
Number:	(Generated)
*	Name:	
Description:	
Hardware Version:	n.a.
*	Type: Component
*	Source:	Not Applicable
Associated Product Family:	PIU
*	View:	Design
*	Assembly Mode:	Separable
*	Gathering Part:	No
*	Default Unit: each
*	Location: 	/P - Design/Article
*	Configurable Module: Yes/No

***Classification**
*	Classification:

Unter Classification kann ich einen Find Button klicken und dann öffnet sich so ein Radio-Picker, wo ich eine Classification auswählen muss unter:
https://plm-dev.neuhausen.balluff.net/Windchill/ptc1/search/callSearchPicker?selectedObjectTypes=wt.part.WTPart%7Cde.balluff.BAL_MECHATRONIC_PART&pickerType=tree&objectTypeName=wt.part.WTPart%7Cde.balluff.BAL_MECHATRONIC_PART&showAllSelectable=false&attributeName=BAL_CLASSIFICATION_BINDING_WTPART&portlet=poppedup&objectType=structuredEnumerationPicker&u8=1

z.B. zur Verfügung: TBD, Label, Accessory: Nut Kit



unter default unit habe ich folgende Optionen:
<select id="defaultUnit" size="1" class="required " name="tcomp$attributesTable$OR:wt.folder.SubFolder:131787$___null!~objectHandle~partHandle~!_col_MdlAttr+java.lang.String+WCTYPE|wt.part.WTPart|de.balluff.BAL_MECHATRONIC_PART~MBA|masterReference^WCTYPE|wt.part.WTPartMaster~MBA|defaultUnit~~NEW|2203821406817707339~NEW|-2119243726112983980~+null___combobox"><option id="defaultUnit_ea" selected="" value="ea"> each </option><option id="defaultUnit_as_needed" value="as_needed"> as needed </option><option id="defaultUnit_kg" value="kg"> kilograms </option><option id="defaultUnit_m" value="m"> meters </option><option id="defaultUnit_l" value="l"> liters </option><option id="defaultUnit_sq_m" value="sq_m"> square meters </option><option id="defaultUnit_cu_m" value="cu_m"> cubic meters </option><option id="defaultUnit_g" value="g"> gram </option><option id="defaultUnit_mm" value="mm"> millimeter </option><option id="defaultUnit_fraction" value="fraction"> partial each </option><option id="defaultUnit_ml" value="ml"> milliliter </option><option id="defaultUnit_KAN" value="KAN"> can </option><option id="defaultUnit_FLA" value="FLA"> bottle </option><option id="defaultUnit_mg" value="mg"> milligram </option><option id="defaultUnit_sq_mm" value="sq_mm"> square millimeter </option><option id="defaultUnit_cm" value="cm"> centimeters </option><option id="defaultUnit_km" value="km"> kilometer </option><option id="defaultUnit_sq_cm" value="sq_cm"> square centimeters </option><option id="defaultUnit_FT" value="FT"> feed </option><option id="defaultUnit_IN" value="IN"> inch </option></select>

Unter View habe ich folgende Optionen:
<select size="1" class="required " name="tcomp$attributesTable$OR:wt.folder.SubFolder:131787$___null!~objectHandle~partHandle~!_col_viewRef___combobox" id="ext-gen100"><option id="null_" value="">  </option><option id="null_0002" value="OR:wt.vc.views.View:379728957"> 0002 </option><option id="null_CN01" value="OR:wt.vc.views.View:379728959"> CN01 </option><option id="null_Design" selected="" value="OR:wt.vc.views.View:24379"> Design </option><option id="null_Manufacturing" value="OR:wt.vc.views.View:24380"> Manufacturing </option><option id="null_MX02" value="OR:wt.vc.views.View:379728962"> MX02 </option></select>


Unter Assembly Mode habe ich die Optionen:
<select id="partType" size="1" class="required " name="tcomp$attributesTable$OR:wt.folder.SubFolder:131787$___null!~objectHandle~partHandle~!_col_MdlAttr+java.lang.String+WCTYPE|wt.part.WTPart|de.balluff.BAL_MECHATRONIC_PART~MBA|partType~~NEW|2203821406817707339~+null___combobox"><option id="partType_separable" selected="" value="separable"> Separable </option><option id="partType_inseparable" value="inseparable"> Inseparable </option><option id="partType_component" value="component"> Component </option></select>

Unter SOurce habe ich diese Optionen:
<select id="source" size="1" class="required " name="tcomp$attributesTable$OR:wt.folder.SubFolder:131787$___null!~objectHandle~partHandle~!_col_MdlAttr+java.lang.String+WCTYPE|wt.part.WTPart|de.balluff.BAL_MECHATRONIC_PART~MBA|source~~NEW|2203821406817707339~+null___combobox"><option id="source_" value="">  </option><option id="source_make" value="make"> Make </option><option id="source_buy" value="buy"> Buy </option><option id="source_notapplicable" selected="" value="notapplicable"> Not Applicable </option></select>

Unter Gathering Part habe ich die Optionen: Yes/No

Unter Associated Product Family habe ich folgende Optionen:
<select id="BAL_CP_ORDER_PREFIX" size="1" name="tcomp$attributesTable$OR:wt.folder.SubFolder:131787$___null!~objectHandle~partHandle~!_col_SoftAttr+java.lang.String+WCTYPE|wt.part.WTPart|de.balluff.BAL_MECHATRONIC_PART~IBA|BAL_CP_ORDER_PREFIX~~NEW|2203821406817707339~NAME|DEFAULT|false+null___combobox"><option id="BAL_CP_ORDER_PREFIX_" value="">  </option><option id="BAL_CP_ORDER_PREFIX_BAE" value="BAE"> BAE </option><option id="BAL_CP_ORDER_PREFIX_BAI" value="BAI"> BAI </option><option id="BAL_CP_ORDER_PREFIX_BAM" value="BAM"> BAM </option><option id="BAL_CP_ORDER_PREFIX_BAV" value="BAV"> BAV </option><option id="BAL_CP_ORDER_PREFIX_BAW" value="BAW"> BAW </option><option id="BAL_CP_ORDER_PREFIX_BCC" value="BCC"> BCC </option><option id="BAL_CP_ORDER_PREFIX_BCM" value="BCM"> BCM </option><option id="BAL_CP_ORDER_PREFIX_BCS" value="BCS"> BCS </option><option id="BAL_CP_ORDER_PREFIX_BCW" value="BCW"> BCW </option><option id="BAL_CP_ORDER_PREFIX_BDG" value="BDG"> BDG </option><option id="BAL_CP_ORDER_PREFIX_BEN" value="BEN"> BEN </option><option id="BAL_CP_ORDER_PREFIX_BES" value="BES"> BES </option><option id="BAL_CP_ORDER_PREFIX_BFB" value="BFB"> BFB </option><option id="BAL_CP_ORDER_PREFIX_BFD" value="BFD"> BFD </option><option id="BAL_CP_ORDER_PREFIX_BFF" value="BFF"> BFF </option><option id="BAL_CP_ORDER_PREFIX_BFO" value="BFO"> BFO </option><option id="BAL_CP_ORDER_PREFIX_BFS" value="BFS"> BFS </option><option id="BAL_CP_ORDER_PREFIX_BFT" value="BFT"> BFT </option><option id="BAL_CP_ORDER_PREFIX_BGL" value="BGL"> BGL </option><option id="BAL_CP_ORDER_PREFIX_BHS" value="BHS"> BHS </option><option id="BAL_CP_ORDER_PREFIX_BIC" value="BIC"> BIC </option><option id="BAL_CP_ORDER_PREFIX_BID" value="BID"> BID </option><option id="BAL_CP_ORDER_PREFIX_BIL" value="BIL"> BIL </option><option id="BAL_CP_ORDER_PREFIX_BIP" value="BIP"> BIP </option><option id="BAL_CP_ORDER_PREFIX_BIR" value="BIR"> BIR </option><option id="BAL_CP_ORDER_PREFIX_BIS" value="BIS"> BIS </option><option id="BAL_CP_ORDER_PREFIX_BIU" value="BIU"> BIU </option><option id="BAL_CP_ORDER_PREFIX_BIW" value="BIW"> BIW </option><option id="BAL_CP_ORDER_PREFIX_BKT" value="BKT"> BKT </option><option id="BAL_CP_ORDER_PREFIX_BLA" value="BLA"> BLA </option><option id="BAL_CP_ORDER_PREFIX_BLG" value="BLG"> BLG </option><option id="BAL_CP_ORDER_PREFIX_BLT" value="BLT"> BLT </option><option id="BAL_CP_ORDER_PREFIX_BMD" value="BMD"> BMD </option><option id="BAL_CP_ORDER_PREFIX_BMF" value="BMF"> BMF </option><option id="BAL_CP_ORDER_PREFIX_BML" value="BML"> BML </option><option id="BAL_CP_ORDER_PREFIX_BMP" value="BMP"> BMP </option><option id="BAL_CP_ORDER_PREFIX_BNI" value="BNI"> BNI </option><option id="BAL_CP_ORDER_PREFIX_BNL" value="BNL"> BNL </option><option id="BAL_CP_ORDER_PREFIX_BNN" value="BNN"> BNN </option><option id="BAL_CP_ORDER_PREFIX_BNP" value="BNP"> BNP </option><option id="BAL_CP_ORDER_PREFIX_BNS" value="BNS"> BNS </option><option id="BAL_CP_ORDER_PREFIX_BOD" value="BOD"> BOD </option><option id="BAL_CP_ORDER_PREFIX_BOH" value="BOH"> BOH </option><option id="BAL_CP_ORDER_PREFIX_BOL" value="BOL"> BOL </option><option id="BAL_CP_ORDER_PREFIX_BOS" value="BOS"> BOS </option><option id="BAL_CP_ORDER_PREFIX_BOW" value="BOW"> BOW </option><option id="BAL_CP_ORDER_PREFIX_BPI" value="BPI"> BPI </option><option id="BAL_CP_ORDER_PREFIX_BSE" value="BSE"> BSE </option><option id="BAL_CP_ORDER_PREFIX_BSG" value="BSG"> BSG </option><option id="BAL_CP_ORDER_PREFIX_BSI" value="BSI"> BSI </option><option id="BAL_CP_ORDER_PREFIX_BSP" value="BSP"> BSP </option><option id="BAL_CP_ORDER_PREFIX_BSS" value="BSS"> BSS </option><option id="BAL_CP_ORDER_PREFIX_BSW" value="BSW"> BSW </option><option id="BAL_CP_ORDER_PREFIX_BTL" value="BTL"> BTL </option><option id="BAL_CP_ORDER_PREFIX_BTM" value="BTM"> BTM </option><option id="BAL_CP_ORDER_PREFIX_BTS" value="BTS"> BTS </option><option id="BAL_CP_ORDER_PREFIX_BUS" value="BUS"> BUS </option><option id="BAL_CP_ORDER_PREFIX_BVS" value="BVS"> BVS </option><option id="BAL_CP_ORDER_PREFIX_BWL" value="BWL"> BWL </option><option id="BAL_CP_ORDER_PREFIX_EQU" value="EQU"> EQU </option><option id="BAL_CP_ORDER_PREFIX_FHW" value="FHW"> FHW </option><option id="BAL_CP_ORDER_PREFIX_PIU" selected="" value="PIU"> PIU </option><option id="BAL_CP_ORDER_PREFIX_PLP" value="PLP"> PLP </option><option id="BAL_CP_ORDER_PREFIX_SET" value="SET"> SET </option></select>



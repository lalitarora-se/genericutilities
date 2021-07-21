<?xml version="1.0" encoding="utf-8"?>
<?mso-application progid="Excel.Sheet"?>
<xsl:stylesheet version="1.0" 
	xmlns:html="http://www.w3.org/TR/REC-html40"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns="urn:schemas-microsoft-com:office:spreadsheet"
    xmlns:o="urn:schemas-microsoft-com:office:office" 
    xmlns:x="urn:schemas-microsoft-com:office:excel"
    xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
	<xsl:variable name="smallcase" select="'abcdefghijklmnopqrstuvwxyz'" />
	<xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />
 
	<xsl:template match="/">
		<xsl:processing-instruction name="mso-application">progid="Excel.Sheet"</xsl:processing-instruction>
		<!--The above instruction denotes the output XML file as an XML Spreadsheet, and configures the file to open in MS Excel-->
		<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
				  xmlns:o="urn:schemas-microsoft-com:office:office"
				  xmlns:x="urn:schemas-microsoft-com:office:excel"
				  xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"
				  xmlns:html="http://www.w3.org/TR/REC-html40">

			<DocumentProperties xmlns="urn:schemas-microsoft-com:office:office">
			</DocumentProperties>

            <Styles>
                <Style ss:ID="Default" ss:Name="Normal">
                    <Font ss:FontName="Calibri" ss:Size="11"/>
					<Interior />
					<Alignment ss:Vertical="Bottom" />
                    <NumberFormat />
                    <Protection />
                </Style>
                <Style ss:ID="Header">
                    <Font ss:FontName="Calibri" ss:Size="11" ss:Color="#FFFFFF" ss:Bold="1"/>
					<Interior ss:Color="#009530" ss:Pattern="Solid"/>
					<Alignment ss:Horizontal="Center" ss:Vertical="Center"/>
					<Borders>
						<Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="2"/>
						<Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="2"/>
						<Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="2"/>
						<Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="2"/>
					</Borders>
                </Style>
				<Style ss:ID="Header2" ss:Parent="Header">
                    <Font ss:FontName="Calibri" ss:Size="11" ss:Color="#FFFFFF" ss:Bold="0"/>
                </Style>
				<Style ss:ID="RowDivider">
                    <Font ss:FontName="Calibri" ss:Size="8" ss:Color="#FFFFFF" ss:Bold="0"/>
					<Interior ss:Color="#B2DFC1" ss:Pattern="Solid"/>
					<Alignment ss:Horizontal="Center" ss:Vertical="Center"/>
                </Style>
				<Style ss:ID="Cells">
                    <Font ss:FontName="Calibri" ss:Size="11"/>
					<Interior />
					<Alignment ss:Vertical="Bottom" />
                    <Borders>
						<Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1"/>
						<Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1"/>
						<Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1"/>
						<Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1"/>
					</Borders>                  
                    <NumberFormat />
                    <Protection />
                </Style>
				<Style ss:ID="Cells_Gray" ss:Parent="Cells">
                    <Interior ss:Color="#D9D9D9" ss:Pattern="Solid"/>
                </Style>
				<Style ss:ID="Cells_HC" ss:Parent="Cells">
                    <Alignment ss:Horizontal="Center" />
                </Style>
            </Styles>
 
			<ExcelWorkbook xmlns="urn:schemas-microsoft-com:office:excel">
				<ProtectStructure>False</ProtectStructure>
				<ProtectWindows>False</ProtectWindows>
			</ExcelWorkbook>
			
            <Worksheet ss:Name="Field Display Order">
                <Table> 
					<Column ss:AutoFitWidth="0" ss:Width="200" />    <!-- Feature Class-->
                    <Column ss:AutoFitWidth="0" ss:Width="75" />     <!-- SubType-->
					<Column ss:AutoFitWidth="0" ss:Width="150" />     <!-- Field-->
					
                    <Row>
						<Cell ss:StyleID="Header"><Data ss:Type="String">Feature Class</Data></Cell>
						<Cell ss:StyleID="Header"><Data ss:Type="String">Field</Data></Cell>						
					</Row>
					<xsl:if test="GXXML/FEATURECLASS">
						<xsl:apply-templates select="GXXML/FEATURECLASS">
							<xsl:sort select="FEATURENAME"/>
						</xsl:apply-templates>
					</xsl:if>
                </Table>
            </Worksheet>
        </Workbook>
     </xsl:template>
	

	<xsl:variable name="AttrubuteList">
		<xsl:text>OBJECTID,SHAPE,GLOBALID,LASTUSER,CREATIONUSER,DATECREATED,DATEMODIFIED,SYMBOLRORATION</xsl:text>
	</xsl:variable>
	
	<xsl:template match="GXXML/FEATURECLASS">				
		<xsl:variable name="featName" select="FEATURENAME"/>
		<xsl:if test="not(contains(translate($featName,$smallcase,$uppercase), '.SDE.'))">
			<xsl:for-each select="SUBTYPE[SUBTYPECODE='-1']">
				<xsl:for-each select="FIELD">  
					<xsl:sort select="FIELDNAME"/>
					<xsl:variable name="fieldName" select="FIELDNAME"/>						
					<xsl:if test="not(contains($AttrubuteList,$fieldName))">					
						<Row>
							<Cell ss:StyleID="Cells"><Data ss:Type="String"><xsl:value-of select="$featName"/></Data></Cell>
							<Cell ss:StyleID="Cells"><Data ss:Type="String"><xsl:value-of select="$fieldName"/></Data></Cell>							
						</Row>
					</xsl:if>
				</xsl:for-each>
				<xsl:for-each select="FIELD">  
					<xsl:sort select="FIELDNAME"/>
					<xsl:variable name="fieldName" select="FIELDNAME"/>						
					<xsl:if test="contains($AttrubuteList,$fieldName)">					
						<Row>
							<Cell ss:StyleID="Cells"><Data ss:Type="String"><xsl:value-of select="$featName"/></Data></Cell>
							<Cell ss:StyleID="Cells"><Data ss:Type="String"><xsl:value-of select="$fieldName"/></Data></Cell>							
						</Row>
					</xsl:if>
				</xsl:for-each>				
			</xsl:for-each>	
		</xsl:if>
		<Row ss:AutoFitHeight="0" ss:Height="10" >
			<Cell ss:MergeAcross="1" ss:StyleID="RowDivider"></Cell>
		</Row>
	</xsl:template>
	
</xsl:stylesheet>
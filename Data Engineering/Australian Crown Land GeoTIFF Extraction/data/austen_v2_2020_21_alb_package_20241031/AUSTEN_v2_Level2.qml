<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" styleCategories="AllStyleCategories" maxScale="0" minScale="1e+08" version="3.22.10-Białowieża">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal mode="0" enabled="0" fetchMode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option value="false" type="QString" name="WMSBackgroundLayer"/>
      <Option value="false" type="QString" name="WMSPublishDataSourceUrl"/>
      <Option value="0" type="QString" name="embeddedWidgets/count"/>
      <Option value="Value" type="QString" name="identify/format"/>
    </Option>
  </customproperties>
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option value="" type="QString" name="name"/>
      <Option name="properties"/>
      <Option value="collection" type="QString" name="type"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling maxOversampling="2" enabled="false" zoomedInResamplingMethod="nearestNeighbour" zoomedOutResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer alphaBand="-1" band="1" type="paletted" opacity="1" nodataColor="">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <colorPalette>
        <paletteEntry alpha="255" label="No data/ unresolved" value="0" color="#ffffff"/>
        <paletteEntry alpha="255" label="Freehold" value="1001" color="#b7d2e3"/>
        <paletteEntry alpha="255" label="Freehold" value="1002" color="#b7d2e3"/>
        <paletteEntry alpha="255" label="Leasehold" value="2111" color="#f2af00"/>
        <paletteEntry alpha="255" label="Leasehold" value="2112" color="#f2af00"/>
        <paletteEntry alpha="255" label="Leasehold" value="2121" color="#f2af00"/>
        <paletteEntry alpha="255" label="Leasehold" value="2122" color="#f2af00"/>
        <paletteEntry alpha="255" label="Leasehold" value="2131" color="#f2af00"/>
        <paletteEntry alpha="255" label="Leasehold" value="2132" color="#f2af00"/>
        <paletteEntry alpha="255" label="Leasehold" value="2141" color="#f2af00"/>
        <paletteEntry alpha="255" label="Leasehold" value="2142" color="#f2af00"/>
        <paletteEntry alpha="255" label="Leasehold" value="2151" color="#f2af00"/>
        <paletteEntry alpha="255" label="Leasehold" value="2152" color="#f2af00"/>
        <paletteEntry alpha="255" label="Leasehold" value="2161" color="#f2af00"/>
        <paletteEntry alpha="255" label="Leasehold" value="2162" color="#f2af00"/>
        <paletteEntry alpha="255" label="Crown purposes" value="2211" color="#6a7f10"/>
        <paletteEntry alpha="255" label="Crown purposes" value="2212" color="#6a7f10"/>
        <paletteEntry alpha="255" label="Crown purposes" value="2221" color="#6a7f10"/>
        <paletteEntry alpha="255" label="Crown purposes" value="2222" color="#6a7f10"/>
        <paletteEntry alpha="255" label="Crown purposes" value="2231" color="#6a7f10"/>
        <paletteEntry alpha="255" label="Crown purposes" value="2232" color="#6a7f10"/>
        <paletteEntry alpha="255" label="Other Crown land" value="2301" color="#dae5cd"/>
        <paletteEntry alpha="255" label="Other Crown land" value="2302" color="#dae5cd"/>
      </colorPalette>
      <colorramp type="randomcolors" name="[source]">
        <Option/>
      </colorramp>
    </rasterrenderer>
    <brightnesscontrast contrast="0" gamma="1" brightness="0"/>
    <huesaturation saturation="0" colorizeOn="0" invertColors="0" colorizeGreen="128" colorizeRed="255" colorizeBlue="128" colorizeStrength="100" grayscaleMode="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>

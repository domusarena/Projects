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
        <paletteEntry alpha="255" label="Freehold - Indigenous" value="1002" color="#5482ab"/>
        <paletteEntry alpha="255" label="Freeholding lease" value="2111" color="#6a4061"/>
        <paletteEntry alpha="255" label="Freeholding lease - Indigenous" value="2112" color="#dfd4d7"/>
        <paletteEntry alpha="255" label="Pastoral perpetual lease" value="2121" color="#b06a92"/>
        <paletteEntry alpha="255" label="Pastoral perpetual lease - Indigenous" value="2122" color="#afadc3"/>
        <paletteEntry alpha="255" label="Other perpetual lease" value="2131" color="#d3b8e2"/>
        <paletteEntry alpha="255" label="Other perpetual lease - Indigenous" value="2132" color="#8f8dcb"/>
        <paletteEntry alpha="255" label="Pastoral term lease" value="2141" color="#e0684b"/>
        <paletteEntry alpha="255" label="Pastoral term lease  - Indigenous" value="2142" color="#d52b1e"/>
        <paletteEntry alpha="255" label="Other term lease" value="2151" color="#ecc182"/>
        <paletteEntry alpha="255" label="Other term lease - Indigenous" value="2152" color="#c88f42"/>
        <paletteEntry alpha="255" label="Other lease" value="2161" color="#e2cdb8"/>
        <paletteEntry alpha="255" label="Other lease - Indigenous" value="2162" color="#512b1b"/>
        <paletteEntry alpha="255" label="Nature conservation reserve" value="2211" color="#284e36"/>
        <paletteEntry alpha="255" label="Nature conservation reserve - Indigenous" value="2212" color="#206c49"/>
        <paletteEntry alpha="255" label="Multiple-use public forest" value="2221" color="#a8b400"/>
        <paletteEntry alpha="255" label="Multiple-use public forest - Indigenous" value="2222" color="#6a7f10"/>
        <paletteEntry alpha="255" label="Other reserve" value="2231" color="#d6e342"/>
        <paletteEntry alpha="255" label="Other reserve - Indigenous " value="2232" color="#7ab800"/>
        <paletteEntry alpha="255" label="Other Crown land" value="2301" color="#dae5cd"/>
        <paletteEntry alpha="255" label="Other Crown land - Indigenous" value="2302" color="#e8e3be"/>
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

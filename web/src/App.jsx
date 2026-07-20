import { useState } from "react";
import DeckGL from "@deck.gl/react";
import { TileLayer, BitmapLayer, GeoJsonLayer } from "deck.gl";
import "./App.css";

// 성수동 bbox 중심 (docs 조사: lon 127.026~127.052, lat 37.533~37.549)
const INITIAL_VIEW_STATE = {
  longitude: 127.039,
  latitude: 37.541,
  zoom: 15,
  pitch: 0,
  bearing: 0,
};

const GENDER_COLOR = {
  MALE: [66, 133, 244, 200],
  FEMALE: [234, 67, 53, 200],
};

function App() {
  const [hoverInfo, setHoverInfo] = useState(null);

  const layers = [
    new TileLayer({
      id: "osm-tiles",
      data: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      minZoom: 0,
      maxZoom: 19,
      tileSize: 256,
      renderSubLayers: (props) => {
        const { boundingBox } = props.tile;
        return new BitmapLayer(props, {
          data: null,
          image: props.data,
          bounds: [
            boundingBox[0][0],
            boundingBox[0][1],
            boundingBox[1][0],
            boundingBox[1][1],
          ],
        });
      },
    }),
    new GeoJsonLayer({
      id: "citizens",
      data: "/citizens.geojson",
      pointType: "circle",
      getPointRadius: 8,
      pointRadiusUnits: "meters",
      getFillColor: (f) => GENDER_COLOR[f.properties.gender] ?? [128, 128, 128, 200],
      pickable: true,
      onHover: (info) => setHoverInfo(info.object ? info : null),
    }),
  ];

  return (
    <div style={{ position: "relative", width: "100vw", height: "100vh" }}>
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={layers}
      />
      {hoverInfo && (
        <div
          style={{
            position: "absolute",
            left: hoverInfo.x + 12,
            top: hoverInfo.y + 12,
            background: "white",
            padding: "6px 10px",
            borderRadius: 4,
            fontSize: 13,
            pointerEvents: "none",
            boxShadow: "0 1px 4px rgba(0,0,0,0.3)",
          }}
        >
          <div>성별: {hoverInfo.object.properties.gender}</div>
          <div>연령대: {hoverInfo.object.properties.age_band}</div>
        </div>
      )}
      <div
        style={{
          position: "absolute",
          bottom: 4,
          right: 8,
          background: "rgba(255,255,255,0.8)",
          fontSize: 11,
          padding: "2px 6px",
        }}
      >
        © OpenStreetMap contributors
      </div>
    </div>
  );
}

export default App;

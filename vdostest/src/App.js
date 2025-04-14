

import React, { useState, useEffect } from "react";
import Plot from "react-plotly.js";

function App() {
  const [timeF0, setTimeF0] = useState([]); // Time for F0
  const [f0Data, setF0Data] = useState([]); // F0 values

  const [timeCPP, setTimeCPP] = useState([]); // Time for CPP
  const [CPPData, setCPPData] = useState([]); // CPP values

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws");

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      // If the data contains F0, update the F0 plot
      if (data.f0 && data.timef0) {
        setTimeF0(data.timef0);
        setF0Data(data.f0);
      }

      // If the data contains CPP, update the CPP plot
      if (data.CPP && data.timeCPP) {
        setTimeCPP(data.timeCPP);
        setCPPData(data.CPP);
      }
    };

    return () => socket.close(); // Close WebSocket on unmount
  }, []);

  return (
    <div>
      <h1>Voice Doismeter Sample Results</h1>

      <Plot
        data={[
          {
            x: timeF0,
            y: f0Data,
            type: "scatter",
            mode: "lines+markers",
            marker: { color: "blue" },
          },
        ]}
        layout={{
          title: {text: 'F0'},
          xaxis: 
          { title: {text: "Blocks (50ms)" }, 
            titlefont: { size: 14, color: "black" }
          },
          yaxis: { title: {text: "Frequency (Hz)" }},
        }}
      />

      <Plot
        data={[
          {
            x: timeCPP,
            y: CPPData,
            type: "scatter",
            mode: "lines+markers",
            marker: { color: "green" },
          },
        ]}
        layout={{
          title: {text: "Cepstral Peak Prominence (CPP) Over Time"},
          xaxis: { title:{text: "Blocks (50ms)" }},
          yaxis: { title:{text: "Magnitude" }},
          width : 900,
          height : 500,
        }}
      />
    </div>
  );
}

export default App;

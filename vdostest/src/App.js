import React, { useState, useEffect } from "react";
import Plot from "react-plotly.js";

function App() {
  const [timeF0, setTimeF0] = useState([]);
  const [f0Data, setF0Data] = useState([]);

  const [timeCPP, setTimeCPP] = useState([]);
  const [CPPData, setCPPData] = useState([]);

  const [timeSPL, setTimeSPL] = useState([]);
  const [SPLData, setSPLData] = useState([]);

  const [devices, setDevices] = useState([]);
  const [connectedDevice, setConnectedDevice] = useState(null);
  const [services, setServices] = useState([]);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws");
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.f0 && data.timef0) {
        setTimeF0(data.timef0);
        setF0Data(data.f0);
      }

      if (data.CPP && data.timeCPP) {
        setTimeCPP(data.timeCPP);
        setCPPData(data.CPP);
      }

      if (data.spls && data.timespl) {
        setTimeSPL(data.timespl);
        setSPLData(data.spls);
      }
    };

    //return () => socket.close();
  }, []);
  

  const handleDisconnection = (event) => {
    const device = event.target;
    console.warn(`Device ${device.name} disconnected`);
    setConnectedDevice("DISCONNECTED");
    setServices([]);
  };

  const scanForDevices = async () => {
    try {
      const device = await navigator.bluetooth.requestDevice({
        acceptAllDevices: true,
      });
      setDevices([device]);
    } catch (error) {
      console.log("Cancelled device selection");
    }
  };

  const startLive = async () => {
    try {
      /*socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
  
        if (data.f0 && data.timef0) {
          setTimeF0(data.timef0);
          setF0Data(data.f0);
        }
  
        if (data.CPP && data.timeCPP) {
          setTimeCPP(data.timeCPP);
          setCPPData(data.CPP);
        }
  
        if (data.spls && data.timespl) {
          setTimeSPL(data.timespl);
          setSPLData(data.spls);
        }
      };*/
    } catch (error) {
      console.log("Start Live Error");
    }
  };

  const stopLive = async () => {
    try {
      //socket.close();
    } catch (error) {
      console.log("Canceled device selection");
    }
  };

  const connectToDevice = async (device) => {
    try {
      const server = await device.gatt.connect();
      device.addEventListener("gattserverdisconnected", handleDisconnection);
      setConnectedDevice(device.name || "Unknown Device");
      const availableServices = await server.getPrimaryServices();
      setServices(availableServices.map((s) => s.uuid));
    } catch (error) {
      console.error("Connection Error:", error);
    }
  };

  return (
    <div>
      <h1>Voice Dosimeter Sample Results</h1>

      <div
        style={{
          marginBottom: "2rem",
          padding: "1rem",
          border: "1px solid #ccc",
          borderRadius: "8px",
        }}
      >
        <h2>Bluetooth Device Manager</h2>
        <button onClick={scanForDevices} style={{ marginBottom: "1rem" }}>
          Scan for Bluetooth Devices
        </button>

        {devices.length > 0 && (
          <select
            onChange={(e) => {
              const selected = devices.find((d) => d.id === e.target.value);
              if (selected) connectToDevice(selected);
            }}
          >
            <option value="">-- Select a device --</option>
            {devices.map((device) => (
              <option key={device.id} value={device.id}>
                {device.name || "Unnamed Device"}
              </option>
            ))}
          </select>
        )}

        {connectedDevice && (
          <div
            style={{
              marginTop: "1rem",
              color: connectedDevice === "DISCONNECTED" ? "red" : "green",
            }}
          >
            {connectedDevice === "DISCONNECTED"
              ? "DISCONNECTED"
              : `CONNECTED TO: ${connectedDevice}`}
          </div>
        )}

        {services.length > 0 && (
          <div style={{ marginTop: "1rem" }}>
            <h4>Available Services:</h4>
            <ul>
              {services.map((s, idx) => (
                <li key={idx}>{s}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div
      style={{
        marginBottom: "2rem",
        padding: "1rem",
        border: "1px solid #ccc",
        borderRadius: "8px",
      }}>
        
      <h2>Start and Stop</h2>
        <button onClick={startLive} style={{ marginBottom: "1rem" }}>
          Start Live Analysis
        </button>
        <button onClick={stopLive} style={{ marginBottom: "1rem" }}>
          Stop Live Analysis
        </button>
      </div>



      {/* Plots */}
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
          title: { text: "F0" },
          xaxis: {
            title: { text: "Blocks (50ms)" },
            titlefont: { size: 14, color: "black" },
          },
          yaxis: { title: { text: "Frequency (Hz)" } },
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
          title: { text: "Cepstral Peak Prominence (CPP) Over Time" },
          xaxis: { title: { text: "Blocks (50ms)" } },
          yaxis: { title: { text: "Magnitude" } },
          width: 900,
          height: 500,
        }}
      />

      <Plot
        data={[
          {
            x: timeSPL,
            y: SPLData,
            type: "scatter",
            mode: "lines+markers",
            marker: { color: "blue" },
          },
        ]}
        layout={{
          title: { text: "SPL over Time" },
          xaxis: { title: { text: "Blocks (50ms)" } },
          yaxis: { title: { text: "Magnitude" } },
          width: 900,
          height: 500,
        }}
      />
    </div>
  );
}

export default App;

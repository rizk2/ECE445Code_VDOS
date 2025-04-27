import React, { useState, useEffect, useContext } from "react";
import { LiveContext } from "./LiveContext";
import Plot from "react-plotly.js";

function PlotData() {
    const [isLive, setisLive] = useContext(LiveContext); // Access shared state
    const [socket, setSocket] = useState(null);

    const [timeF0, setTimeF0] = useState([]);
    const [f0Data, setF0Data] = useState([]);

    const [timeCPP, setTimeCPP] = useState([]);
    const [CPPData, setCPPData] = useState([]);

    const [timeSPL, setTimeSPL] = useState([]);
    const [SPLData, setSPLData] = useState([]);

    const POINT_LIMIT = 1000;

    useEffect(() => {
        let ws = null;

        if (isLive) {
            console.log("Starting WebSocket connection for live data...");
            ws = new WebSocket("ws://localhost:8000/live-data");

            ws.onopen = () => {
                console.log("WebSocket connection established for live data.");
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log("Received data:", data); // Handle the received data

                if (data.f0 && data.timef0) {
                    /* setTimeF0((prev) => [...prev, ...data.timef0].slice(-1000));
                    setF0Data((prev) => [...prev, ...data.f0].slice(-1000)); */
                    setTimeF0(data.timef0);
                    setF0Data(data.f0);
                }

                if (data.CPP && data.timeCPP) {
                    /* setTimeCPP((prev) => [...prev, ...data.timeCPP].slice(-1000));
                    setCPPData((prev) => [...prev, ...data.CPP].slice(-1000)); */
                    setTimeCPP(data.timeCPP);
                    setCPPData(data.CPP);
                }

                if (data.spls && data.timespl) {
                    /* setTimeSPL((prev) => [...prev, ...data.timespl].slice(-1000));
                    setSPLData((prev) => [...prev, ...data.spls].slice(-1000)); */
                    setTimeSPL(data.timespl);
                    setSPLData(data.spls);
                }
            };

            ws.onclose = () => {
                console.log("WebSocket connection closed");
            };

            ws.onerror = (error) => {
                console.error("WebSocket error:", error);
            };

            setSocket(ws); // Store the WebSocket connection

        } else if (socket) {
            // Close WebSocket connection when live streaming stops
            socket.close();
            setSocket(null);
        }

        return () => {
            if (ws) {
                console.log("Closing WebSocket connection...");
                ws.close();
            }
        };
    }, [isLive]);

    return (
        <div>
            {/* First Plot: Fundamental Frequency */}
            <Plot 
                key='f0-plot'
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
                    title: { text: "Fundamental Frequency F0" },
                    xaxis: { title: { text: "Time Bins (50ms)" } },
                    yaxis: { title: { text: "Frequency (Hz)" }, 
                        range: [0, null] }, // Adjusted range to always start at 0
                    width: 1500,
                    height: 500,
                }}
            />

            {/* Second Plot: Cepstral Peak Prominence */}
            <Plot 
                key='cpp-plot'
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
                    title: { text: "Cepstral Peak Prominence (CPP)" },
                    xaxis: { title: { text: "Time Bins (50ms)" } },
                    yaxis: { title: { text: "Magnitude" } },
                    width: 1500,
                    height: 500,
                }}
            />

            {/* Third Plot: Sound Pressure Level */}
            <Plot 
                key='spl-plot'
                data={[
                    {
                    x: timeSPL,
                    y: SPLData,
                    type: "scatter",
                    mode: "lines+markers",
                    marker: { color: "orange" },
                    },
                ]}
                layout={{
                    title: { text: "Sound Pressure Level (SPL)" },
                    xaxis: { title: { text: "Time Bins (50ms)" } },
                    yaxis: { title: { text: "Magnitude" } },
                    width: 1500,
                    height: 500,
                }}
            />
        </div>
    );
}

export default PlotData;
// This component is responsible for plotting data received from the Bluetooth device
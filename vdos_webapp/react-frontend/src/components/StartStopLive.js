import React, { useContext, useEffect } from "react";
import { LiveContext } from "./LiveContext";


function StartStopLive() {
    const [isLive, setIsLive] = useContext(LiveContext); // State to manage live data streaming status

    useEffect(() => {
        console.log("isLive state changed:", isLive);
    }, [isLive]); // Log the state change whenever isLive changes

    const controlLiveTransmission = async (live) => {
        try {
            // Call the backend API to control live data transmission
            const response = await fetch("http://127.0.0.1:8000/control-live_transmission", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ live }), // Send the boolean value
            });

            if (!response.ok) {
                throw new Error("Failed to control live transmission");
            }

            const data = await response.json();
            console.log(data.message);
        } catch (error) {
            console.error("Error controlling live transmission:", error);
        }
    };
    
    const startLive = () => {
        // Function to start live data streaming
        console.log("Starting live data streaming...");
        controlLiveTransmission(true); // Call the function to start live transmission
        setIsLive(true);
    };

    const stopLive = () => {
        // Function to stop live data streaming
        console.log("Stopping live data streaming...");
        controlLiveTransmission(false); // Call the function to stop live transmission
        setIsLive(false);
    };

    const clearPlots = async () => {
        // Function to clear the plots
        console.log("Clearing plots...");
        try {
            const response = await fetch("http://127.0.0.1:8000/reset-audio-data", {
                method: "POST",
            });

            if (!response.ok) {
                throw new Error("Failed to control live transmission");
            }

            const data = await response.json();
            console.log(data.message);
        } catch (error) {
            console.error("Error controlling live transmission:", error);
        }
    };



    // Render the buttons to start and stop live data streaming
    return (
        <div id='start-stop-live-section'>
            <button onClick={startLive} style={{ marginRight: "10px" }}>
                Start Live Analysis
            </button>

            <button onClick={stopLive} style={{ marginRight: "10px" }}>
                Stop Live Analysis
            </button>

            <button onClick={clearPlots}>
                Clear Plots
            </button>
        </div>
    );
}

export default StartStopLive;
// This component is responsible for starting and stopping live data streaming
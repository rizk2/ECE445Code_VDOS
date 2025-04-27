import React, { useState } from "react";

function BluetoothConnection() {
    // These variables are used to manage the Bluetooth discovery process
    const [devices, setDevices] = useState([]); // State to store available devices
    const [showDeviceList, setShowDeviceList] = useState(false); // State to control the modal visibility
    // These variables are used to manage the Bluetooth connection process
    const [connectedDeviceInfo, setConnectedDeviceInfo] = useState(null); // State to store connected device info
    const [showConnectedDeviceInfo, setShowConnectedDeviceInfo] = useState(false); // State to control the connected device info modal visibility
    const [isLoading, setIsLoading] = useState(false); // State to manage loading state

    const discoverDevices = async () => {
        setIsLoading(true); // Set loading state to true
        try {
            // Fetch the list of Bluetooth devices from the backend
            console.log("Fetching Bluetooth devices from backend...");
            const response = await fetch("http://127.0.0.1:8000/scan-bluetooth"); // FastAPI endpoint
            if (!response.ok) {
                throw new Error("Failed to fetch devices");
            }
            const data = await response.json();
            setDevices(data.devices); // Update the devices state with the response
            setShowDeviceList(true); // Show the modal
        } catch (error) {
            console.log("Error scanning for Bluetooth devices:", error);
        } finally {
            setIsLoading(false); // Set loading state to false
        }
    };

    const connectDevice = async (device) => {
        console.log("Device selected:", device);
        try {
            // Send a request to connect to the selected device
            const response = await fetch("http://127.0.0.1:8000/connect-device", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ address: device.address }), // Send the device address
            });

            if (!response.ok) {
                throw new Error("Failed to connect to device");
            }
            const data = await response.json();
            console.log("Connected to device:", data);

            // Close the device list modal and show the connected device info
            setShowDeviceList(false); // Close the modal after selection

            setConnectedDeviceInfo(data); // Store the connected device info
            setShowConnectedDeviceInfo(true); // Show the connected device info modal
        } catch (error) {
            console.log("Error connecting to device:", error);
        }
    };

    const closeModal = () => {
        setShowDeviceList(false); // Close the modal
    };

    const disconnectDevice = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/disconnect-device", {
                method: "POST",
            });
    
            if (!response.ok) {
                throw new Error("Failed to disconnect from device");
            }
    
            const data = await response.json();
            console.log("Disconnected from device:", data);
    
            // Clear the connected device info and close the modal
            setConnectedDeviceInfo(null);
            setShowConnectedDeviceInfo(false);
        } catch (error) {
            console.log("Error disconnecting from device:", error);
        }
    };


    // This the HTML structure of the Bluetooth connection component
    return (
        <div id='bluetooth-section'>
            <h2>Bluetooth Device Manager</h2>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <button onClick={discoverDevices}>
                    Scan for Bluetooth Devices
                </button>
                {isLoading && <div className="loading-wheel"></div>}
            </div>

            {/* Modal for displaying available devices */}
            {showDeviceList && (
                <div className="modal">
                    <div className="device-list-content">
                        <h3>Available Bluetooth Devices</h3>
                        <ul>
                            {devices.map((device, index) => (
                                <li key={index}
                                    onClick={() => connectDevice(device)}
                                    className="device-list">
                                    {device.name || "Unnamed Device"}
                                </li>
                            ))}
                        </ul>
                        <button onClick={closeModal}>Close</button>
                    </div>
                </div>
            )}

            {/* Modal for displaying connected device information */}
            {showConnectedDeviceInfo && connectedDeviceInfo && (
                <div className="modal">
                    <div className="device-info-content">
                        <h3>Connected Device Information</h3>
                        <p><strong>Message:</strong> {connectedDeviceInfo.message}</p>
                        <p><strong>MTU Size:</strong> {connectedDeviceInfo.mtu_size}</p>
                        <h4>Services:</h4>
                        <ul>
                            {connectedDeviceInfo.services.map((service, index) => (
                                <li key={index}>
                                    <strong>Service UUID:</strong> {service.service_uuid}
                                    <ul>
                                        {service.characteristics.map((characteristic, charIndex) => (
                                            <li key={charIndex}>
                                                <strong>Characteristic UUID:</strong> {characteristic.uuid}<br />
                                                <strong>Properties:</strong> {characteristic.properties.join(", ")}
                                            </li>
                                        ))}
                                    </ul>
                                </li>
                            ))}
                        </ul>
                        <button onClick={disconnectDevice}>Disconnect</button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default BluetoothConnection;
// This component is responsible for managing the Bluetooth connection
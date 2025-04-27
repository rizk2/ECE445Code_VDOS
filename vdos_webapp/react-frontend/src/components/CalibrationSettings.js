import React from "react";

function CalibrationSettings() {

    const saveDefaultCalibrationLevel = async (event) => {
        event.preventDefault(); // Prevent the default form submission behavior

        const calibrationLevel = document.getElementById("calibration-level").value; // Get the value from the input field
        console.log("Saving default calibration level:", calibrationLevel);

        try {
            // Call the backend API to save the calibration level
            const response = await fetch("http://localhost:8000/set-calibration-constant", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ calibration_constant: parseFloat(calibrationLevel) }), // Send the calibration level as JSON
            });

            if (response.ok) {
                const data = await response.json();
                console.log(data.message); // Log the success message from the backend
            } else {
                const errorData = await response.json();
                console.error("Error:", errorData.detail);
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error("Error saving calibration level:", error);
            alert("Failed to save calibration level. Please try again.");
        }
    }

    return (
        <div id="calibration-section">
            <h2>SPL Calibration Settings</h2>
            <form>
                <label htmlFor="calibration-level">Calibration Level:</label>
                <input type="number" id="calibration-level" name="calibration-level" defaultValue="30.0" style={{ marginLeft: "10px" }} />
                <br />
                <br />
                <button type="submit" onClick={saveDefaultCalibrationLevel}>Save Calibration Settings</button>
            </form>
        </div>
    );
}

export default CalibrationSettings;
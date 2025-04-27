import { LiveProvider } from "./components/LiveContext";
import BluetoothConnection from "./components/BluetoothConnection";
import CalibrationSettings from "./components/CalibrationSettings";
import StartStopLive from "./components/StartStopLive";
import PlotData from "./components/PlotData";
// App.js
// This is the main application component that imports and uses the other components
// It manages the state and lifecycle of the application
// It is responsible for rendering the Bluetooth connection, start/stop live data, and plotting data components
import "./App.css"; // Importing CSS for styling
// Importing the necessary components for the application
// This component serves as the main entry point for the React application

function App() {
  return (
    <div>
      <h1
        style={{
          textAlign: "center",
          color: "#333",
          fontFamily: "Arial, sans-serif",
        }}
      >Voice Dosimeter Sample Results</h1>

      <BluetoothConnection />

      <CalibrationSettings />
      
      {/*The LiveProvider is used to provide a shared variable between the plotter and the buttons*/}
      <LiveProvider>  
        <div class="live-section">
          <StartStopLive />
          <PlotData />
        </div>
      </LiveProvider>

    </div>
  );
}

export default App;

import React, { createContext, useState } from "react";

export const LiveContext = createContext();

export const LiveProvider = ({ children }) => {
    const [isLive, setIsLive] = useState(false); // Shared state for live streaming

    return (
        <LiveContext.Provider value={[isLive, setIsLive]}>
            {children}
        </LiveContext.Provider>
    );
};
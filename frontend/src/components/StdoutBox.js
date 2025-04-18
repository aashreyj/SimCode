import React from "react";

const StdoutBox = ({ stdout }) => {
    return (
        <div className="stdout-box">
            <div className="output-label">Stdout:</div>
            <pre className="output-text">{stdout}</pre>
        </div>
    );
};

export default StdoutBox;

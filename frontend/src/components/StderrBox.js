import React from "react";

const StderrBox = ({ stderr }) => {
    return (
        <div className="stderr-box">
            <div className="output-label">Stderr:</div>
            <pre className="output-text">{stderr}</pre>
        </div>
    );
};

export default StderrBox;

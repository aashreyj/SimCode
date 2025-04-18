import React from "react";

const PrerequisitesInput = ({ prerequisites, setPrerequisites }) => {
    return (
        <textarea
            className="prerequisites"
            placeholder="Enter code pre-requisites here in Bash"
            value={prerequisites}
            onChange={(e) => setPrerequisites(e.target.value)}
        />
    );
};

export default PrerequisitesInput;
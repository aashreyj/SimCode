import React, {useState, useEffect} from "react";
import ACTIONS from "../actions/Actions";

const PrerequisitesInput = ({ socketRef, roomId, onPrerequisitesChange }) => {

    const [prerequisites, setPrerequisites] = useState("");

    useEffect(() => {
        if (socketRef.current) {
            socketRef.current.on(ACTIONS.PREREQ_CHANGE, ({prereq}) => {
                if (prereq !== null) {
                    setPrerequisites(prereq);
                    onPrerequisitesChange(prereq);
                }
            });
        }

        return () => {
            socketRef.current.off(ACTIONS.PREREQ_CHANGE);
        };
    }, [socketRef.current]);

    function handlePrerequisitesChange(value) {
        setPrerequisites(value);
        socketRef.current.emit(ACTIONS.PREREQ_CHANGE, {
            roomId,
            prerequisites: value
        });
        onPrerequisitesChange(value);
    }

    return (
        <textarea
            className="prerequisites"
            placeholder="Enter code pre-requisites here in Bash"
            value={prerequisites}
            onChange={(e) => handlePrerequisitesChange(e.target.value)}
        />
    );
};

export default PrerequisitesInput;
import React, { useRef, useState } from "react";
import toast from "react-hot-toast";
import { Navigate, useLocation, useNavigate, useParams } from "react-router-dom";
import { useRecoilState } from "recoil";
import ACTIONS from "../actions/Actions";
import { cmtheme, language, mode } from "../atoms";
import EditorPage from "../components/EditorPage";
import useSocket from "../hooks/useSocket";

const EditorPageContainer = () => {
    const apiUrl = `${process.env.REACT_APP_BACKEND_URL}/api/execute`;

    const [, setEditorMode] = useRecoilState(mode);
    const [lang, setLang] = useRecoilState(language);
    const [theme, setTheme] = useRecoilState(cmtheme);

    const [clients, setClients] = useState([]);
    const [stdout, setStdout] = useState("");
    const [stderr, setStderr] = useState("");

    const codeRef = useRef(null);
    const prereqRef = useRef(null);
    const location = useLocation();
    const { roomId } = useParams();
    const reactNavigator = useNavigate();

    // Use the custom hook for socket operations
    const socketRef = useSocket(
        roomId,
        location.state?.username,
        setClients,
        setLang,
        setStdout,
        setStderr,
        codeRef,
        prereqRef,
        lang
    );

    async function copyRoomId() {
        try {
            await navigator.clipboard.writeText(roomId);
            toast.success("Room ID has been copied to clipboard");
        } catch (err) {
            toast.error("Could not copy the Room ID");
            console.error(err);
        }
    }

    function leaveRoom(roomId) {
        if (socketRef.current) {
            socketRef.current.emit("leave", {
                roomId,
                username: location.state?.username,
            });
        }
        reactNavigator("/");
    }

    function changeLanguage(el) {
        setLang(el.target.value);
        setEditorMode(el.target.mode);
        if (socketRef.current) {
            socketRef.current.emit(ACTIONS.LANG_CHANGE, {
                roomId,
                lang: el.target.value,
            });
        }
    }

    const submitCodeHandler = async () => {
        if (lang === "markdown" || !codeRef.current) return;

        if (!prereqRef.current && !codeRef.current) {
            toast.error("Please enter code or pre-requisites");
            return;
        }

        try {
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    language: lang,
                    prerequisites: prereqRef.current,
                    code: codeRef.current,
                }),
            });

            if (!response.ok) throw new Error(`Error during code execution: ${response.status}`);
            const data = await response.json();
            setStdout(data.stdout);
            setStderr(data.stderr);

            socketRef.current.emit(ACTIONS.CODE_EXECUTED, {
                roomId,
                stdout: data.stdout,
                stderr: data.stderr,
            });
        } catch (error) {
            toast.error("Error while trying to execute code");
            console.log(error);
        }
    };

    if (!location.state) {
        return <Navigate to="/" />;
    }

    return (
        <EditorPage
            clients={clients}
            lang={lang}
            theme={theme}
            prerequisitesRef={prereqRef}
            stdout={stdout}
            stderr={stderr}
            setTheme={setTheme}
            changeLanguage={changeLanguage}
            copyRoomId={copyRoomId}
            leaveRoom={leaveRoom}
            submitCodeHandler={submitCodeHandler}
            socketRef={socketRef}
            roomId={roomId}
            codeRef={codeRef}
        />
    );
};

export default EditorPageContainer;
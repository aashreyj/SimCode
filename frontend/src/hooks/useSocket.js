import { useEffect, useRef } from "react";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import ACTIONS from "../actions/Actions";
import { initSocket } from "../socket";

const useSocket = (roomId, username, setClients, setLang, setStdout, setStderr, codeRef, prereqRef, lang) => {
    const socketRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        const init = async () => {
            socketRef.current = await initSocket();

            socketRef.current.on("connect_error", handleErrors);
            socketRef.current.on("connect_failed", handleErrors);

            function handleErrors(err) {
                console.error("Socket error:", err);
                toast.error("Socket connection failed, try again later.");
                navigate("/");
            }

            // Emit join event
            socketRef.current.emit("join", {
                roomId,
                username,
            });

            // Listen for joined event
            socketRef.current.on(ACTIONS.JOINED, ({ clients, username, socketId }) => {
                if (username !== username) {
                    toast.success(`${username} joined the room.`);
                }
                setClients(clients);

                // Sync code with the newly joined client
                socketRef.current.emit(ACTIONS.SYNC_CODE, {
                    code: codeRef.current,
                    prerequisites: prereqRef.current,
                    lang,
                    socketId,
                });
            });

            // Listen for disconnected event
            socketRef.current.on(ACTIONS.DISCONNECTED, ({ socketId, username }) => {
                toast.success(`${username} left the room.`);
                setClients((prev) => prev.filter((client) => client.socketId !== socketId));
            });

            // Listen for language change
            socketRef.current.on(ACTIONS.LANG_CHANGE, ({ lang }) => {
                setLang(lang);
            });

            // Listen for code execution results
            socketRef.current.on(ACTIONS.CODE_EXECUTED, ({ stdout, stderr }) => {
                setStdout(stdout);
                setStderr(stderr);
            });
        };

        init();

        return () => {
            // Cleanup socket listeners and disconnect
            if (socketRef.current) {
                socketRef.current.off(ACTIONS.JOINED);
                socketRef.current.off(ACTIONS.DISCONNECTED);
                socketRef.current.off(ACTIONS.LANG_CHANGE);
                socketRef.current.off(ACTIONS.CODE_EXECUTED);
                socketRef.current.disconnect();
            }
        };
    }, [roomId, username, setClients, setLang, setStdout, setStderr, navigate]);

    return socketRef;
};

export default useSocket;
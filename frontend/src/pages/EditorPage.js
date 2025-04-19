import React, {useState, useRef, useEffect} from 'react';
import toast from 'react-hot-toast';
import Client from '../components/Client';
import Editor from '../components/Editor'
import {language, cmtheme, mode} from '../../src/atoms';
import {useRecoilState} from 'recoil';
import ACTIONS from '../actions/Actions';
import {initSocket} from '../socket';
import {useLocation, useNavigate, Navigate, useParams} from 'react-router-dom';

const EditorPage = () => {

    const apiUrl = `${process.env.REACT_APP_BACKEND_URL}/api/execute`;

    const [editorMode, setEditorMode] = useRecoilState(mode)
    const [lang, setLang] = useRecoilState(language);
    const [theme, setTheme] = useRecoilState(cmtheme);

    const [clients, setClients] = useState([]);

    const [prerequisites, setPrerequisites] = useState("");
    const [stdout, setStdout] = useState("");
    const [stderr, setStderr] = useState("");

    const socketRef = useRef(null);
    const codeRef = useRef(null);
    const location = useLocation();
    const {roomId} = useParams();
    const reactNavigator = useNavigate();

    useEffect(() => {
        const init = async () => {
            socketRef.current = await initSocket();
            socketRef.current.on('connect_error', (err) => handleErrors(err));
            socketRef.current.on('connect_failed', (err) => handleErrors(err));

            function handleErrors(e) {
                console.log('socket error', e);
                toast.error('Socket connection failed, try again later.');
                reactNavigator('/');
            }

            socketRef.current.emit('join', {
                roomId,
                username: location.state?.username,
            });

            // Listening for joined event
            socketRef.current.on(
                ACTIONS.JOINED,
                ({clients, username, socketId}) => {
                    if (username !== location.state?.username) {
                        toast.success(`${username} joined the room.`);
                        console.log(`${username} joined`);
                    }
                    
                    setClients(clients);
                    socketRef.current.emit(ACTIONS.SYNC_CODE, {
                        code: codeRef.current,
                        socketId,
                    });
                }
            );

            // Listening for disconnected
            socketRef.current.on(
                ACTIONS.DISCONNECTED,
                ({socketId, username}) => {
                    toast.success(`${username} left the room.`);
                    console.log(`${username} left`);
                    setClients((prev) => {
                        return prev.filter(
                            (client) => client.socketId !== socketId
                        );
                    });
                }
            );

            // Listening for language change
            socketRef.current.on('lang_change',
                ({lang}) => {
                    setLang(lang);
                }
            );
        };
        init();
        return () => {
            socketRef.current.off(ACTIONS.JOINED);
            socketRef.current.off(ACTIONS.DISCONNECTED);
            socketRef.current.off(ACTIONS.LANG_CHANGE);
            socketRef.current.disconnect();
        };
    }, []);

    useEffect(() => {
        if (lang === "markdown")
            document.getElementsByClassName('submitBtn')[0].disabled = true;
    }, []);

    async function copyRoomId() {
        try {
            await navigator.clipboard.writeText(roomId);
            toast.success('Room ID has been copied to clipboard');
        } catch (err) {
            toast.error('Could not copy the Room ID');
            console.error(err);
        }
    }

    function leaveRoom(roomId) {
        if (socketRef.current) {
            socketRef.current.emit('leave', {
                roomId,
                username: location.state?.username,
            });
        }
        reactNavigator('/');
    }

    function changeLanguage(el) {
        setLang(el.target.value);
        setEditorMode(el.target.mode);
        if (socketRef.current) {
            socketRef.current.emit(
                ACTIONS.LANG_CHANGE, {
                roomId,
                lang: el.target.value
            });
        }
    }

    const submitCodeHandler = async () => {
        if (lang === "markdown" || !codeRef.current)
            return;

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    language: lang,
                    prerequisites,
                    code: codeRef.current
                })
            });
        
            if(!response.ok) throw new Error(`Error during code execution: ${response.status}`);
            const data = await response.json();
            setStdout(data.stdout);
            setStderr(data.stderr);
        } catch (error) {
            toast.error("Error while trying to execute code");
            console.log(error);
        }
    }

    if (!location.state) {
        return <Navigate to="/" />;
    }

    return (
        <div className="mainWrap">
            <div className="aside">
                <div className="asideInner">
                    <div className="logo">
                        <img
                            className="logoImage"
                            src="/logo.png"
                            alt="logo"
                        />
                    </div>
                    <h3>Connected</h3>
                    <div className="clientsList">
                        {clients.map((client) => (
                            <Client
                                key={client.socketId}
                                username={client.username}
                            />
                        ))}
                    </div>
                </div>

                <label>
                    Select Language:
                    <select value={lang} onChange={changeLanguage} className="seLang">
                        <option value="python" mode="python">Python</option>
                        <option value="cpp" mode="clike">C++</option>
                        <option value="java" mode="clike">Java</option>
                        <option value="javascript" mode="javascript">JavaScript</option>
                        <option value="bash" mode="shell">Shell</option>
                        <option value="markdown" mode="markdown">Markdown</option>
                    </select>
                </label>

                <label>
                    Select Theme:
                    <select value={theme} onChange={(e) => {setTheme(e.target.value);}} className="seLang">
                        <option value="cobalt">cobalt</option>
                        <option value="darcula">darcula</option>
                        <option value="eclipse">eclipse</option>
                        <option value="idea">idea</option>
                        <option value="material">material</option>
                        <option value="material-ocean">material-ocean</option>
                        <option value="monokai">monokai</option>
                        <option value="solarized">solarized</option>
                    </select>
                </label>

                <button className="btn copyBtn" onClick={copyRoomId}>
                    Copy Room ID
                </button>
                <button className="btn leaveBtn" onClick={() => {leaveRoom(roomId)}}>
                    Leave
                </button>
                <button className="btn submitBtn" onClick={submitCodeHandler}>
                    Run Code
                </button>
            </div>

            <div className="editor-layout">
                <div className="left-panel">
                    <textarea
                        className="prerequisites"
                        placeholder="Enter code pre-requisites here in Bash"
                        value={prerequisites}
                        onChange={(e) => setPrerequisites(e.target.value)}
                    />

                    <Editor
                        socketRef={socketRef}
                        roomId={roomId}
                        onCodeChange={(code) => {
                            codeRef.current = code;
                        }}
                    />
                </div>

                <div className="right-panel">
                    <div className="stdout-box">
                        <div className="output-label">Stdout:</div>
                        <pre className="output-text">{stdout}</pre>
                    </div>

                    <div className="stderr-box">
                        <div className="output-label">Stderr:</div>
                            <pre className="output-text">{stderr}</pre>
                        </div>
                    </div>
            </div>
        </div>
    );
}

export default EditorPage;
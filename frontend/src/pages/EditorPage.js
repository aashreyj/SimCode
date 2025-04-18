import React, { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { Navigate, useLocation, useNavigate, useParams } from 'react-router-dom';
import { useRecoilState } from 'recoil';
import { cmtheme, language, mode } from '../../src/atoms';
import ACTIONS from '../actions/Actions';
import Client from '../components/Client';
import Editor from '../components/Editor';
import LanguageSelector from '../components/LanguageSelector';
import PrerequisitesInput from '../components/PrerequisitesInput';
import StderrBox from '../components/StderrBox';
import StdoutBox from '../components/StdoutBox';
import ThemeSelector from '../components/ThemeSelector';
import { initSocket } from '../socket';

const EditorPage = () => {

    const apiUrl = `${process.env.REACT_APP_BACKEND_URL}/api/execute`;

    const [, setEditorMode] = useRecoilState(mode)
    const [lang, setLang] = useRecoilState(language);
    const [theme, setTheme] = useRecoilState(cmtheme);

    const [clients, setClients] = useState([]);

    const [stdout, setStdout] = useState("");
    const [stderr, setStderr] = useState("");

    const socketRef = useRef(null);
    const codeRef = useRef(null);
    const prereqRef = useRef(null);
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
                        prerequisites: prereqRef.current,
                        lang,
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
            socketRef.current.on(ACTIONS.LANG_CHANGE,
                ({lang}) => {
                    setLang(lang);
                }
            );

            // Listening for code execution
            socketRef.current.on(ACTIONS.CODE_EXECUTED, 
                ({stdout, stderr}) => {
                    setStdout(stdout);
                    setStderr(stderr);            
                }
            );
        };

        init();
        
        return () => {
            socketRef.current.off(ACTIONS.JOINED);
            socketRef.current.off(ACTIONS.DISCONNECTED);
            socketRef.current.off(ACTIONS.LANG_CHANGE);
            socketRef.current.off(ACTIONS.CODE_EXECUTED);
            socketRef.current.disconnect();
        };
    }, [reactNavigator, roomId, setLang]);

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
        if (lang === "markdown" || !codeRef.current) return;

        if (!prereqRef.current && !codeRef.current) {
            toast.error("Please enter code or pre-requisites");
            return;
        }

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    language: lang,
                    prerequisites: prereqRef.current,
                    code: codeRef.current
                })
            });
        
            if(!response.ok) throw new Error(`Error during code execution: ${response.status}`);
            const data = await response.json();
            setStdout(data.stdout);
            setStderr(data.stderr);

            socketRef.current.emit(ACTIONS.CODE_EXECUTED, {
                roomId,
                stdout: data.stdout,
                stderr: data.stderr
            });
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

                <LanguageSelector
                    lang={lang}
                    changeLanguage={changeLanguage}
                />

                <ThemeSelector
                    theme={theme}
                    setTheme={setTheme}
                />

                <button className="btn copyBtn" onClick={copyRoomId}>
                    Copy Room ID
                </button>
                <button className="btn leaveBtn" onClick={() => {leaveRoom(roomId)}}>
                    Leave
                </button>
                <button className="btn submitBtn" onClick={submitCodeHandler} disabled={lang === "markdown"}>
                    Run Code
                </button>
            </div>

            <div className="editor-layout">
                <div className="left-panel">
                    <PrerequisitesInput
                        socketRef={socketRef}
                        roomId={roomId}
                        onPrerequisitesChange={(prereq) => {
                            prereqRef.current = prereq;
                        }}
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
                    <StdoutBox stdout={stdout} />
                    <StderrBox stderr={stderr} />
                </div>
            </div>
        </div>
    );
}

export default EditorPage;
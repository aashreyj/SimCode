import React from 'react';
import Client from '../components/Client';
import Editor from '../components/Editor';
import LanguageSelector from '../components/LanguageSelector';
import PrerequisitesInput from '../components/PrerequisitesInput';
import StderrBox from '../components/StderrBox';
import StdoutBox from '../components/StdoutBox';
import ThemeSelector from '../components/ThemeSelector';

const EditorPage = ({
    clients,
    lang,
    theme,
    prerequisitesRef,
    stdout,
    stderr,
    setTheme,
    changeLanguage,
    copyRoomId,
    leaveRoom,
    submitCodeHandler,
    socketRef,
    roomId,
    codeRef,
}) => {
    return (
        <div className="mainWrap">
            <div className="aside">
                <div className="asideInner">
                    <div className="logo">
                        <img className="logoImage" src="/logo.png" alt="logo" />
                    </div>
                    <h3>Connected</h3>
                    <div className="clientsList">
                        {clients.map((client) => (
                            <Client key={client.socketId} username={client.username} />
                        ))}
                    </div>
                </div>

                <LanguageSelector lang={lang} changeLanguage={changeLanguage} />
                <ThemeSelector theme={theme} setTheme={setTheme} />

                <button className="btn copyBtn" onClick={copyRoomId}>
                    Copy Room ID
                </button>
                <button className="btn leaveBtn" onClick={() => leaveRoom(roomId)}>
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
                            prerequisitesRef.current = prereq;
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
};

export default EditorPage;
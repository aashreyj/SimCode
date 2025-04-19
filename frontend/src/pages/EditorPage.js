import React, { useState, useRef, useEffect } from "react";
import toast from "react-hot-toast";
import CodeMirror from 'codemirror';
import 'codemirror/lib/codemirror.css';
import 'codemirror/mode/javascript/javascript';
import Client from "../components/Client";
import Editor from "../components/Editor";
import DocumentPanel from "../components/DocumentPanel";
import { language, cmtheme, mode } from "../../src/atoms";
import { useRecoilState } from "recoil";
import ACTIONS from "../actions/Actions";
import { initSocket } from "../socket";
import {
  useLocation,
  useNavigate,
  Navigate,
  useParams,
} from "react-router-dom";
import { diffChars } from 'diff';


const EditorPage = () => {
  const apiUrl = `${process.env.REACT_APP_BACKEND_URL}/api/execute`;

  const [editorMode, setEditorMode] = useRecoilState(mode);
  const [lang, setLang] = useRecoilState(language);
  const [theme, setTheme] = useRecoilState(cmtheme);

  const [code, setCode] = useState("");
  const [clients, setClients] = useState([]);

  const [prerequisites, setPrerequisites] = useState("");
  const [stdout, setStdout] = useState("");
  const [stderr, setStderr] = useState("");

  const socketRef = useRef(null);
  const codeRef = useRef(null);
  const location = useLocation();
  const { roomId } = useParams();
  const reactNavigator = useNavigate();

  // Function to handle code changes - will be passed to Editor

    useEffect(() => {
      const handleBeforeUnload = () => {
        // Emit a leaveRoom event just before the user closes the window
        if (socketRef.current) {
          socketRef.current.emit("leave", {
            roomId,
            username: location.state?.username,
          });
        }
      };

      window.addEventListener("beforeunload", handleBeforeUnload);

      return () => {
        window.removeEventListener("beforeunload", handleBeforeUnload);
      };
    }, []);

  const handleCodeChange = (newCode) => {
    setCode(newCode);
    codeRef.current = newCode;
  };
  useEffect(() => {
    console.log("Code state updated in EditorPage:", code);
  }, [code]);
  useEffect(() => {
    const init = async () => {
      socketRef.current = await initSocket();
      socketRef.current.on("connect_error", (err) => handleErrors(err));
      socketRef.current.on("connect_failed", (err) => handleErrors(err));

      function handleErrors(e) {
        console.log("socket error", e);
        toast.error("Socket connection failed, try again later.");
        reactNavigator("/");
      }

      socketRef.current.emit("join", {
        roomId,
        username: location.state?.username,
      });

      socketRef.current.on("initial_state", (message) => {
                console.log(message)
                setUsers(message.users || []);
                setCode(message.document_snapshot || "");
                userColors.current = message.user_colors;
                setUserCursors(message.cursor_position || []);
                console.log(userColors.current);
            })


            socketRef.current.on("edit", (message) => {
                console.log("EDIT", message)
                if (message.user_id !== userId) {
                    suppressLocalChanges.current = true;
                    setCode(message.document_snapshot || "");
                    suppressLocalChanges.current = false;
                }
            })
            

            socketRef.current.on("operation", (message) => {  
                if (message.user_id !== userId) {
                    setCode(message.document_snapshot || "");
                }
            })

            socketRef.current.on("user_list", (message) => {
                setUsers(message.users || []);
                userColors.current = message.user_colors
                console.log("COOO", userColors.current)
            })

            socketRef.current.on("cursor", (message) => {
                console.log("CURSOR", message)
                setUserCursors(message.cursor_position || []);
            })


      // Listening for joined event
      socketRef.current.on(
        ACTIONS.JOINED,
        ({ clients, username, socketId }) => {
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
      socketRef.current.on(ACTIONS.DISCONNECTED, ({ socketId, username }) => {
        toast.success(`${username} left the room.`);
        console.log(`${username} left`);
        setClients((prev) => {
          return prev.filter((client) => client.socketId !== socketId);
        });
      });

      // Listening for language change
      socketRef.current.on("lang_change", ({ lang }) => {
        setLang(lang);
      });
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
      document.getElementsByClassName("submitBtn")[0].disabled = true;
  }, []);

  async function copyRoomId() {
    try {
      await navigator.clipboard.writeText(roomId);
      toast.success("Room ID has been copied to clipboard");
    } catch (err) {
      toast.error("Could not copy the Room ID");
      console.error(err);
    }
  }


    async function leaveRoom(roomId) {
        if (socketRef.current) {
        socketRef.current.emit("leave", {
            roomId,
            username: location.state?.username,
        });
        }
      try {
        const response = await fetch(
          `http://localhost:8000/api/sessions/leave/${roomId}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to leave session: ${response.status}`);
        }

        const data = await response.json();
        reactNavigator("/");
      } catch (error) {
        console.error("Error leaving session:", error);
      }
    };

    const applyCRDTOperation = (operation) => {
    const docText = editorInstance.current.getValue();

    if (operation.type === "insert") {
        const { position, text } = operation;
        const pos = offsetToPos(docText, position);
        editorInstance.current.replaceRange(text, pos, pos);
    } else if (operation.type === "delete") {
        const { position, length } = operation;
        const from = offsetToPos(docText, position);
        const to = offsetToPos(docText, position + length);
        editorInstance.current.replaceRange("", from, to);
    }
};


  const initializeEditor = (initialText) => {
    editorInstance.current = CodeMirror(editorRef.current, {
      value: initialText,
      lineNumbers: true,
      mode: "javascript",
      theme: "default"
    });

    editorInstance.current.on("cursorActivity", () => {
      if (suppressLocalChanges.current) return;
      const cursorPos = editorInstance.current.getCursor();
      socketRef.current.send(JSON.stringify({
        type: "cursor",
        user_id: userId,
        position: cursorPos
      }));
    });

    let previousValue = editorInstance.current.getValue(); 
    editorInstance.current.on("change", () => {
      if (suppressLocalChanges.current) return;
      const newValue = editorInstance.current.getValue();
    //   socketRef.current.send(JSON.stringify({
    //     type: "edit",
    //     user_id: userId,
    //     document_snapshot: value
    //   }));
        console.log("VAL",previousValue);
    const operation = generateCRDTOperation(previousValue,newValue);
        console.log("OP",operation)
  // Send the operation to the server
    socketRef.current.send(JSON.stringify({
        type: "operation",
        user_id: userId,
        operation: operation,
        document_snapshot:newValue
    }));
    previousValue = newValue;
        });
  };

  const generateCRDTOperation = (oldValue, newValue) => {
  
    // const oldValue = editorInstance.current.getValue();
  console.log("OLD",oldValue,"NEW",newValue);
  const diff = getDiffBetweenStrings(oldValue, newValue);
  
  const operations = diff.map((change) => {
    if (change.type === "insert") {
      return { type: "insert", position: change.position, text: change.text };
    } else if (change.type === "delete") {
      return { type: "delete", position: change.position, length: change.length };
    }
  });
  
  return operations;
};



const getDiffBetweenStrings = (oldStr, newStr) => {
  console.log("OLD",oldStr,"NEW",newStr);
    const diffs = diffChars(oldStr, newStr);
  const diff = [];



    
    let positionOld = 0; // To track position in old string
    let positionNew = 0; // To track position in new string

    diffs.forEach((part) => {
        if (part.added) {
            // Insertion: track where the insertion occurs in newStr
            diff.push({
                type: 'insert',
                position: positionNew,
                text: part.value
            });
            positionNew += part.value.length; // Update position for new string
        } else if (part.removed) {
            // Deletion: track where the deletion occurs in oldStr
            diff.push({
                type: 'delete',
                position: positionOld,
                length: part.value.length
            });
            positionOld += part.value.length; // Update position for old string
        } else {
            // For unchanged parts, just update positions
            positionOld += part.value.length;
            positionNew += part.value.length;
        }
    });

    console.log("DIFF", diff);
    return diff;
};


  const updateCursorPosition = (user_cursor_positions) => {
    if(!user_cursor_positions)
        return;
    for (const id in userCursors.current) {
      if (userCursors.current[id]) {
        userCursors.current[id].clear();
      }
    }

    for (const [id, pos] of Object.entries(user_cursor_positions)) {
      if (id === userId) continue;
      const { line, ch } = pos;
      if (line >= editorInstance.current.lineCount()) continue;

    //   const color = getUserColor(id);
        const color=userColors.current[id];
      const cursorEl = document.createElement("span");
      cursorEl.className = "remote-cursor";
      cursorEl.style.borderLeft = `2px solid ${color}`;
      cursorEl.style.height = "1em";
      cursorEl.style.marginLeft = "-1px";
      cursorEl.style.pointerEvents = "none";

      const label = document.createElement("div");
      label.textContent = id;
      label.style.position = "absolute";
      label.style.background = color;
      label.style.color = "#fff";
      label.style.padding = "2px 4px";
      label.style.fontSize = "10px";
      label.style.whiteSpace = "nowrap";
      label.style.top = "-1.2em";
      label.style.left = "0";
      label.style.borderRadius = "4px";

      const wrapper = document.createElement("span");
      wrapper.style.position = "relative";
      wrapper.appendChild(label);
      wrapper.appendChild(cursorEl);

      const bookmark = editorInstance.current.setBookmark({ line, ch }, { widget: wrapper, insertLeft: true });
      userCursors.current[id] = bookmark;
    }
  };

  async function copyRoomId() {
    try {
      await navigator.clipboard.writeText(roomId);
      toast.success('Room ID has been copied to clipboard');
    } catch (err) {
      toast.error('Could not copy the Room ID');
      console.error(err);
    }
  }

  function leaveRoom() {
    if (socketRef.current) {
      socketRef.current.send(JSON.stringify({
        type: 'leave',
        user_id: userId
      }));
    }
    reactNavigator('/');
  }

  if (!location.state) {
    return <Navigate to="/" />;
  }
  console.log("COLS:",userColors)
  console.log(users);

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

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          language: lang,
          prerequisites,
          code: codeRef.current,
        }),
      });

      if (!response.ok)
        throw new Error(`Error during code execution: ${response.status}`);
      const data = await response.json();
      setStdout(data.stdout);
      setStderr(data.stderr);
    } catch (error) {
      toast.error("Error while trying to execute code");
      console.log(error);
    }
  };

  if (!location.state) {
    return <Navigate to="/" />;
  }

  return (
    <div className="mainWrap">
      <div className="aside">
        <div className="asideInner">
          <div className="logo">
            <img className="logoImage" src="/logo.png" alt="logo" />
          </div>
          <h3>Connected</h3>
          <div className="clientsList">

             {clients.map((user) => (
  <Client key={user.socketId || user} username={user.username || user} color={userColors.current[user.username || user]} />
))}
          </div>
        </div>
        {/* Add document panel here */}

        <DocumentPanel
          roomId={roomId}
          username={location.state?.username}
          code={code}
          setCode={(newCode) => {
            console.log("Document panel setting code:", newCode);
            // Update local state
            setCode(newCode);
            // Update ref for socket events
            codeRef.current = newCode;

            // If connected to socket, emit code change
            if (socketRef.current) {
              socketRef.current.emit(ACTIONS.CODE_CHANGE, {
                roomId,
                code: newCode,
              });
            }
          }}
          language={lang}
          onLanguageChange={changeLanguage}
        />

        <label>
          Select Language:
          <select value={lang} onChange={changeLanguage} className="seLang">
            <option value="python" mode="python">
              Python
            </option>
            <option value="cpp" mode="clike">
              C++
            </option>
            <option value="java" mode="clike">
              Java
            </option>
            <option value="javascript" mode="javascript">
              JavaScript
            </option>
            <option value="bash" mode="shell">
              Shell
            </option>
            <option value="markdown" mode="markdown">
              Markdown
            </option>
          </select>
        </label>
        <label>
          Select Theme:
          <select
            value={theme}
            onChange={(e) => {
              setTheme(e.target.value);
            }}
            className="seLang"
          >
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
        <button
          className="btn leaveBtn"
          onClick={() => {
            leaveRoom(roomId);
          }}
        >
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
            onCodeChange={handleCodeChange}
            code={code}
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
};

export default EditorPage;

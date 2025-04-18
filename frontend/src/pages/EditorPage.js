import React, { useState, useRef, useEffect } from 'react';
import CodeMirror from 'codemirror';
import 'codemirror/lib/codemirror.css';
import 'codemirror/mode/javascript/javascript';
import toast from 'react-hot-toast';
import Client from '../components/Client';
import { language, cmtheme, mode } from '../../src/atoms';
import { useRecoilState } from 'recoil';
import { useLocation, useNavigate, Navigate, useParams } from 'react-router-dom';
import { diffChars } from 'diff';

const EditorPage = () => {

  const [editorMode, setEditorMode] = useRecoilState(mode);
  const [lang, setLang] = useRecoilState(language);
  const [theme, setTheme] = useRecoilState(cmtheme);
  const [users, setUsers] = useState([]);

  const socketRef = useRef(null);
  const editorRef = useRef(null);
  const editorInstance = useRef(null);
  const suppressLocalChanges = useRef(false);
  const userCursors = useRef({});
  const userColors = useRef({});
    // let userColors=[];
  const location = useLocation();
  const { roomId } = useParams();
  const reactNavigator = useNavigate();
  const { username } = location.state || {};
  const userId = username;

  useEffect(() => {
    const socket = new WebSocket(`ws://localhost:8000/ws/${roomId}/${userId}`);
    socketRef.current = socket;

    socket.addEventListener("open", () => {
      console.log("Connected to WebSocket");
    });

    socket.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      console.log("Received:", message);

      if (message.type === "initial_state") {
        if (!editorInstance.current) {
          initializeEditor(message.document_snapshot || "");
          userColors.current=message.user_colors;
        } else {
          editorInstance.current.setValue(message.document_snapshot || "");
        }
        setUsers(message.users || []);
        userColors.current=message.user_colors;
        updateCursorPosition(message.cursor_position || "");
        console.log(userColors.current);
      }

      if (message.type === "edit" && message.user_id !== userId) {
        suppressLocalChanges.current = true;
        editorInstance.current.setValue(message.document_snapshot);
        suppressLocalChanges.current = false;
      }

      if (message.type === "operation" && message.user_id !== userId) {
            applyCRDTOperation(message.operation);
        }

      if (message.type === "user_list") {
        setUsers(message.users || []);
        userColors.current=message.user_colors
        console.log("COOO",userColors.current)
      }

      if (message.type === "cursor") {
        updateCursorPosition(message.cursor_position);
      }

      if(message.type==="colors")
      {
        console.log(message)
      }
    });

    window.addEventListener("beforeunload", () => {
      socket.send(JSON.stringify({
        type: "leave",
        user_id: userId
      }));
    });

    return () => {
      socket.close();
    };
  }, []);

    const offsetToPos = (doc, offset) => {
    const lines = doc.split("\n");
    let currentOffset = 0;

    for (let i = 0; i < lines.length; i++) {
        const lineLength = lines[i].length + 1; // +1 for newline
        if (currentOffset + lineLength > offset) {
            return { line: i, ch: offset - currentOffset };
        }
        currentOffset += lineLength;
    }

    // fallback to end of doc
    const lastLine = lines.length - 1;
    return { line: lastLine, ch: lines[lastLine].length };
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
  return (
    <div className="mainWrap">
      <div className="aside">
        <div className="asideInner">
          <div className="logo">
            <img className="logoImage" src="/logo.png" alt="logo" />
          </div>
          <h3>Connected</h3>
          <div className="clientsList">
            {/* {Object.entries(userColors.current).map(([username, color]) => (
                <Client key={username} username={username} color={color} />
                ))} */}
                {users.map((user) => (
  <Client key={user.socketId || user} username={user.username || user} color={userColors.current[user.username || user]} />
))}

          </div>
        </div>

        <label>
          Select Language:
          <select value={lang} onChange={(e) => {
            setLang(e.target.value);
            setEditorMode(e.target.mode);
          }} className="seLang">
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
          <select value={theme} onChange={(e) => setTheme(e.target.value)} className="seLang">
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
          Copy ROOM ID
        </button>
        <button className="btn leaveBtn" onClick={leaveRoom}>
          Leave
        </button>
      </div>

      <div className="editorWrap">
        <div ref={editorRef} style={{ height: '100%', width: '100%' }} />
      </div>
    </div>
  );
};

export default EditorPage;

import React, { useEffect, useRef } from "react";
import { cmtheme, mode } from "../../src/atoms";
import { useRecoilValue } from "recoil";
import ACTIONS from "../actions/Actions";

// CODE MIRROR
import Codemirror from "codemirror";
import "codemirror/lib/codemirror.css";

// theme
import "codemirror/theme/cobalt.css";
import "codemirror/theme/darcula.css";
import "codemirror/theme/eclipse.css";
import "codemirror/theme/idea.css";
import "codemirror/theme/material.css";
import "codemirror/theme/material-ocean.css";
import "codemirror/theme/monokai.css";
import "codemirror/theme/solarized.css";

// modes
import "codemirror/mode/clike/clike";
import "codemirror/mode/javascript/javascript";
import "codemirror/mode/markdown/markdown";
import "codemirror/mode/python/python";
import "codemirror/mode/shell/shell";

// features
import "codemirror/addon/edit/closetag";
import "codemirror/addon/edit/closebrackets";
import "codemirror/addon/scroll/simplescrollbars.css";
import "@codemirror/autocomplete";

// search
import "codemirror/addon/search/search.js";
import "codemirror/addon/search/searchcursor.js";
import "codemirror/addon/search/jump-to-line.js";
import "codemirror/addon/dialog/dialog.js";
import "codemirror/addon/dialog/dialog.css";

// autocomplete
import "codemirror/addon/hint/show-hint";
import "codemirror/addon/hint/show-hint.css";
import "codemirror/addon/hint/javascript-hint";
import "codemirror/addon/hint/anyword-hint";

const Editor = ({ socketRef, roomId, onCodeChange, code }) => {
  const editorRef = useRef(null);
  const editorMode = useRecoilValue(mode);
  const editorTheme = useRecoilValue(cmtheme);

  useEffect(() => {
    if (editorRef.current && code !== undefined) {
      const currentValue = editorRef.current.getValue();

      if (code !== currentValue) {
        const cursor = editorRef.current.getCursor();
        const scrollInfo = editorRef.current.getScrollInfo();

        editorRef.current.setValue(code);

        editorRef.current.setCursor(cursor);
        editorRef.current.scrollTo(scrollInfo.left, scrollInfo.top);
      }
    }
  }, [code]);

  useEffect(() => {
    async function init() {
      if (!editorRef.current) {
        editorRef.current = Codemirror.fromTextArea(
          document.getElementById("realtimeEditor"),
          {
            mode: { name: editorMode },
            theme: editorTheme,
            autoCloseTags: true,
            autoCloseBrackets: true,
            lineNumbers: true,
            extraKeys: {
              "Ctrl-Space": "autocomplete",
            },
            hintOptions: {
              completeSingle: false,
            },
          }
        );

        // Set initial value if code prop exists
        if (code) {
          editorRef.current.setValue(code);
        }

        editorRef.current.on("change", (instance, changes) => {
          const { origin } = changes;
          const currentCode = instance.getValue();
          onCodeChange(currentCode);
          if (origin !== "setValue") {
            socketRef.current.emit(ACTIONS.CODE_CHANGE, {
              roomId,
              code: currentCode,
            });
          }
        });
      }

      if (editorRef.current) {
        editorRef.current.setOption("mode", { name: editorMode });
      }
    }
    init();
  }, [editorMode]);

  useEffect(() => {
    if (socketRef.current) {
      socketRef.current.on(ACTIONS.CODE_CHANGE, ({ code: newCode }) => {
        if (newCode !== null && editorRef.current) {
          editorRef.current.setValue(newCode);
        }
      });
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.off(ACTIONS.CODE_CHANGE);
      }
    };
  }, [socketRef.current]);

  useEffect(() => {
    if (editorRef.current) {
      editorRef.current.setOption("mode", { name: editorMode });
      editorRef.current.setOption("theme", editorTheme);
    }
  }, [editorMode, editorTheme]);

  return <textarea id="realtimeEditor"></textarea>;
};

export default Editor;

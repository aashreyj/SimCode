import React from "react";

const LanguageSelector = ({ lang, changeLanguage }) => {
    return (
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
    );
};

export default LanguageSelector;
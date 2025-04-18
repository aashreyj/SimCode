import React from "react";

const ThemeSelector = ({ theme, setTheme }) => {
    return (
        <label>
            Select Theme:
            <select
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
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
    );
};

export default ThemeSelector;
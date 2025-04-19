import {atom} from "recoil";

// saving previously selected language and theme to local storage
const localStorageEffect = key => ({setSelf, onSet}) => {
    const savedValue = localStorage.getItem(key)
    if (savedValue != null) {
        try {
            setSelf(JSON.parse(savedValue));
        } catch (e) {
            console.error("Failed to parse saved value:", e);
        }
    }
    

    onSet(newValue => {
        //   if (newValue instanceof DefaultValue) {
        //     localStorage.removeItem(key);
        //   } else {
        localStorage.setItem(key, JSON.stringify(newValue));
        //   }
    });
};

export const language = atom({
    key: "language",
    default: "javascript",
    effects_UNSTABLE: [
        localStorageEffect('language'),
    ]
});

export const mode = atom({
    key: "mode",
    default: "javascript",
    effects_UNSTABLE: [
        localStorageEffect('mode'),
    ]
});

export const cmtheme = atom({
    key: "cmtheme",
    default: "monokai",
    effects_UNSTABLE: [
        localStorageEffect('cmtheme'),
    ]
});
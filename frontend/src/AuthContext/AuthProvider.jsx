import React, { useReducer } from "react";
import AuthContext from "./AuthContext";

/**
 * 
 * @param {*} state 
 * @param {*} action
 * @param {str} action.type the type of action to perform "login"|"logout"|"init"
 * @param {str} action.user username (only appiles when action="login")
 * @returns 
 */
function reducer(state, action) {
    switch (action.type) {
        case "login":
            return {
                user: action.user,
                loggedIn: true,
                initialLoginCheck: true,
            };
        case "logout":
            return {
                user: null,
                loggedIn: false,
                initialLoginCheck: true,
            };
        case "init":
        default:
            return {
                user: null,
                loggedIn: false,
                initialLoginCheck: false,
            };
    }
}

/**
 * call setLoginData({ type: "login", user: username }); to login
 * call setLoginData({ type: "logout" }); to logout
 * @returns 
 */
function AuthProvider({ children }) {
    const [loginData, setLoginData] = useReducer(reducer, reducer(null, {type: "init"}));

    function login(username) {
        setLoginData({ type: "login", user: username });
    }

    function logout() {
        setLoginData({ type: "logout" });
    }

    return (
        <AuthContext.Provider
            value={{
                login,
                logout,
                ...loginData
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export default AuthProvider;

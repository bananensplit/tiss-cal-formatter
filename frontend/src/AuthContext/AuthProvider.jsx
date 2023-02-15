import React, { useState } from "react";
import AuthContext from "./AuthContext";

function AuthProvider({ children }) {
    const [userData, setUserData] = useState(null);
    const [loggedIn, setLoggedIn] = useState(false);

    function setUser(userData) {
        if (userData === null) {
            setLoggedIn(false);
            setUserData(null);
        } else {
            setLoggedIn(true);
            setUserData(userData);
        }
    }

    return (
        <AuthContext.Provider
            value={{
                setUser: setUser,
                user: userData,
                loggedIn: loggedIn,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export default AuthProvider;

import React, { useEffect } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import useAuth from "./AuthContext/useAuth";
import useFeedbackMachine from "./FeedbackMachine/useFeedbackMachine";
import "./index.css";
import BufferPage from "./Pages/BufferPage";
import CalendarEdit from "./Pages/CalendarEdit";
import CalendarOverview from "./Pages/CalendarOverview";
import Login from "./Pages/Login";
import Register from "./Pages/Register";

function App({ children }) {
    const { login, logout, user, loggedIn, initialLoginCheck } = useAuth();
    const { setLoading, loading, addSuccess, addError } = useFeedbackMachine();
    const navigate = useNavigate();

    // Check if user is already logged in
    useEffect(() => {
        setLoading(true);
        fetch(`${import.meta.env.BASE_URL.replace(/\/+$/, "")}/api/me`, {
            credentials: "include",
        })
            .then((response) => response.json())
            .then((data) => {
                if (data?.metadata?.error) {
                    console.error(data?.message);
                    logout();
                } else {
                    login(data);
                }
            })
            .catch((error) => console.error(error))
            .finally(() => setLoading(false));
    }, []);

    return (
        <>
            {(initialLoginCheck && (
                <Routes>
                    <Route path="/" element={<Navigate to="/calendars" replace />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route
                        path="/calendars"
                        element={
                            (loggedIn && <CalendarOverview />) || <Navigate to="/login" replace />
                        }
                    />
                    <Route
                        path="/calendars/edit/:token"
                        element={(loggedIn && <CalendarEdit />) || <Navigate to="/login" replace />}
                    />
                    <Route path="*" element={<Navigate to="/" replace />} />{" "}
                </Routes>
            )) || <BufferPage />}
        </>
    );
}

export default App;

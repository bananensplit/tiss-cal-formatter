import { createTheme } from "@mui/material/styles";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import AuthProvider from "./AuthContext/AuthProvider";
import TemplateBanana from "./bananenTempalte/TemplateBanana";
import "./index.css";

const theme = createTheme({
    palette: {
        praimary: {
            main: "#252525",
        },
        secondary: {
            main: "#0066ff",
        },
    },
    typography: {
        fontSize: 12,
        fontFamily: ["Poppins", "Helvetica", "Arial", "sans-serif"].join(","),
        h1: {
            fontSize: "2em",
            fontWeight: 700,
        },
        h2: {
            fontSize: "1.5em",
            fontWeight: 700,
        },
        h3: {
            fontSize: "1.17em",
            fontWeight: 700,
        },
        h4: {
            fontSize: "1em",
            fontWeight: 700,
        },
        h5: {
            fontSize: "0.83em",
            fontWeight: 700,
        },
        h6: {
            fontSize: "0.67em",
            fontWeight: 700,
        },
        code: {
            fontSize: "1em",
            fontFamily: "monospace",
            whiteSpace: "pre",
        }
    },
    components: {
        MuiTextField: {
            defaultProps: {
                size: "small",
            },
        },
        MuiButton: {
            defaultProps: {
                variant: "outlined",
                size: "medium",
            },
        },
        MuiIconButton: {
            defaultProps: {
                size: "small",
            },
        },
        MuiFab: {
            defaultProps: {
                size: "small",
            },
        },
    },
});

ReactDOM.createRoot(document.getElementById("root")).render(
    <React.StrictMode>
        <BrowserRouter basename={import.meta.env.BASE_URL.replace(/\/+$/, "")}>
            <TemplateBanana theme={theme}>
                <AuthProvider>
                    <App />
                </AuthProvider>
            </TemplateBanana>
        </BrowserRouter>
    </React.StrictMode>
);

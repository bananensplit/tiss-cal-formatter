import LinearProgress from "@mui/material/LinearProgress";
import { SnackbarProvider, useSnackbar } from "notistack";
import React, { useState } from "react";
import FeedbackContext from "./FeedbackContext";

function FeedbackMachine({ children }) {
    const [loadingState, setLoadingState] = useState(0);
    const { enqueueSnackbar, closeSnackbar } = useSnackbar();

    function addSuccess(message = "Done!", autoHideDuration = 3000) {
        return enqueueSnackbar(message, {
            variant: "success",
            autoHideDuration: autoHideDuration,
        });
    }

    function addError(
        message = "Something went wrong!",
        autoHideDuration = 3000
    ) {
        return enqueueSnackbar(message, {
            variant: "error",
            autoHideDuration: autoHideDuration,
        });
    }

    function setLoading(state) {
        if (state) {
            setLoadingState(loadingState + 1);
        } else if (loadingState == 1) {
            setTimeout(() => setLoadingState(loadingState - 1), 2000);
        } else if (loadingState == 0) {
            setLoadingState(0);
        } else {
            setLoadingState(loadingState - 1);
        }
    }

    return (
        <FeedbackContext.Provider
            value={{
                setLoading: setLoading,
                loading: loadingState != 0,
                addSuccess: addSuccess,
                addError: addError,
            }}
        >
            <SnackbarProvider>
                <LinearProgress
                    color="secondary"
                    sx={{
                        position: "absolute",
                        height: loadingState != 0 ? "3px" : "0",
                        width: "100%",
                        background: "transparent",
                        transition: "height .3s",
                        zIndex: "1101",
                    }}
                />
                {children}
            </SnackbarProvider>
        </FeedbackContext.Provider>
    );
}

export default FeedbackMachine;

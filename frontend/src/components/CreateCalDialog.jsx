import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Link from "@mui/material/Link";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useEffect, useRef, useState } from "react";
import useFeedbackMachine from "../FeedbackMachine/useFeedbackMachine";

function CreateCalDialog({ open, onClose, reloadCalendars }) {
    const { setLoading, loading, addSuccess, addError } = useFeedbackMachine();
    const [calNameError, setCalNameError] = useState(false);
    const [calUrlError, setCalUrlError] = useState(false);
    const calNameRef = useRef(null);
    const calUrlRef = useRef(null);

    useEffect(() => {
        if (open) {
            setCalNameError(false);
            setCalUrlError(false);
        }
    }, [open]);

    function checkValidity() {
        if (!calNameRef.current.checkValidity()) {
            setCalNameError("Is required!");
        } else setCalNameError(false);

        if (!calUrlRef.current.checkValidity()) {
            if (calUrlRef.current.value === "") setCalUrlError("Is required!");
            setCalUrlError("Has to be a valid URL!");
        } else setCalUrlError(false);

        return calNameRef.current.checkValidity() && calUrlRef.current.checkValidity();
    }

    function createCalendar(event) {
        if (!checkValidity()) return;

        setLoading(true);
        fetch(`${import.meta.env.BASE_URL.replace(/\/+$/, "")}/api/cal/create`, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: calNameRef.current.value,
                url: calUrlRef.current.value,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data?.metadata?.error) {
                    console.error(data?.message);
                    addError(data?.message);
                } else {
                    addSuccess("Calendar created!");
                    reloadCalendars();
                    onClose();
                }
            })
            .catch((error) => {
                console.error(error);
                addError("Something went wrong :(");
            })
            .finally(() => setLoading(false));
    }

    return (
        <Dialog open={open} onClose={() => onClose()}>
            <DialogTitle sx={{ fontSize: "15px" }}>Create new Calendar...</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    <Typography variant="body1" gutterBottom>
                        Please enter the name and URL of your calendar.
                    </Typography>
                    <Typography variant="body1">
                        The calendar name can be anything you want.
                    </Typography>
                    <Typography variant="body1">
                        The calendar URL has to be your TISS-Calendar URL. You can get it from{" "}
                        <Link href="https://tiss.tuwien.ac.at/events/personSchedule.xhtml">
                            here
                        </Link>
                        .
                    </Typography>
                </DialogContentText>
                <TextField
                    sx={{ mt: 2 }}
                    inputRef={calNameRef}
                    id="calname"
                    label="Calendar Name"
                    variant="standard"
                    fullWidth
                    error={calNameError && true}
                    helperText={calNameError && calNameError}
                    required
                />
                <TextField
                    sx={{ mt: 2 }}
                    inputRef={calUrlRef}
                    id="calurl"
                    label="Calendar URL"
                    variant="standard"
                    fullWidth
                    error={calUrlError && true}
                    helperText={calUrlError && calUrlError}
                    required
                    inputProps={{
                        pattern:
                            "^https?:\\/\\/(?:www.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$",
                    }}
                />
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Cancel</Button>
                <Button
                    color="success"
                    variant="contained"
                    onClick={(event) => createCalendar(event)}
                >
                    Submit
                </Button>
            </DialogActions>
        </Dialog>
    );
}

export default CreateCalDialog;

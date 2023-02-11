import DeleteRoundedIcon from "@mui/icons-material/DeleteRounded";
import EditIcon from "@mui/icons-material/Edit";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import useFeedbackMachine from "../FeedbackMachine/useFeedbackMachine";
import CopyElement from "./CopyElement";
import DeleteCalDialog from "./DeleteCalDialog";

function CalendarSummary({ name, url, token, reloadCalendars }) {
    const { setLoading, loading, addError, addSuccess } = useFeedbackMachine();
    const [deleteCalDialog, setDeleteCalDialog] = useState(false);
    const navigate = useNavigate();

    function shortString(string, length = 50) {
        if (string.length > length) {
            return string.substring(0, length) + "...";
        } else {
            return string;
        }
    }

    function deleteCalendar() {
        setLoading(true);
        fetch("http://localhost:8000/tisscal/api/cal/delete/" + token, {
            credentials: "include",
        })
            .then((response) => response.json())
            .then((data) => {
                if (data?.metadata?.error) {
                    console.error(data?.message);
                    addError(data?.message);
                } else {
                    addSuccess(data?.message);
                    reloadCalendars();
                    setDeleteCalDialog(false);
                }
            })
            .catch((error) => {
                console.error(error);
                addError("An error occured!");
            })
            .finally(() => setLoading(false));
    }

    return (
        <Paper sx={{ width: "700px", padding: 2, mt: 1 }}>
            <Box sx={{ display: "flex", alignItems: "center" }}>
                <Typography variant="h4" sx={{ flexGrow: 1 }}>
                    {name || "-"}
                </Typography>
                <IconButton onClick={() => navigate(`/calendars/${token}`)}>
                    <EditIcon />
                </IconButton>
                <IconButton onClick={() => setDeleteCalDialog(true)}>
                    <DeleteRoundedIcon />
                </IconButton>
            </Box>
            <Box>
                <CopyElement copyText={url || ""}>
                    <Typography
                        variant="subtitle"
                        sx={{ fontFamily: "monospace" }}
                    >
                        {(url && shortString(url)) || "-"}
                    </Typography>
                </CopyElement>
            </Box>
            <Box>
                <CopyElement copyText={token || ""}>
                    <Typography
                        variant="subtitle"
                        sx={{ fontFamily: "monospace" }}
                    >
                        {token || "-"}
                    </Typography>
                </CopyElement>
            </Box>
            <DeleteCalDialog
                open={deleteCalDialog}
                onClose={() => setDeleteCalDialog(false)}
                onDelete={deleteCalendar}
                calName={name}
            />
        </Paper>
    );
}

export default CalendarSummary;

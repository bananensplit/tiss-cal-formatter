import AddRoundedIcon from "@mui/icons-material/AddRounded";
import Box from "@mui/material/Box";
import Fab from "@mui/material/Fab";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import CalendarSummary from "../components/CalendarSummary";
import CreateCalDialog from "../components/CreateCalDialog";
import useFeedbackMachine from "../FeedbackMachine/useFeedbackMachine";

function CalendarOverview({}) {
    const { setLoading, loading, addError, addSuccess } = useFeedbackMachine();
    const [calendars, setCalendars] = useState([]);

    const [createCalDialog, setCreateCalDialog] = useState(false);

    useEffect(() => fetchCalendars(), []);

    function fetchCalendars() {
        setLoading(true);
        fetch(`${import.meta.env.BASE_URL.replace(/\/+$/, "")}/api/cal/list`, {
            credentials: "include",
        })
            .then((response) => response.json())
            .then((data) => {
                if (data?.metadata?.error) {
                    console.error(data?.message);
                    addError(data?.message);
                } else {
                    setCalendars(data?.calendars);
                }
            })
            .catch((error) => {
                console.error(error);
                addError("An error occured!");
            })
            .finally(() => setLoading(false));
    }

    return (
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                height: "100%",
                width: "100%",
                padding: 2,
            }}
        >
            {(calendars.length > 0 &&
                calendars.map((calendar) => (
                    <CalendarSummary
                        key={calendar?.token}
                        name={calendar?.name}
                        url={calendar?.url}
                        token={calendar?.token}
                        reloadCalendars={fetchCalendars}
                    />
                ))) || (
                <Box
                    sx={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        height: "100%",
                        width: "100%",
                        padding: 2,
                    }}
                >
                    <Typography variant="h3">No calendars found :I</Typography>
                    <Typography variant="body2">
                        To create a calendar click on the '+' in the bottom right corner.
                    </Typography>
                </Box>
            )}

            <Fab
                color="secondary"
                sx={{ position: "absolute", bottom: 70, right: 16 }}
                onClick={() => setCreateCalDialog(true)}
            >
                <AddRoundedIcon />
            </Fab>

            <CreateCalDialog
                open={createCalDialog}
                onClose={() => setCreateCalDialog(false)}
                reloadCalendars={fetchCalendars}
            />
        </Box>
    );
}

export default CalendarOverview;

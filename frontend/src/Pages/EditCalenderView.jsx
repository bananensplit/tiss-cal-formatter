import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import EventSummary from "../components/EventSummary";
import useFeedbackMachine from "../FeedbackMachine/useFeedbackMachine";
import Grid from "@mui/material/Grid";
import Switch from "@mui/material/Switch";

function EditCalendarView({}) {
    const { token } = useParams();
    const [calendar, setCalendar] = useState(null);
    const { setLoading, loading, addSuccess, addError } = useFeedbackMachine();

    useEffect(() => fetchCalendar(), []);

    function fetchCalendar() {
        setLoading(true);
        fetch(`http://localhost:8000/tisscal/api/cal/data/${token}`, {
            method: "GET",
            credentials: "include",
        })
            .then((response) => response.json())
            .then((data) => {
                if (data?.metadata?.error) {
                    console.error(data?.message);
                    addError(data?.message);
                } else {
                    setCalendar(data);
                }
            })
            .catch((error) => console.log(error))
            .finally(() => setLoading(false));
    }

    function changeEvent() {}

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
            <Typography variant="h4">Edit Calendar</Typography>
            <Typography variant="body1">{calendar?.name}</Typography>
            <Typography variant="body1">{calendar?.url}</Typography>
            <Typography variant="body1">{calendar?.token}</Typography>
            <Box
                sx={{
                    display: "grid",
                    gridTemplateColumns: "1fr repeat(3, 120px) 30px",
                    width: "100%",
                    justifyItems: "center",
                    alignItems: "center",
                    padding: "10px 0",
                }}
            >
                <Typography
                    variant="h4"
                    sx={{ flexGrow: 1, justifySelf: "flex-start" }}
                >
                    Name
                </Typography>
                <Typography variant="h4" sx={{ textAlign: "center" }}>
                    Is LVA
                </Typography>
                <Typography variant="h4" sx={{ textAlign: "center" }}>
                    Will prettify
                </Typography>
                <Typography variant="h4" sx={{ textAlign: "center" }}>
                    Will remove
                </Typography>
            </Box>
            {calendar?.all_events?.map((event) => (
                <>
                    <Divider flexItem/>
                    <EventSummary event={event} />
                </>
            ))}
        </Box>
    );
}

export default EditCalendarView;

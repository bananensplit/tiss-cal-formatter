import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import CopyElement from "../components/CopyElement";
import EventEdit from "../components/EventEdit";
import useFeedbackMachine from "../FeedbackMachine/useFeedbackMachine";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import _ from "lodash";
import TextField from "@mui/material/TextField";

function CalendarEdit({}) {
    const { token } = useParams();
    const { setLoading, loading, addSuccess, addError } = useFeedbackMachine();
    const [calendar, setCalendar] = useState(null);
    const [oldCalendar, setOldCalendar] = useState(null);

    const [defaultSummaryFormat, setDefaultSummaryFormat] = useState("");
    const [defaultLocationFormat, setDefaultLocationFormat] = useState("");
    const [defaultDescriptionFormat, setDefaultDescriptionFormat] = useState("");

    useEffect(() => {
        fetchCalendar();
    }, [token]);

    useEffect(() => {
        setDefaultSummaryFormat(calendar?.default_template?.defaultSummaryFormat || "");
        setDefaultLocationFormat(calendar?.default_template?.defaultLocationFormat || "");
        setDefaultDescriptionFormat(calendar?.default_template?.defaultDescriptionFormat || "");
    }, [calendar]);

    useEffect(
        () =>
            onEditDefault({
                defaultSummaryFormat: defaultSummaryFormat,
                defaultLocationFormat: defaultLocationFormat,
                defaultDescriptionFormat: defaultDescriptionFormat,
            }),
        [defaultSummaryFormat, defaultLocationFormat, defaultDescriptionFormat]
    );

    function fetchCalendar() {
        setLoading(true);
        fetch(`${import.meta.env.BASE_URL.replace(/\/+$/, "")}/api/cal/data/${token}`)
            .then((response) => response.json())
            .then((data) => {
                if (data?.metadata?.error) {
                    console.error(data?.message);
                    addError(data?.message);
                } else {
                    setCalendar(data);
                    setOldCalendar(data);
                }
            })
            .catch((error) => console.error(error))
            .finally(() => setLoading(false));
    }

    function updateCalendar() {
        setLoading(true);
        console.log(calendar);
        fetch(`${import.meta.env.BASE_URL.replace(/\/+$/, "")}/api/cal/data`, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(calendar),
        })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
                if (data?.metadata?.error) {
                    console.error(data?.message);
                    addError(data?.message);
                } else {
                    setCalendar(data);
                    setOldCalendar(data);
                    addSuccess("Calendar updated!");
                }
            })
            .catch((error) => console.error(error))
            .finally(() => setLoading(false));
    }

    function resetChanges() {
        setCalendar(oldCalendar);
    }

    function onEdit(newEvent) {
        setCalendar((oldCalendar) => {
            const newCalendar = { ...oldCalendar };
            newCalendar.all_events = newCalendar.all_events.map((event) => {
                if (event.name === newEvent.name) {
                    return newEvent;
                }
                return event;
            });
            return newCalendar;
        });
    }

    function onEditDefault(newDefault) {
        setCalendar((oldCalendar) => {
            const newCalendar = { ...oldCalendar };
            newCalendar.default_template = newDefault;
            return newCalendar;
        });
    }

    return (
        <Box sx={{ m: 3 }}>
            <Typography variant="h3">{calendar?.name}</Typography>
            <CopyElement copyText={calendar?.url}>
                <Typography variant="subtitle" sx={{ fontFamily: "monospace" }}>
                    {calendar?.url}
                </Typography>
            </CopyElement>
            <br />
            <CopyElement
                copyText={
                    (calendar?.token &&
                        `${window.location.origin}${import.meta.env.BASE_URL.replace(
                            /\/+$/,
                            ""
                        )}/api/cal/${calendar.token}`) ||
                    ""
                }
            >
                <Typography variant="subtitle" sx={{ fontFamily: "monospace" }}>
                    {(calendar?.token &&
                        `${window.location.origin}${import.meta.env.BASE_URL.replace(
                            /\/+$/,
                            ""
                        )}/api/cal/${calendar.token}`) ||
                        ""}
                </Typography>
            </CopyElement>
            <br />
            <Box sx={{ display: "flex", mt: 1, gap: 2 }}>
                <Button
                    onClick={updateCalendar}
                    disabled={loading || _.isEqual(calendar, oldCalendar)}
                    color="success"
                    variant="contained"
                >
                    Save Changes
                </Button>
                <Button
                    onClick={resetChanges}
                    disabled={loading || _.isEqual(calendar, oldCalendar)}
                    color="info"
                >
                    Reset Changes
                </Button>
            </Box>

            <Typography variant="h4" sx={{ mt: 3 }}>
                Default Templates
            </Typography>
            <Box sx={{mt: 2, ml: 3, display: "flex", flexDirection: "column"}}>
                <Typography variant="code" sx={{ fontWeight: "bold" }}>
                {'Description                                           Variable'}
                </Typography>
                <Typography variant="code">{'TISS-Details Link                                     TissDetail'}</Typography>
                <Typography variant="code">{'TISS-Calender original Description                    TissCalDesc'}</Typography>
                <Typography variant="code">{'Room Name (Ausgeschriebener Raum Name)                RoomName'}</Typography>
                <Typography variant="code">{'Room TISS-Raumbelegung Link                           RoomTiss'}</Typography>
                <Typography variant="code">{'Room TUW-Maps Link                                    RoomTuwMap'}</Typography>
                <Typography variant="code">{'Room Gebäude Addresse (z.B. "Getreidemarkt 9")        RoomBuildingAddress'}</Typography>
                <Typography variant="code">{'StartDate formated as (dd-MM-YYYY)                    StartDate'}</Typography>
                <Typography variant="code">{'StartTime formated as (hh:mm)                         StartTime'}</Typography>
                <Typography variant="code">{'EndDate formated as (dd-MM-YYYY)                      EndDate'}</Typography>
                <Typography variant="code">{'EndTime formated as (hh:mm)                           EndTime'}</Typography>
                <Typography variant="code">{'LVA Name (z.B. "Algebra und Diskrete Mathematik für Informatik und Wirtschaftsinformatik")    LvaName'}</Typography>
                <Typography variant="code">{'LVA Typ kurz (z.B. "VO", "UE", "VU", ...)                                                     LvaTypeShort'}</Typography>
                <Typography variant="code">{'LVA Typ lang (z.B. "Vorlesung", "Übung", "Vorlesung mit Übung")                               LvaTypeLong'}</Typography>
                <Typography variant="code">{'LVA ID (z.B. "104.265")                                                                       LvaId'}</Typography>
            </Box>
            <Box
                sx={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gridColumnGap: "20px",
                    m: 3,
                }}
            >
                <TextField
                    label="Default summary format"
                    value={defaultSummaryFormat}
                    onChange={(event) => setDefaultSummaryFormat(event.target.value)}
                    multiline
                    rows={3}
                    fullWidth
                />
                <TextField
                    sx={{ gridRow: "span 2" }}
                    label="Default description format"
                    value={defaultDescriptionFormat}
                    onChange={(event) => setDefaultDescriptionFormat(event.target.value)}
                    multiline
                    rows={10}
                    fullWidth
                />
                <TextField
                    label="Default location format"
                    value={defaultLocationFormat}
                    onChange={(event) => setDefaultLocationFormat(event.target.value)}
                    multiline
                    rows={3}
                    fullWidth
                />
            </Box>

            <Typography variant="h4" sx={{ mt: 3 }}>
                Events
            </Typography>
            <Box sx={{ m: 1 }}>
                <Box
                    sx={{
                        display: "grid",
                        gridTemplateColumns: "1fr repeat(3, 100px) 40px",
                        alignItems: "center",
                        justifyItems: "center",
                        textAlign: "center",
                        fontWeight: "bolder",
                    }}
                >
                    <Typography
                        sx={{
                            justifySelf: "flex-start",
                            fontWeight: "bold",
                            textAlign: "left",
                        }}
                    >
                        Event Name
                    </Typography>
                    <Typography sx={{ fontWeight: "bold" }}>Is LVA</Typography>
                    <Typography sx={{ fontWeight: "bold" }}>Will prettify</Typography>
                    <Typography sx={{ fontWeight: "bold" }}>Will remove</Typography>
                </Box>
                {calendar?.all_events?.map((event) => (
                    <EventEdit
                        key={event.name}
                        eventData={event}
                        onEdit={onEdit}
                        defaultTemplates={calendar.default_template}
                    />
                ))}
            </Box>
        </Box>
    );
}

export default CalendarEdit;

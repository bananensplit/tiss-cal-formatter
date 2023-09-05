import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import CopyElement from "../components/CopyElement";
import EventEdit from "../components/EventEdit";
import useFeedbackMachine from "../FeedbackMachine/useFeedbackMachine";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Link from "@mui/material/Link";
import _ from "lodash";
import TextField from "@mui/material/TextField";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";

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
                    data.all_events = _.sortBy(data.all_events, ["name"]);
                    setCalendar(data);
                    setOldCalendar(data);
                }
            })
            .catch((error) => console.error(error))
            .finally(() => setLoading(false));
    }

    function updateCalendar() {
        setLoading(true);
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
                if (data?.metadata?.error) {
                    console.error(data?.message);
                    addError(data?.message);
                } else {
                    data.all_events = _.sortBy(data.all_events, ["name"]);
                    setCalendar(data);
                    setOldCalendar(data);
                    addSuccess("Calendar updated!");
                }
            })
            .catch((error) => console.error(error))
            .finally(() => setLoading(false));
    }

    function updateCalendarFromSource() {
        setLoading(true);
        fetch(`${import.meta.env.BASE_URL.replace(/\/+$/, "")}/api/cal/update/${token}`, {
            include: "credentials",
        })
            .then((response) => response.json())
            .then((data) => {
                if (data?.metadata?.error) {
                    console.error(data?.message);
                    addError(data?.message);
                } else {
                    data.all_events = _.sortBy(data.all_events, ["name"]);
                    setCalendar(data);
                    setOldCalendar(data);
                    addSuccess("Calendar updated from source!");
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

    function calendarLink() {
        return (
            (calendar?.token &&
                `${window.location.origin}${import.meta.env.BASE_URL.replace(/\/+$/, "")}/api/cal/${
                    calendar.token
                }`) ||
            ""
        );
    }


    return (
        <Box sx={{ m: 3 }}>
            <Typography variant="h1">{calendar?.name}</Typography>
            <CopyElement copyText={calendar?.url}>
                <Typography variant="code">{calendar?.url}</Typography>
            </CopyElement>
            <br />
            <CopyElement copyText={calendarLink()}>
                <Typography variant="code">
                    {calendarLink()}
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
                <Button onClick={updateCalendarFromSource} disabled={loading} color="warning">
                    Reload from Source
                </Button>
            </Box>

            <Typography variant="h3" mt={5} gutterBottom>
                Default Templates
            </Typography>

            <Grid2 container spacing={2}>
                <Grid2 xs={6}>
                    <Typography variant="body1" gutterBottom>
                        These are the default templates for the calendar. They are used when no
                        template is set for a specific event. All templates (default and event
                        specific) are{" "}
                        <Link href="https://jinja.palletsprojects.com/en/3.1.x/">Jinja2</Link>{" "}
                        Templates.{" "}
                        <Link href="https://jinja.palletsprojects.com/en/3.1.x/templates/">
                            Here
                        </Link>{" "}
                        you can find the documentation on how to write this templates.
                    </Typography>

                    <Typography variant="body1" gutterBottom>
                        The basic thing to understand are variables. Variables are written into
                        double curly brackets like this:{" "}
                        <Typography variant="code">{"{{variable}}"}</Typography>. All variables that
                        can be used in the templates are listed below.
                    </Typography>

                    <Typography variant="codeBlock" gutterBottom>
                        <Typography variant="code" fontWeight="bold">
                            {"Description                                           Variable"}
                        </Typography>
                        <br />
                        {
                            "TISS-Details Link (/courseDetails)                    TissCourseDetailLink"
                        }
                        <br />
                        {
                            "TISS-Details Link (/eductaionDetails)                 TissEductionDetailLink"
                        }
                        <br />
                        {"TISS-Calender original Description                    TissCalDesc"}
                        <br />
                        {'Category of the Event ("EXAM"|"COURSE"|"GROUP")       Category'}
                        <br />
                        {"Room Name (Ausgeschriebener Raum Name)                RoomName"}
                        <br />
                        {"Room TISS-Raumbelegung Link                           RoomTiss"}
                        <br />
                        {"Room TUW-Maps Link                                    RoomTuwMap"}
                        <br />
                        {
                            'Room Gebäude Addresse (z.B. "Getreidemarkt 9")        RoomBuildingAddress'
                        }
                        <br />
                        {"StartDate formated as (dd-MM-YYYY)                    StartDate"}
                        <br />
                        {"StartTime formated as (hh:mm)                         StartTime"}
                        <br />
                        {"EndDate formated as (dd-MM-YYYY)                      EndDate"}
                        <br />
                        {"EndTime formated as (hh:mm)                           EndTime"}
                        <br />
                        {'LVA Name (z.B. "Einführung in die Programmierung 2")  LvaName'}
                        <br />
                        {'LVA Typ kurz (z.B. "VO", "UE", "VU", ...)             LvaTypeShort'}
                        <br />
                        {'LVA Typ lang (z.B. "Vorlesung", "Übung", ...)         LvaTypeLong'}
                        <br />
                        {'LVA ID (z.B. "185.A92")                               LvaId'}
                    </Typography>

                    <Typography variant="body1" gutterBottom>
                        Please be careful when editing the templates. If you make a typo writing a
                        variablename the event will not be rendered correctly. There are no sanity-
                        or spell-checks (yet), so potential errors will only be visible when the
                        calendar is rendered.
                    </Typography>
                </Grid2>
                <Grid2 xs={6}>
                    <TextField
                        label="Default summary format"
                        value={defaultSummaryFormat}
                        onChange={(event) => setDefaultSummaryFormat(event.target.value)}
                        multiline
                        rows={3}
                        fullWidth
                        sx={{ mb: 3 }}
                    />
                    <TextField
                        label="Default location format"
                        value={defaultLocationFormat}
                        onChange={(event) => setDefaultLocationFormat(event.target.value)}
                        multiline
                        rows={3}
                        fullWidth
                        sx={{ mb: 3 }}
                    />
                    <TextField
                        label="Default description format"
                        value={defaultDescriptionFormat}
                        onChange={(event) => setDefaultDescriptionFormat(event.target.value)}
                        multiline
                        rows={10}
                        fullWidth
                        sx={{ mb: 3 }}
                    />
                </Grid2>
            </Grid2>

            <Typography variant="h3" mt={5} gutterBottom>
                Events
            </Typography>

            <Typography variant="body1" gutterBottom>
                In this section you can edit the events of the calendar. The events are sorted by
                their name.
            </Typography>

            <Typography variant="body1">
                <b>Will prettify</b>: If this switch is enabled the templates will be applied to
                this event.
            </Typography>
            <Typography variant="body1" gutterBottom>
                <b>Will remove</b>: If this switch is enabled the event will be removed from the
                calendar.
            </Typography>

            <Typography variant="body1" gutterBottom>
                By clicking on the little arrow on the far left you can expand the event to see the
                current event templates and edit them. The templates are the same as the default
                templates, but they are only used for this specific event.
            </Typography>

            <Box sx={{ m: 1 }}>
                <Box
                    sx={{
                        display: "grid",
                        gridTemplateColumns: "1fr repeat(2, 100px) 40px",
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

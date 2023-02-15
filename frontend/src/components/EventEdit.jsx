import ExpandMoreRoundedIcon from "@mui/icons-material/ExpandMoreRounded";
import Box from "@mui/material/Box";
import Collapse from "@mui/material/Collapse";
import Divider from "@mui/material/Divider";
import FormControlLabel from "@mui/material/FormControlLabel";
import IconButton from "@mui/material/IconButton";
import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";

function EventEdit({ eventData, onEdit, defaultTemplates }) {
    const [collapsed, setCollapsed] = useState(true);

    const [is_lva, setIsLva] = useState(eventData?.is_lva || false);
    const [will_remove, setWillRemove] = useState(eventData?.will_remove || false);
    const [will_prettify, setWillPrettify] = useState(eventData?.will_prettify || false);
    const [summaryFormat, setSummaryFormat] = useState(eventData?.summaryFormat);
    const [descriptionFormat, setDescriptionFormat] = useState(eventData?.descriptionFormat);
    const [locationFormat, setLocationFormat] = useState(eventData?.locationFormat);

    useEffect(() => {
        setIsLva(eventData?.is_lva || false);
        setWillRemove(eventData?.will_remove || false);
        setWillPrettify(eventData?.will_prettify || false);
        setSummaryFormat(eventData?.summaryFormat);
        setDescriptionFormat(eventData?.descriptionFormat);
        setLocationFormat(eventData?.locationFormat);
    }, [eventData]);

    useEffect(
        () =>
            onEdit({
                ...eventData,
                summaryFormat: summaryFormat,
                descriptionFormat: descriptionFormat,
                locationFormat: locationFormat,
            }),
        [summaryFormat, descriptionFormat, locationFormat]
    );

    useEffect(
        () =>
            onEdit({
                ...eventData,
                is_lva: is_lva,
                will_remove: will_remove,
                will_prettify: will_prettify,
            }),
        [is_lva, will_remove, will_prettify]
    );

    return (
        <>
            <Divider />
            <Box
                sx={{
                    display: "grid",
                    gridTemplateColumns: "1fr repeat(3, 100px) 40px",
                    alignItems: "center",
                    justifyItems: "center",
                }}
            >
                <Typography variant="body1" sx={{ justifySelf: "flex-start" }}>
                    {eventData?.name || "-"}
                </Typography>
                <Switch
                    checked={is_lva}
                    onChange={(event) => setIsLva(event.target.checked)}
                    disabled
                />
                <Switch
                    checked={will_prettify}
                    onChange={(event) => setWillPrettify(event.target.checked)}
                    disabled={!is_lva}
                />
                <Switch
                    checked={will_remove}
                    onChange={(event) => setWillRemove(event.target.checked)}
                />

                <IconButton onClick={() => setCollapsed(!collapsed)} disabled={!is_lva}>
                    <ExpandMoreRoundedIcon
                        sx={{
                            transform: collapsed ? "rotate(0deg)" : "rotate(180deg)",
                            transition: ".3s",
                        }}
                    />
                </IconButton>
            </Box>
            <Collapse in={!collapsed} timeout="auto" unmountOnExit>
                <Box
                    sx={{
                        display: "grid",
                        gridTemplateColumns: "1fr 1fr",
                        gridColumnGap: "20px",
                        m: 3,
                    }}
                >
                    <Box>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={summaryFormat !== null || false}
                                    onChange={(event) =>
                                        setSummaryFormat(event.target.checked ? "" : null)
                                    }
                                />
                            }
                            label="Use custom summary format"
                        />
                        <TextField
                            label="Summary format"
                            value={
                                summaryFormat !== null
                                    ? summaryFormat
                                    : defaultTemplates?.defaultSummaryFormat
                            }
                            onChange={(event) => setSummaryFormat(event.target.value)}
                            disabled={summaryFormat === null}
                            multiline
                            rows={3}
                            fullWidth
                        />
                    </Box>
                    <Box sx={{ gridRow: "span 2" }}>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={descriptionFormat !== null || false}
                                    onChange={(event) =>
                                        setDescriptionFormat(event.target.checked ? "" : null)
                                    }
                                />
                            }
                            label="Use custom description format"
                        />
                        <TextField
                            label="Description format"
                            value={
                                descriptionFormat !== null
                                    ? descriptionFormat
                                    : defaultTemplates?.defaultDescriptionFormat
                            }
                            onChange={(event) => setDescriptionFormat(event.target.value)}
                            disabled={descriptionFormat === null}
                            multiline
                            rows={10}
                            fullWidth
                        />
                    </Box>
                    <Box>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={locationFormat !== null || false}
                                    onChange={(event) =>
                                        setLocationFormat(event.target.checked ? "" : null)
                                    }
                                />
                            }
                            label="Use custom location format"
                        />
                        <TextField
                            label="Location format"
                            value={
                                locationFormat !== null
                                    ? locationFormat
                                    : defaultTemplates?.defaultLocationFormat
                            }
                            onChange={(event) => setLocationFormat(event.target.value)}
                            disabled={locationFormat === null}
                            multiline
                            rows={3}
                            fullWidth
                        />
                    </Box>
                </Box>
            </Collapse>
        </>
    );
}

export default EventEdit;

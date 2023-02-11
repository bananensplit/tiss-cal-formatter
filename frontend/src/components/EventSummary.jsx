import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import Box from "@mui/material/Box";
import Collapse from "@mui/material/Collapse";
import IconButton from "@mui/material/IconButton";
import ExpandMoreRoundedIcon from '@mui/icons-material/ExpandMoreRounded';

function EventSummary({ event = null }) {
    const [showDetails, setShowDetails] = useState(false);

    return (
        <>
            <Box
                sx={{
                    display: "grid",
                    gridTemplateColumns: "1fr repeat(3, 120px) 30px",
                    width: "100%",
                    justifyItems: "center",
                    alignItems: "center",
                }}
            >
                <Typography
                    variant="body1"
                    sx={{ flexGrow: 1, justifySelf: "flex-start" }}
                >
                    {event?.name || "-"}
                </Typography>
                <Switch checked={event?.is_lva || false} disabled />
                <Switch
                    checked={event?.will_prettify || false}
                    disabled={!event?.is_lva}
                />
                <Switch
                    checked={event?.will_remove || false}
                    disabled={!event?.is_lva}
                />
                <IconButton onClick={() => setShowDetails(!showDetails)}>
                    <ExpandMoreRoundedIcon sx={{
                        transform: showDetails ? "rotate(180deg)" : "rotate(0deg)",
                        transition: ".3s",
                    }}/>
                </IconButton>
            </Box>
            <Collapse component={"div"} in={showDetails}><Typography>UNICORNS AND COOKIES ARE NICE</Typography></Collapse>
        </>
    );
}

export default EventSummary;

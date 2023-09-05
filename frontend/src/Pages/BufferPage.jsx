import { Box, Typography } from "@mui/material";

function BufferPage({}) {
    return (
        <Box
            sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                height: "100%",
            }}
        >
            <Typography sx={{ textAlign: "right", mr: 7 }} variant="h2">
                Tiss Calendar
                <br />
                Formatter 📅
            </Typography>
        </Box>
    );
}

export default BufferPage;

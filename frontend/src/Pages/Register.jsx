import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { useNavigate } from "react-router-dom";

function Register({}) {
    const navigate = useNavigate();
    return (
        <Box
            sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                flexDirection: "column",
                height: "100%",
            }}
        >
            <Typography sx={{ textAlign: "center" }} variant="h2">
                Tiss Calendar Formatter 📅
            </Typography>

            <Typography sx={{ textAlign: "center", mt: 6 }} variant="body1">
                Currently we do not support creating new accounts! Pech gehabt!
                <br />
                If you still want an account you can contact{" "}
                <Link href="mailto:jeremiasz.zrolka@gmail.com">
                    jeremiasz.zrolka@gmail.com
                </Link>
                .
            </Typography>

            <Button sx={{ mt: 6 }} onClick={() => navigate("/login")}>
                Back to Login
            </Button>
        </Box>
    );
}

export default Register;

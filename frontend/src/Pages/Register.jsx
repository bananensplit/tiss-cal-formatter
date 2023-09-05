import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import Link from "@mui/material/Link";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "../AuthContext/useAuth";
import useFeedbackMachine from "../FeedbackMachine/useFeedbackMachine";

function Login({}) {
    const navigate = useNavigate();
    const { setLoading, loading, addSuccess, addError } = useFeedbackMachine();
    const { login, logout, user, loggedIn, initialLoginCheck } = useAuth();

    const [usernameError, setUsernameError] = useState(false);
    const [passwordError, setPasswordError] = useState(false);
    const usernameRef = useRef(null);
    const passwordRef = useRef(null);
    const passwordRetypeRef = useRef(null);

    function submitRegister(event) {
        if (!checkValidity()) return;

        setLoading(true);
        fetch(`${import.meta.env.BASE_URL.replace(/\/+$/, "")}/api/user/create`, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: usernameRef.current.value,
                password: passwordRef.current.value,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data?.metadata?.error) {
                    console.error(data?.message);
                    setUsernameError(data?.message);
                    setPasswordError(data?.message);
                } else {
                    login(data);
                    addSuccess("User created!");
                    navigate("/calendars");
                }
            })
            .catch((error) => console.error(error))
            .finally(() => setLoading(false));
    }

    function checkValidity() {
        let valid = true;

        if (!usernameRef.current.checkValidity()) {
            if (usernameRef.current.value === "") setUsernameError("Is required!");
            else setUsernameError("Needs to pass [.a-zA-Z0-9@_\\-]{8,40}");
            valid = false;
        } else setUsernameError(false);

        if (!passwordRef.current.checkValidity() || !passwordRetypeRef.current.checkValidity()) {
            setPasswordError("Is required!");
            valid = false;
        } else if (passwordRef.current.value !== passwordRetypeRef.current.value) {
            setPasswordError("Passwords do not match!");
            valid = false;
        } else if (
            passwordRef.current.value.length < 10 ||
            passwordRetypeRef.current.value.length < 10
        ) {
            setPasswordError("Password needs to has at least 10 characters!");
            valid = false;
        } else setPasswordError(false);

        return valid;
    }

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

            <Divider orientation="vertical" sx={{ height: "300px" }} />

            <Box
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    alignItems: "center",
                    ml: 6,
                    width: "250px",
                }}
            >
                <TextField
                    inputRef={usernameRef}
                    id="username"
                    label="Username"
                    variant="standard"
                    fullWidth
                    error={usernameError && true}
                    helperText={usernameError && usernameError}
                    required
                    inputProps={{
                        pattern: "[.a-zA-Z0-9@_\\-]{8,40}",
                    }}
                />
                <TextField
                    sx={{ mt: 2 }}
                    inputRef={passwordRef}
                    id="password"
                    label="Password"
                    variant="standard"
                    fullWidth
                    error={passwordError && true}
                    helperText={passwordError && passwordError}
                    required
                    type="password"
                />
                <TextField
                    sx={{ mt: 2 }}
                    inputRef={passwordRetypeRef}
                    id="passwordRetype"
                    label="Retype Password"
                    variant="standard"
                    fullWidth
                    error={passwordError && true}
                    helperText={passwordError && passwordError}
                    required
                    type="password"
                />
                <Button variant="outlined" sx={{ width: "100px", mt: 5 }} onClick={submitRegister}>
                    Register
                </Button>
                <Typography sx={{ mt: 2 }} variant="caption">
                    Already have an account? <Link onClick={() => navigate("/login")}>Login</Link>
                </Typography>
            </Box>
        </Box>
    );
}

export default Login;

import { styled, ThemeProvider } from "@mui/material/styles";
import { SnackbarProvider } from "notistack";
import FeedbackMachine from "../FeedbackMachine/FeedbackMachine";

const footerHeight = 6;
const contentHeight = 100 - footerHeight;
const svgHeight = (8 / 16) * footerHeight;

const CustomFooter = styled("footer")(({ theme }) => ({
    height: footerHeight + "vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#252525",

    "& p": {
        color: "aliceblue",
        fontSize: "larger",
        fontWeight: "bolder",

        marginRight: "15px",
        paddingRight: "20px",
        borderRight: "aliceblue solid 1px",
    },

    "& a": {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",

        margin: "0 10px 0 10px",
    },

    "& svg": {
        height: svgHeight + "vh",
        width: "auto",
        transition: ".2s",
        fill: "#0066ff",
    },

    "& .instagram:hover svg": {
        fill: "#e1306c",
    },

    "& .spotify:hover svg": {
        fill: "#1DB954",
    },

    "& .github:hover svg": {
        fill: "aliceblue",
    },
}));

const CustomMain = styled("main")(({ style, theme }) => ({
    height: contentHeight + "vh",
    overflowX: "auto",
    ...style,
}));

function TemplateBanana({ theme = null, style, children }) {
    return (
        <ThemeProvider theme={theme}>
            <SnackbarProvider
                anchorOrigin={{
                    horizontal: "right",
                    vertical: "bottom",
                }}
            >
                <FeedbackMachine>
                    <CustomMain style={style}>{children}</CustomMain>

                    <CustomFooter>
                        <p>bananensplit.com</p>

                        <a
                            className="instagram"
                            href="https://instagram.com/jeremiasz_z"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 503.84 503.84"
                            >
                                <path
                                    d="M256,49.47c67.27,0,75.23.26,101.8,1.47,24.56,1.12,37.9,5.22,46.78,8.67a78,78,0,0,1,29,18.85,78,78,0,0,1,18.85,29c3.45,8.88,7.55,22.22,8.67,46.78,1.21,26.57,1.47,34.53,1.47,101.8s-.26,75.23-1.47,101.8c-1.12,24.56-5.22,37.9-8.67,46.78a83.51,83.51,0,0,1-47.81,47.81c-8.88,3.45-22.22,7.55-46.78,8.67-26.56,1.21-34.53,1.47-101.8,1.47s-75.24-.26-101.8-1.47c-24.56-1.12-37.9-5.22-46.78-8.67a78,78,0,0,1-29-18.85,78,78,0,0,1-18.85-29c-3.45-8.88-7.55-22.22-8.67-46.78-1.21-26.57-1.47-34.53-1.47-101.8s.26-75.23,1.47-101.8c1.12-24.56,5.22-37.9,8.67-46.78a78,78,0,0,1,18.85-29,78,78,0,0,1,29-18.85c8.88-3.45,22.22-7.55,46.78-8.67,26.57-1.21,34.53-1.47,101.8-1.47m0-45.39c-68.42,0-77,.29-103.87,1.52S107,11.08,91,17.3A123.68,123.68,0,0,0,46.36,46.36,123.68,123.68,0,0,0,17.3,91c-6.22,16-10.48,34.34-11.7,61.15S4.08,187.58,4.08,256s.29,77,1.52,103.87S11.08,405,17.3,421a123.68,123.68,0,0,0,29.06,44.62A123.52,123.52,0,0,0,91,494.69c16,6.23,34.34,10.49,61.15,11.71s35.45,1.52,103.87,1.52,77-.29,103.87-1.52S405,500.92,421,494.69A128.74,128.74,0,0,0,494.69,421c6.23-16,10.49-34.34,11.71-61.15s1.52-35.45,1.52-103.87-.29-77-1.52-103.87S500.92,107,494.69,91a123.52,123.52,0,0,0-29.05-44.62A123.68,123.68,0,0,0,421,17.3c-16-6.22-34.34-10.48-61.15-11.7S324.42,4.08,256,4.08Z"
                                    transform="translate(-4.08 -4.08)"
                                />
                                <path
                                    d="M256,126.64A129.36,129.36,0,1,0,385.36,256,129.35,129.35,0,0,0,256,126.64ZM256,340a84,84,0,1,1,84-84A84,84,0,0,1,256,340Z"
                                    transform="translate(-4.08 -4.08)"
                                />
                                <circle cx="386.4" cy="117.44" r="30.23" />
                            </svg>
                        </a>
                        <a
                            className="spotify"
                            href="https://open.spotify.com/user/jeremiasz.zrolka"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 167.49 167.49"
                            >
                                <path
                                    d="M85,1.28A83.75,83.75,0,1,0,168.77,85,83.75,83.75,0,0,0,85,1.28Zm38.4,120.79a5.22,5.22,0,0,1-7.18,1.74c-19.66-12-44.41-14.74-73.56-8.08a5.22,5.22,0,1,1-2.33-10.17c31.9-7.3,59.27-4.16,81.34,9.33A5.22,5.22,0,0,1,123.43,122.07Zm10.25-22.8a6.54,6.54,0,0,1-9,2.15c-22.51-13.84-56.82-17.84-83.45-9.76a6.53,6.53,0,1,1-3.79-12.5c30.41-9.22,68.22-4.75,94.07,11.13A6.54,6.54,0,0,1,133.68,99.27Zm.88-23.75c-27-16-71.52-17.5-97.29-9.68a7.83,7.83,0,1,1-4.54-15c29.58-9,78.75-7.25,109.83,11.2a7.83,7.83,0,0,1-8,13.47Z"
                                    transform="translate(-1.28 -1.28)"
                                />
                            </svg>
                        </a>
                        <a
                            className="github"
                            href="https://github.com/bananensplit"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 32.58 31.77"
                            >
                                <path d="M16.29,0a16.29,16.29,0,0,0-5.15,31.75c.82.15,1.11-.36,1.11-.79s0-1.41,0-2.77C7.7,29.18,6.74,26,6.74,26a4.36,4.36,0,0,0-1.81-2.39c-1.47-1,.12-1,.12-1a3.43,3.43,0,0,1,2.49,1.68,3.48,3.48,0,0,0,4.74,1.36,3.46,3.46,0,0,1,1-2.18c-3.62-.41-7.42-1.81-7.42-8a6.3,6.3,0,0,1,1.67-4.37,5.94,5.94,0,0,1,.16-4.31s1.37-.44,4.48,1.67a15.41,15.41,0,0,1,8.16,0c3.11-2.11,4.47-1.67,4.47-1.67A5.91,5.91,0,0,1,25,11.07a6.3,6.3,0,0,1,1.67,4.37c0,6.26-3.81,7.63-7.44,8a3.85,3.85,0,0,1,1.11,3c0,2.18,0,3.94,0,4.47s.29.94,1.12.78A16.29,16.29,0,0,0,16.29,0Z" />
                            </svg>
                        </a>
                    </CustomFooter>
                </FeedbackMachine>
            </SnackbarProvider>
        </ThemeProvider>
    );
}

export default TemplateBanana;

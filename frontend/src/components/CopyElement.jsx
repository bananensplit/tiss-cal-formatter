import { useState } from "react";
import IconButton from "@mui/material/IconButton";
import ContentCopyRoundedIcon from "@mui/icons-material/ContentCopyRounded";

function CopyElement({ copyText, children }) {
    const [isCopied, setIsCopied] = useState(false);

    function copyToClipboard(event) {
        navigator.clipboard.writeText(copyText);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 4000);
    }

    return [
        children,
        <IconButton
            color={isCopied ? "success" : "secondary"}
            disabled={!(copyText && true)}
            onClick={copyToClipboard}
        >
            <ContentCopyRoundedIcon />
        </IconButton>,
    ];
}

export default CopyElement;
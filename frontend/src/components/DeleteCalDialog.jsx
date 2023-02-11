import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Typography from "@mui/material/Typography";

function DeleteCalDialog({ open, onClose, onDelete, calName }) {
    return (
        <Dialog open={open} onClose={onClose}>
            <DialogTitle sx={{ fontSize: "15px" }}>Delete Calendar</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    Are you sure you want to delete this calendar?
                </DialogContentText>
                <Typography variant="h4">{calName}</Typography>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Cancel</Button>
                <Button color="error" variant="contained" onClick={onDelete}>
                    Delete
                </Button>
            </DialogActions>
        </Dialog>
    );
}

export default DeleteCalDialog;

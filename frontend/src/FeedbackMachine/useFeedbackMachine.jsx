import { useContext } from "react";
import FeedbackContext from "./FeedbackContext";

export default function useFeedbackMachine() {
    return useContext(FeedbackContext);
}
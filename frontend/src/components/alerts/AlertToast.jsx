import { Alert, Snackbar } from "@mui/material";

import { useAlerts } from "../../context/AlertsContext";

function severityToMuiColor(severity) {
    switch (severity) {
        case "CRITICAL":
            return "error";
        case "WARNING":
            return "warning";
        default:
            return "info";
    }
}

export default function AlertToast() {
    const { toast, dismissToast } = useAlerts();

    return (
        <Snackbar
            open={Boolean(toast)}
            autoHideDuration={toast?.severity === "CRITICAL" ? 10000 : 6000}
            onClose={dismissToast}
            anchorOrigin={{ vertical: "top", horizontal: "right" }}
        >
            {toast ? (
                <Alert
                    onClose={dismissToast}
                    severity={severityToMuiColor(toast.severity)}
                    variant="filled"
                    sx={{ width: "100%", maxWidth: 420 }}
                >
                    <strong>{toast.event_type.replaceAll("_", " ")}</strong>
                    {" — "}
                    {toast.message}
                    {" "}
                    <span style={{ opacity: 0.85 }}>
                        ({toast.camera_id})
                    </span>
                </Alert>
            ) : (
                <span />
            )}
        </Snackbar>
    );
}

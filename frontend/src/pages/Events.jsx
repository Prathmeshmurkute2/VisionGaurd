import { useEffect, useState } from "react";
import {
    Alert,
    Chip,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
} from "@mui/material";

import { getEvents } from "../api/eventApi";
import { useAlerts } from "../context/AlertsContext";

function severityColor(severity) {
    switch (severity) {
        case "CRITICAL":
            return "error";
        case "WARNING":
            return "warning";
        default:
            return "info";
    }
}

export default function Events() {
    const { alerts } = useAlerts();
    const [historicalEvents, setHistoricalEvents] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let cancelled = false;

        getEvents({ page: 1, size: 50 })
            .then((response) => {
                if (!cancelled) {
                    setHistoricalEvents(response.data ?? []);
                }
            })
            .catch((err) => {
                if (!cancelled) {
                    setError(err);
                }
            })
            .finally(() => {
                if (!cancelled) {
                    setIsLoading(false);
                }
            });

        return () => {
            cancelled = true;
        };
    }, []);

    // Merge live alerts (from the WebSocket) on top of the page we
    // fetched from the API, de-duplicating by id.
    const liveIds = new Set(alerts.map((event) => event.id));

    const combinedEvents = [
        ...alerts,
        ...historicalEvents
            .map((event) => ({
                id: event.event_id ?? event.id,
                event_type: event.event_type,
                camera_id: event.camera_id,
                severity: event.severity,
                message: event.message,
                timestamp: event.timestamp,
            }))
            .filter((event) => !liveIds.has(event.id)),
    ];

    return (
        <TableContainer component={Paper} sx={{ borderRadius: 3 }}>
            <Typography variant="h6" sx={{ p: 2, fontWeight: "bold" }}>
                Events
            </Typography>

            {isLoading && (
                <Typography sx={{ px: 2, pb: 2 }}>Loading events…</Typography>
            )}

            {error && (
                <Alert severity="error" sx={{ mx: 2, mb: 2 }}>
                    Could not load events.
                </Alert>
            )}

            {!isLoading && !error && combinedEvents.length === 0 && (
                <Typography sx={{ px: 2, pb: 2, color: "text.secondary" }}>
                    No events yet. Once the camera is running, detected
                    activity will show up here.
                </Typography>
            )}

            {combinedEvents.length > 0 && (
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell><b>ID</b></TableCell>
                            <TableCell><b>Camera</b></TableCell>
                            <TableCell><b>Event</b></TableCell>
                            <TableCell><b>Message</b></TableCell>
                            <TableCell><b>Severity</b></TableCell>
                            <TableCell><b>Time</b></TableCell>
                        </TableRow>
                    </TableHead>

                    <TableBody>
                        {combinedEvents.map((event) => (
                            <TableRow key={event.id} hover>
                                <TableCell>{event.id}</TableCell>
                                <TableCell>{event.camera_id}</TableCell>
                                <TableCell>
                                    {event.event_type?.replaceAll("_", " ")}
                                </TableCell>
                                <TableCell>{event.message}</TableCell>
                                <TableCell>
                                    <Chip
                                        label={event.severity}
                                        color={severityColor(event.severity)}
                                        size="small"
                                    />
                                </TableCell>
                                <TableCell>
                                    {new Date(event.timestamp).toLocaleString()}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            )}
        </TableContainer>
    );
}

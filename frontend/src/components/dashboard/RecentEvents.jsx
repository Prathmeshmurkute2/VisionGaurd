import {
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
    Chip,
} from "@mui/material";

function getSeverityColor(severity) {
    switch (severity?.toLowerCase()) {
        case "high":
            return "error";
        case "medium":
            return "warning";
        case "low":
            return "success";
        default:
            return "default";
    }
}

export default function RecentEvents({ events }) {
    return (
        <TableContainer
            component={Paper}
            sx={{ mt: 4, borderRadius: 3 }}
        >
            <Typography
                variant="h6"
                sx={{ p: 2, fontWeight: "bold" }}
            >
                Recent Events
            </Typography>

            <Table>

                <TableHead>
                    <TableRow>
                        <TableCell><b>ID</b></TableCell>
                        <TableCell><b>Camera</b></TableCell>
                        <TableCell><b>Event</b></TableCell>
                        <TableCell><b>Severity</b></TableCell>
                        <TableCell><b>Time</b></TableCell>
                    </TableRow>
                </TableHead>

                <TableBody>

                    {events.map((event) => (

                        <TableRow key={event.id} hover>

                            <TableCell>{event.id}</TableCell>

                            <TableCell>{event.camera_id}</TableCell>

                            <TableCell>{event.event_type}</TableCell>

                            <TableCell>
                                <Chip
                                    label={event.severity}
                                    color={getSeverityColor(event.severity)}
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

        </TableContainer>
    );
}
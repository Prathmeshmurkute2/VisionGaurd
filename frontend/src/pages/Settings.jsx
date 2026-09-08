import { useEffect, useRef, useState } from "react";
import {
    Alert,
    Box,
    Button,
    Chip,
    Paper,
    Stack,
    Typography,
} from "@mui/material";

import { getZones, createZone, deleteZone } from "../api/zoneApi";

const API_URL = import.meta.env.VITE_API_BASE_URL;
const CAMERA_ID = "Gate-1"; // matches backend's DEFAULT_CAMERA_ID (single-camera setup for now)

export default function Settings() {
    const containerRef = useRef(null);

    const [streamKey] = useState(() => Date.now());
    const [activeZone, setActiveZone] = useState(null);
    const [draftPoints, setDraftPoints] = useState([]);
    const [isDrawing, setIsDrawing] = useState(false);
    const [error, setError] = useState(null);
    const [statusMessage, setStatusMessage] = useState(null);

    useEffect(() => {
        async function loadActiveZone() {
            try {
                const zones = await getZones(CAMERA_ID);
                const active = zones.find((z) => z.is_active) ?? null;
                setActiveZone(active);
            } catch {
                setError("Could not load the current zone.");
            }
        }

        loadActiveZone();
    }, []);

    function handleContainerClick(event) {
        if (!isDrawing) return;

        const rect = containerRef.current.getBoundingClientRect();

        const x = (event.clientX - rect.left) / rect.width;
        const y = (event.clientY - rect.top) / rect.height;

        setDraftPoints((points) => [...points, { x, y }]);
    }

    function startDrawing() {
        setError(null);
        setStatusMessage(null);
        setDraftPoints([]);
        setIsDrawing(true);
    }

    function cancelDrawing() {
        setIsDrawing(false);
        setDraftPoints([]);
    }

    function undoLastPoint() {
        setDraftPoints((points) => points.slice(0, -1));
    }

    async function saveZone() {
        if (draftPoints.length < 3) {
            setError("Click at least 3 points to draw a zone.");
            return;
        }

        try {
            const zone = await createZone({
                cameraId: CAMERA_ID,
                name: "Restricted Zone",
                points: draftPoints,
            });

            setActiveZone(zone);
            setIsDrawing(false);
            setDraftPoints([]);
            setStatusMessage(
                "Zone saved — applied to the live camera immediately."
            );
        } catch (err) {
            const message =
                err.response?.data?.message ??
                "Could not save the zone.";
            setError(message);
        }
    }

    async function removeActiveZone() {
        if (!activeZone) return;

        try {
            await deleteZone(activeZone.id);
            setActiveZone(null);
            setStatusMessage("Zone removed.");
        } catch {
            setError("Could not remove the zone.");
        }
    }

    // Points currently shown on the overlay: the zone being drawn
    // if in drawing mode, otherwise the saved active zone.
    const displayPoints = isDrawing ? draftPoints : (activeZone?.points ?? []);

    const polygonAttr = displayPoints
        .map((p) => `${p.x * 100},${p.y * 100}`)
        .join(" ");

    return (
        <Box>
            <Typography variant="h5" fontWeight="bold" mb={3}>
                Settings — Intrusion Zone
            </Typography>

            <Paper elevation={3} sx={{ p: 3, borderRadius: 3, maxWidth: 900 }}>

                <Stack direction="row" spacing={2} alignItems="center" mb={2}>
                    <Typography variant="body1">
                        {activeZone
                            ? `Active zone: "${activeZone.name}" (${activeZone.points.length} points)`
                            : "No restricted zone configured yet."}
                    </Typography>

                    {activeZone && !isDrawing && (
                        <Chip label="Live" color="success" size="small" />
                    )}
                </Stack>

                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}

                {statusMessage && !error && (
                    <Alert severity="success" sx={{ mb: 2 }}>
                        {statusMessage}
                    </Alert>
                )}

                <Typography variant="body2" color="text.secondary" mb={2}>
                    {isDrawing
                        ? "Click on the video to add points tracing the restricted area (at least 3). Then save."
                        : "Draw a zone to get intrusion alerts when someone enters this area. The camera should be running so you can see the live feed below."}
                </Typography>

                <Box
                    ref={containerRef}
                    onClick={handleContainerClick}
                    sx={{
                        position: "relative",
                        width: "100%",
                        borderRadius: 2,
                        overflow: "hidden",
                        cursor: isDrawing ? "crosshair" : "default",
                        bgcolor: "#111",
                    }}
                >
                    <img
                        key={streamKey}
                        src={`${API_URL}/camera/stream?t=${streamKey}`}
                        alt="Live camera feed"
                        style={{
                            width: "100%",
                            display: "block",
                        }}
                        onError={(e) => {
                            e.target.style.display = "none";
                        }}
                    />

                    <svg
                        viewBox="0 0 100 100"
                        preserveAspectRatio="none"
                        style={{
                            position: "absolute",
                            top: 0,
                            left: 0,
                            width: "100%",
                            height: "100%",
                            pointerEvents: "none",
                        }}
                    >
                        {displayPoints.length >= 2 && (
                            <polygon
                                points={polygonAttr}
                                fill="rgba(239, 68, 68, 0.25)"
                                stroke="#EF4444"
                                strokeWidth="0.4"
                            />
                        )}

                        {displayPoints.map((p, i) => (
                            <circle
                                key={i}
                                cx={p.x * 100}
                                cy={p.y * 100}
                                r="0.8"
                                fill="#EF4444"
                            />
                        ))}
                    </svg>
                </Box>

                <Stack direction="row" spacing={2} sx={{ mt: 3 }}>

                    {!isDrawing && (
                        <Button variant="contained" onClick={startDrawing}>
                            {activeZone ? "Redraw Zone" : "Draw Zone"}
                        </Button>
                    )}

                    {isDrawing && (
                        <>
                            <Button
                                variant="contained"
                                color="success"
                                onClick={saveZone}
                                disabled={draftPoints.length < 3}
                            >
                                Save Zone ({draftPoints.length} points)
                            </Button>

                            <Button variant="outlined" onClick={undoLastPoint}>
                                Undo Last Point
                            </Button>

                            <Button variant="outlined" color="error" onClick={cancelDrawing}>
                                Cancel
                            </Button>
                        </>
                    )}

                    {!isDrawing && activeZone && (
                        <Button variant="outlined" color="error" onClick={removeActiveZone}>
                            Remove Zone
                        </Button>
                    )}

                </Stack>

            </Paper>
        </Box>
    );
}

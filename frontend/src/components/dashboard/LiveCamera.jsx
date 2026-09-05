import { useEffect, useState } from "react";
import {
    Paper,
    Typography,
    Button,
    Box,
} from "@mui/material";

const API_URL = "http://127.0.0.1:8000";

export default function LiveCamera() {

    const [running, setRunning] = useState(false);
    const [loading, setLoading] = useState(false);
    const [streamKey, setStreamKey] = useState(null);


    // --------------------------------
    // Check backend camera status
    // --------------------------------

    useEffect(() => {

        const checkCameraStatus = async () => {

            try {

                const response = await fetch(
                    `${API_URL}/camera/status`
                );

                if (!response.ok) {
                    throw new Error(
                        "Failed to fetch camera status"
                    );
                }

                const data = await response.json();

                setRunning(data.running);

                // If backend is already running,
                // create a fresh stream URL.
                if (data.running) {
                    setStreamKey(Date.now());
                }

            } catch (error) {

                console.error(
                    "❌ Failed to get camera status:",
                    error
                );

            }
        };

        checkCameraStatus();

    }, []);


    // --------------------------------
    // Start camera
    // --------------------------------

    const startCamera = async () => {

        setLoading(true);

        try {

            const response = await fetch(
                `${API_URL}/camera/start`,
                {
                    method: "POST",
                }
            );

            if (!response.ok) {
                throw new Error(
                    "Failed to start camera"
                );
            }

            setRunning(true);

            // Create a fresh stream URL
            setStreamKey(Date.now());

        } catch (error) {

            console.error(
                "❌ Failed to start camera:",
                error
            );

        } finally {

            setLoading(false);
        }
    };


    // --------------------------------
    // Stop camera
    // --------------------------------

    const stopCamera = async () => {

        setLoading(true);

        try {

            const response = await fetch(
                `${API_URL}/camera/stop`,
                {
                    method: "POST",
                }
            );

            if (!response.ok) {
                throw new Error(
                    "Failed to stop camera"
                );
            }

            setRunning(false);

            // Remove old stream
            setStreamKey(null);

        } catch (error) {

            console.error(
                "❌ Failed to stop camera:",
                error
            );

        } finally {

            setLoading(false);
        }
    };


    return (
        <Paper
            elevation={3}
            sx={{
                mt: 4,
                p: 2,
                borderRadius: 3,
            }}
        >

            <Typography
                variant="h6"
                fontWeight="bold"
                mb={2}
            >
                Live Camera Feed
            </Typography>


            {/* -------------------------------- */}
            {/* Camera controls */}
            {/* -------------------------------- */}

            <Box
                sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 2,
                    mb: 2,
                }}
            >

                <Button
                    variant="contained"
                    color="success"
                    onClick={startCamera}
                    disabled={running || loading}
                >
                    ▶ Start Camera
                </Button>


                <Button
                    variant="contained"
                    color="error"
                    onClick={stopCamera}
                    disabled={!running || loading}
                >
                    ■ Stop Camera
                </Button>


                <Typography
                    fontWeight="bold"
                    sx={{ ml: 1 }}
                >
                    {running
                        ? "🟢 Camera Running"
                        : "🔴 Camera Stopped"}
                </Typography>

            </Box>


            {/* -------------------------------- */}
            {/* Camera stream */}
            {/* -------------------------------- */}

            {running && streamKey ? (

                <img
                    key={streamKey}
                    src={`${API_URL}/camera/stream?t=${streamKey}`}
                    alt="Live Camera"
                    style={{
                        width: "100%",
                        borderRadius: "12px",
                    }}
                />

            ) : (

                <Box
                    sx={{
                        height: 400,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        backgroundColor: "#111",
                        borderRadius: "12px",
                    }}
                >

                    <Typography color="white">
                        🔴 Camera is stopped
                    </Typography>

                </Box>

            )}

        </Paper>
    );
}
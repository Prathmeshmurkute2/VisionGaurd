import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    Alert,
    Box,
    Button,
    Paper,
    TextField,
    Typography,
} from "@mui/material";

import { useAuth } from "../context/AuthContext";

export default function Login() {
    const { login } = useAuth();
    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    async function handleSubmit(event) {
        event.preventDefault();

        setError(null);
        setIsSubmitting(true);

        try {
            await login({ username, password });
            navigate("/", { replace: true });
        } catch (err) {
            const message =
                err.response?.data?.message ??
                "Invalid username or password.";

            setError(message);
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <Box
            sx={{
                minHeight: "100vh",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                bgcolor: "#F5F7FA",
            }}
        >
            <Paper
                elevation={3}
                component="form"
                onSubmit={handleSubmit}
                sx={{
                    p: 4,
                    width: 360,
                    borderRadius: 3,
                }}
            >
                <Typography variant="h5" fontWeight="bold" mb={1}>
                    Sign in
                </Typography>

                <Typography variant="body2" color="text.secondary" mb={3}>
                    Intelligent Video Surveillance
                </Typography>

                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}

                <TextField
                    label="Username"
                    fullWidth
                    margin="normal"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    autoFocus
                    required
                />

                <TextField
                    label="Password"
                    type="password"
                    fullWidth
                    margin="normal"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />

                <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    disabled={isSubmitting}
                    sx={{ mt: 3 }}
                >
                    {isSubmitting ? "Signing in…" : "Sign in"}
                </Button>
            </Paper>
        </Box>
    );
}

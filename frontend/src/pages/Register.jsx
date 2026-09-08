import { useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import {
    Alert,
    Box,
    Button,
    Link,
    Paper,
    TextField,
    Typography,
} from "@mui/material";

import { register as registerRequest } from "../api/authApi";
import { useAuth } from "../context/AuthContext";

export default function Register() {
    const { login } = useAuth();
    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    async function handleSubmit(event) {
        event.preventDefault();

        setError(null);

        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        if (password.length < 8) {
            setError("Password must be at least 8 characters.");
            return;
        }

        setIsSubmitting(true);

        try {
            await registerRequest({ username, email, password });

            // Registration succeeded - log the user straight in
            // rather than making them re-enter credentials.
            await login({ username, password });

            navigate("/", { replace: true });
        } catch (err) {
            const message =
                err.response?.data?.message ??
                "Could not create account. Please try again.";

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
                    width: 380,
                    borderRadius: 3,
                }}
            >
                <Typography variant="h5" fontWeight="bold" mb={1}>
                    Create account
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
                    label="Email"
                    type="email"
                    fullWidth
                    margin="normal"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />

                <TextField
                    label="Password"
                    type="password"
                    fullWidth
                    margin="normal"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    helperText="At least 8 characters"
                    required
                />

                <TextField
                    label="Confirm password"
                    type="password"
                    fullWidth
                    margin="normal"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                />

                <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    disabled={isSubmitting}
                    sx={{ mt: 3 }}
                >
                    {isSubmitting ? "Creating account…" : "Create account"}
                </Button>

                <Typography variant="body2" align="center" sx={{ mt: 2 }}>
                    Already have an account?{" "}
                    <Link component={RouterLink} to="/login">
                        Sign in
                    </Link>
                </Typography>
            </Paper>
        </Box>
    );
}

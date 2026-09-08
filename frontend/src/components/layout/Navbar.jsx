import NotificationsIcon from "@mui/icons-material/Notifications";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import VolumeOffIcon from "@mui/icons-material/VolumeOff";
import LogoutIcon from "@mui/icons-material/Logout";
import {
    AppBar,
    Avatar,
    Badge,
    Box,
    IconButton,
    Toolbar,
    Tooltip,
    Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

import { useAlerts } from "../../context/AlertsContext";
import { useAuth } from "../../context/AuthContext";

const drawerWidth = 240;

export default function Navbar() {
    const { unreadCount, clearUnread, soundEnabled, toggleSound } = useAlerts();
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    function handleLogout() {
        logout();
        navigate("/login", { replace: true });
    }

    return (
        <AppBar
            position="fixed"
            elevation={1}
            sx={{
                width: `calc(100% - ${drawerWidth}px)`,
                ml: `${drawerWidth}px`,
                bgcolor: "#FFFFFF",
                color: "#1E293B",
            }}
        >
            <Toolbar>

                <Typography
                    variant="h6"
                    fontWeight="bold"
                    sx={{ flexGrow: 1 }}
                >
                    Intelligent Video Surveillance
                </Typography>

                <Tooltip title={soundEnabled ? "Mute alert sound" : "Unmute alert sound"}>
                    <IconButton color="inherit" onClick={toggleSound}>
                        {soundEnabled ? <VolumeUpIcon /> : <VolumeOffIcon />}
                    </IconButton>
                </Tooltip>

                <IconButton color="inherit" onClick={clearUnread}>
                    <Badge
                        badgeContent={unreadCount}
                        color="error"
                    >
                        <NotificationsIcon />
                    </Badge>
                </IconButton>

                <Box
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        ml: 2,
                    }}
                >
                    <Avatar
                        sx={{
                            bgcolor: "#2563EB",
                        }}
                    >
                        {(user?.username?.[0] ?? "A").toUpperCase()}
                    </Avatar>

                   <Typography
                        sx={{
                            ml: 1,
                            fontWeight: 500,
                        }}
                    >
                        {user?.username ?? "Admin"}
                    </Typography>

                    <Tooltip title="Sign out">
                        <IconButton
                            color="inherit"
                            onClick={handleLogout}
                            sx={{ ml: 1 }}
                        >
                            <LogoutIcon fontSize="small" />
                        </IconButton>
                    </Tooltip>
                </Box>

            </Toolbar>
        </AppBar>
    );
}
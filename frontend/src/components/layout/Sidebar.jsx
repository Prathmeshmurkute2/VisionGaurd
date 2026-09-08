import {
    Analytics,
    Dashboard,
    Logout,
    Settings,
    Videocam,
    Warning,
} from "@mui/icons-material";

import {
    Box,
    Drawer,
    List,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Toolbar,
    Typography,
} from "@mui/material";

import { Link, useLocation } from "react-router-dom";

const drawerWidth = 240;

const menuItems = [
    {
        text: "Dashboard",
        icon: <Dashboard />,
        path: "/",
    },
    {
        text: "Events",
        icon: <Warning />,
        path: "/events",
    },
    {
        text: "Cameras",
        icon: <Videocam />,
        path: "/cameras",
    },
    {
        text: "Analytics",
        icon: <Analytics />,
        path: "/analytics",
    },
    {
        text: "Settings",
        icon: <Settings />,
        path: "/settings",
    },
];

export default function Sidebar() {
    const location = useLocation();

    return (
        <Drawer
            variant="permanent"
            sx={{
                width: drawerWidth,
                flexShrink: 0,
                "& .MuiDrawer-paper": {
                    width: drawerWidth,
                    boxSizing: "border-box",
                    bgcolor: "#1E293B",
                    color: "white",
                    borderRight: "none",
                },
            }}
        >
            <Toolbar />

            {/* Logo */}
            <Box
                sx={{
                    textAlign: "center",
                    py: 3,
                }}
            >
                <Typography
                    variant="h5"
                    fontWeight="bold"
                    color="#3B82F6"
                >
                    IVS
                </Typography>

                <Typography
                    variant="body2"
                    sx={{
                        color: "#CBD5E1",
                        mt: 0.5,
                    }}
                >
                    Intelligent Video Surveillance
                </Typography>
            </Box>

            {/* Navigation */}
            <List sx={{ px: 1 }}>
                {menuItems.map((item) => (
                    <ListItemButton
                        key={item.text}
                        component={Link}
                        to={item.path}
                        selected={location.pathname === item.path}
                        sx={{
                            color: "white",
                            borderRadius: 2,
                            mb: 1,

                            "&.Mui-selected": {
                                bgcolor: "#2563EB",
                            },

                            "&.Mui-selected:hover": {
                                bgcolor: "#1D4ED8",
                            },

                            "&:hover": {
                                bgcolor: "#334155",
                            },
                        }}
                    >
                        <ListItemIcon
                            sx={{
                                color: "inherit",
                                minWidth: 40,
                            }}
                        >
                            {item.icon}
                        </ListItemIcon>

                        <ListItemText primary={item.text} />
                    </ListItemButton>
                ))}
            </List>

            {/* Logout Button */}
            <Box sx={{ flexGrow: 1 }} />

            <List sx={{ px: 1, mb: 2 }}>
                <ListItemButton
                    sx={{
                        color: "white",
                        borderRadius: 2,

                        "&:hover": {
                            bgcolor: "#334155",
                        },
                    }}
                >
                    <ListItemIcon
                        sx={{
                            color: "inherit",
                            minWidth: 40,
                        }}
                    >
                        <Logout />
                    </ListItemIcon>

                    <ListItemText primary="Logout" />
                </ListItemButton>
            </List>
        </Drawer>
    );
}
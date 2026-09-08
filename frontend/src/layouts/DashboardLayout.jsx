import { Box, Toolbar } from "@mui/material";
import { Outlet } from "react-router-dom";

import Navbar from "../components/layout/Navbar";
import Sidebar from "../components/layout/Sidebar";
import AlertToast from "../components/alerts/AlertToast";
import { AlertsProvider } from "../context/AlertsContext";

const drawerWidth = 240;

export default function DashboardLayout() {
    return (
        <AlertsProvider>
            <Box sx={{ display: "flex" }}>

                <Navbar />

                <Sidebar />

                <Box
                    component="main"
                    sx={{
                        flexGrow: 1,
                        bgcolor: "#F5F7FA",
                        minHeight: "100vh",
                        width: `calc(100% - ${drawerWidth}px)`,
                        p: 3,
                    }}
                >
                    <Toolbar />

                    <Outlet />
                </Box>

                <AlertToast />

            </Box>
        </AlertsProvider>
    );
}
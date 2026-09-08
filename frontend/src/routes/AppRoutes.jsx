import { BrowserRouter, Routes, Route } from "react-router-dom";

import DashboardLayout from "../layouts/DashboardLayout";

import Dashboard from "../pages/Dashboard.jsx";
import Events from "../pages/Events.jsx";
import Cameras from "../pages/Cameras.jsx";
import Login from "../pages/Login.jsx";
import Settings from "../pages/Settings.jsx";
import Analytics from "../pages/Analytics.jsx";
import Register from "../pages/Register.jsx";

import { AuthProvider } from "../context/AuthContext";
import RequireAuth from "../components/auth/RequireAuth";

export default function AppRoutes() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Routes>

                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route
                        element={
                            <RequireAuth>
                                <DashboardLayout />
                            </RequireAuth>
                        }
                    >

                        <Route path="/" element={<Dashboard />} />

                        <Route path="/events" element={<Events />} />

                        <Route path="/cameras" element={<Cameras />} />

                        <Route path="/settings" element={<Settings />} />

                        <Route
                            path="/analytics" element={<Analytics />}
                        />
                    </Route>

                </Routes>
            </AuthProvider>
        </BrowserRouter>
    );
}
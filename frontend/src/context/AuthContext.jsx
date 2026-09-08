import { createContext, useContext, useEffect, useState } from "react";

import { login as loginRequest, getMe } from "../api/authApi";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem("access_token");

        if (!token) {
            setIsLoading(false);
            return;
        }

        getMe()
            .then((currentUser) => setUser(currentUser))
            .catch(() => localStorage.removeItem("access_token"))
            .finally(() => setIsLoading(false));
    }, []);

    async function login(credentials) {
        const { access_token } = await loginRequest(credentials);

        localStorage.setItem("access_token", access_token);

        const currentUser = await getMe();
        setUser(currentUser);

        return currentUser;
    }

    function logout() {
        localStorage.removeItem("access_token");
        setUser(null);
    }

    return (
        <AuthContext.Provider
            value={{
                user,
                isAuthenticated: Boolean(user),
                isLoading,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }

    return context;
}

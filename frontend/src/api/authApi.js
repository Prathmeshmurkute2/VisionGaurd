import api from "./axios";

export async function login({ username, password }) {
    const response = await api.post("/auth/login", { username, password });

    // ApiResponse wrapper: { success, message, data: { access_token, token_type } }
    return response.data.data;
}

export async function register({ username, email, password }) {
    const response = await api.post("/auth/register", {
        username,
        email,
        password,
    });

    return response.data.data;
}

export async function getMe() {
    const response = await api.get("/auth/me");

    return response.data.data;
}

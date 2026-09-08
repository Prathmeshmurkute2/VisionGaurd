import api from "./axios";

export async function getDashboard() {
    const response = await api.get("/dashboard/");

    return response.data;
}
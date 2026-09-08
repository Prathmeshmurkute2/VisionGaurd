import api from "./axios";

export async function getEvents({ page = 1, size = 20 } = {}) {
    const response = await api.get("/events/", {
        params: { page, size },
    });

    return response.data;
}

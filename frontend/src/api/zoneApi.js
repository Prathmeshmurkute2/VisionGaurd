import api from "./axios";

export async function getZones(cameraId) {
    const response = await api.get("/zones", {
        params: { camera_id: cameraId },
    });

    return response.data.data;
}

export async function createZone({ cameraId, name, points, zoneType = "intrusion" }) {
    const response = await api.post("/zones", {
        camera_id: cameraId,
        name,
        zone_type: zoneType,
        points,
    });

    return response.data.data;
}

export async function updateZone(zoneId, updates) {
    const response = await api.put(`/zones/${zoneId}`, updates);

    return response.data.data;
}

export async function deleteZone(zoneId) {
    await api.delete(`/zones/${zoneId}`);
}

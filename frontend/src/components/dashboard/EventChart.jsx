import {
    BarChart,
    Bar,
    CartesianGrid,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

import { Paper, Typography } from "@mui/material";

const data = [
    { day: "Mon", events: 12 },
    { day: "Tue", events: 18 },
    { day: "Wed", events: 9 },
    { day: "Thu", events: 23 },
    { day: "Fri", events: 15 },
    { day: "Sat", events: 20 },
    { day: "Sun", events: 10 },
];

export default function EventChart() {
    return (
        <Paper
            elevation={3}
            sx={{
                mt: 4,
                p: 3,
                borderRadius: 3,
            }}
        >
            <Typography
                variant="h6"
                fontWeight="bold"
                mb={2}
            >
                Weekly Event Analytics
            </Typography>

            <ResponsiveContainer
                width="100%"
                height={300}
            >
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis dataKey="day" />

                    <YAxis />

                    <Tooltip />

                    <Bar
                        dataKey="events"
                        fill="#2563EB"
                        radius={[8, 8, 0, 0]}
                    />
                </BarChart>
            </ResponsiveContainer>
        </Paper>
    );
}
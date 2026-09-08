import { Card, CardContent, Box, Typography } from "@mui/material";

export default function StatCard({
    title,
    value,
    icon,
    color,
}) {
    return (
        <Card
            elevation={3}
            sx={{
                borderRadius: 3,
                position: "relative",
                overflow: "hidden",
            }}
        >
            <Box
                sx={{
                    position: "absolute",
                    left: 0,
                    top: 0,
                    bottom: 0,
                    width: 6,
                    bgcolor: color,
                }}
            />

            <CardContent>
                <Box
                    sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                    }}
                >
                    <Box>
                        <Typography
                            variant="body2"
                            color="text.secondary"
                        >
                            {title}
                        </Typography>

                        <Typography
                            variant="h4"
                            fontWeight="bold"
                            mt={1}
                        >
                            {value}
                        </Typography>
                    </Box>

                    <Box
                        sx={{
                            color: color,
                            fontSize: 40,
                        }}
                    >
                        {icon}
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );
}
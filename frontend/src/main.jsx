import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import App from "./App";

import { ThemeProvider } from "@mui/material/styles";

import theme from "./theme/theme";

const queryClient = new QueryClient();

createRoot(document.getElementById("root")).render(
    <StrictMode>

        <QueryClientProvider client={queryClient}>

            <ThemeProvider theme={theme}>

                <App />

            </ThemeProvider>

        </QueryClientProvider>
    </StrictMode>
);
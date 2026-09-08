import { createTheme } from "@mui/material/styles";

import colors from "./colors";

const theme = createTheme({
    palette: {
        primary: {
            main: colors.primary,
        },

        background: {
            default: colors.background,
        },
    },

    typography: {
        fontFamily: "Roboto, sans-serif",

        h6: {
            fontWeight: 700,
        },
    },

    shape: {
        borderRadius: 12,
    },
});

export default theme;
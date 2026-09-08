import { useEffect, useRef } from "react";

export function useWebSocket(onMessage) {

    const callbackRef = useRef(onMessage);

    useEffect(() => {
        callbackRef.current = onMessage;
    }, [onMessage]);

    useEffect(() => {

        const socket = new WebSocket(
            "ws://127.0.0.1:8000/ws"
        );

        socket.onopen = () => {
            console.log("✅ WebSocket Connected");
        };

        socket.onmessage = (event) => {

            console.log(
                "📨 Raw WebSocket message:",
                event.data
            );

            try {

                const message = JSON.parse(event.data);

                console.log(
                    "📨 WebSocket Message:",
                    message
                );

                callbackRef.current(message);

            } catch (error) {

                console.error(
                    "❌ Failed to parse WebSocket message:",
                    error
                );

            }
        };

        socket.onerror = (error) => {
            console.error(
                "❌ WebSocket Error:",
                error
            );
        };

        socket.onclose = (event) => {

            console.log(
                "🔌 WebSocket Closed:",
                event.code,
                event.reason
            );

        };

        return () => {

            if (
                socket.readyState === WebSocket.OPEN ||
                socket.readyState === WebSocket.CONNECTING
            ) {
                socket.close();
            }

        };

    }, []);
}
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";

import { useWebSocket } from "../hooks/useWebSocket";

const AlertsContext = createContext(null);

const MAX_ALERTS = 100;

// Severities that are loud enough to interrupt with a sound + popup.
// "INFO" events still show up in the events list, just quietly.
const AUDIBLE_SEVERITIES = new Set(["CRITICAL", "WARNING"]);

function normalizeEvent(raw) {
    return {
        id: raw.event_id ?? raw.id,
        event_type: raw.event_type,
        track_id: raw.track_id,
        camera_id: raw.camera_id,
        timestamp: raw.timestamp,
        severity: raw.severity,
        message: raw.message,
        metadata: raw.metadata ?? raw.event_metadata ?? {},
    };
}

// Short two-tone beep via the Web Audio API - no audio asset needed,
// and it still works the first time a user visits the page (subject
// to the browser's autoplay policy, which is why it's only triggered
// from the alert itself, i.e. after some other user interaction).
function playAlertSound(severity) {
    try {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        const ctx = new AudioContextClass();

        const frequencies = severity === "CRITICAL" ? [880, 660] : [660];

        frequencies.forEach((freq, index) => {
            const oscillator = ctx.createOscillator();
            const gain = ctx.createGain();

            oscillator.type = "sine";
            oscillator.frequency.value = freq;

            const startTime = ctx.currentTime + index * 0.18;

            gain.gain.setValueAtTime(0.0001, startTime);
            gain.gain.exponentialRampToValueAtTime(0.2, startTime + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.0001, startTime + 0.16);

            oscillator.connect(gain);
            gain.connect(ctx.destination);

            oscillator.start(startTime);
            oscillator.stop(startTime + 0.18);
        });

        setTimeout(() => ctx.close(), 500);
    } catch (error) {
        console.warn("Could not play alert sound:", error);
    }
}

export function AlertsProvider({ children }) {
    const [alerts, setAlerts] = useState([]);
    const [toast, setToast] = useState(null);
    const [unreadCount, setUnreadCount] = useState(0);
    const [soundEnabled, setSoundEnabled] = useState(true);
    const soundEnabledRef = useRef(soundEnabled);

    useEffect(() => {
        soundEnabledRef.current = soundEnabled;
    }, [soundEnabled]);

    const handleMessage = useCallback((message) => {
        if (message.type !== "event_created") {
            return;
        }

        const event = normalizeEvent(message.data);

        setAlerts((previous) => [event, ...previous].slice(0, MAX_ALERTS));
        setUnreadCount((count) => count + 1);
        setToast(event);

        if (AUDIBLE_SEVERITIES.has(event.severity) && soundEnabledRef.current) {
            playAlertSound(event.severity);
        }
    }, []);

    useWebSocket(handleMessage);

    const dismissToast = useCallback(() => setToast(null), []);
    const clearUnread = useCallback(() => setUnreadCount(0), []);
    const toggleSound = useCallback(() => setSoundEnabled((v) => !v), []);

    return (
        <AlertsContext.Provider
            value={{
                alerts,
                toast,
                dismissToast,
                unreadCount,
                clearUnread,
                soundEnabled,
                toggleSound,
            }}
        >
            {children}
        </AlertsContext.Provider>
    );
}

export function useAlerts() {
    const context = useContext(AlertsContext);

    if (!context) {
        throw new Error("useAlerts must be used within an AlertsProvider");
    }

    return context;
}

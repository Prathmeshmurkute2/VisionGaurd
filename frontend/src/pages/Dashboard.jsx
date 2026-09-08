import DashboardCards from "../components/dashboard/DashboardCards";
import RecentEvents from "../components/dashboard/RecentEvents";
import EventChart from "../components/dashboard/EventChart";
import LiveCamera from "../components/dashboard/LiveCamera";

import { useDashboard } from "../hooks/useDashboard";

export default function Dashboard() {

    const { data, isLoading, error } = useDashboard();

    if (isLoading) {
        return <h2>Loading...</h2>;
    }

    if (error) {
        return <h2>Something went wrong.</h2>;
    }

    return (
        <>
            <DashboardCards
                analytics={data.data.analytics}
            />

            <EventChart />

            <LiveCamera />

            <RecentEvents
                events={data.data.recent_events}
            />
        </>
    );
}
import { useEffect, useState } from "react";
import { dashboardResults } from "../api/dashboard";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import {
    Legend,
    PieChart,
    Pie,
    Cell,
} from "recharts";
export const DashboardHome = () => {

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                const res = await dashboardResults();
                setData(res.data);
                console.log(res);
            } catch (err) {
                console.log(err);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboard();
    }, []);

    //     const sortedVolume = [...data.email_volume].sort(
    //     (a, b) => new Date(a.date) - new Date(b.date)
    // );
    if (loading || !data) return <div className="loading">Loading...</div>;
    // if (!data || !data.top_reasons) return null;
    const categoryLabels = {
        "order_status": "Order Status",
        "return_request": "Return Request",
        "exchange_request": "Exchange Request",
        "refund_request": "Refund Request",
        "product_question": "Product Question",
        "complaint": "Complaint",
        "general": "General"
    };
    return (
        <>
            <div className="dashboardbox">

                <div className="bb1">
                    <div className="a1"><p>Total Emails</p><h1>{data.stats.total}</h1></div>
                    <div className="a1"><p>Today Emails</p><h1>{data.stats.today}</h1></div>
                    <div className="a1"><p>Pending Emails</p><h1>{data.stats.pending}</h1></div>
                    <div className="a1"><p>Emails Sent</p><h1>{data.stats.sent}</h1></div>
                </div>

                <div className="bb2">
                    <div className="c1">
                        <div className="a2">
                            <h3>Email Activity</h3>

                            <ResponsiveContainer width="100%" height="80%" className="a2a">
                                <LineChart data={data.email_volume}>

                                    {/* 🌈 Gradient */}
                                    <defs>
                                        <linearGradient id="colorLine" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#f29f67" stopOpacity={0.8} />
                                            <stop offset="100%" stopColor="#1e1e2c" stopOpacity={0.2} />
                                        </linearGradient>
                                    </defs>

                                    {/* 🟣 Soft grid */}
                                    <CartesianGrid
                                        stroke="#84848400"
                                        strokeDasharray="3 3"
                                        vertical={false}
                                    />

                                    {/* 📅 X Axis */}
                                    <XAxis
                                        dataKey="date"
                                        tickFormatter={(date) => date.slice(5)}
                                        stroke="#525050"
                                        tick={{ fill: "#1e1e2c", fontSize: 12 }}
                                        axisLine={false}
                                        tickLine={false}
                                        tickMargin={20}
                                    />

                                    {/* 📊 Y Axis */}
                                    <YAxis
                                        tickMargin={10}
                                        stroke="#525050"
                                        tick={{ fill: "#1e1e2c", fontSize: 12 }}
                                        axisLine={false}
                                        tickLine={false}
                                    />

                                    {/* 🧠 Tooltip */}
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: "#1a1a2e",
                                            border: "none",
                                            borderRadius: "10px",
                                            color: "#f29f67"
                                        }}
                                        labelStyle={{ color: "#f29f67" }}
                                    />

                                    {/* 💜 Area (background fill) */}
                                    <Line
                                        type="monotone"
                                        dataKey="count"
                                        stroke="#f29f67"
                                        strokeWidth={3}
                                        dot={{ r: 5, fill: "#1e1e2c", stroke: "#f29f67", strokeWidth: 2 }}
                                        activeDot={{ r: 7 }}
                                    />

                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="a3">
                            <h3>Category Distribution</h3>

                            <div className="chart-container">
                                <ResponsiveContainer width="100%" height={220}>
                                    <PieChart>
                                        <Pie
                                            data={data.category_breakdown}
                                            dataKey="count"
                                            nameKey="category"
                                            cx="50%"
                                            cy="50%"
                                            outerRadius={70}
                                            innerRadius={50}
                                            paddingAngle={4}
                                            stroke="#ffffff"
                                            strokeWidth={2}
                                            label={({ percent }) =>
                                                `${(percent * 100).toFixed(0)}%`
                                            }
                                            labelLine={false}
                                        >
                                            {data.category_breakdown.map((entry, index) => (
                                                <Cell
                                                    key={`cell-${index}`}
                                                    fill={
                                                        [
                                                            "#F29F67",
                                                            "#3B8FF3",
                                                            "#34B1AA",
                                                            "#E0B50F",
                                                            "#f5b183",
                                                            "#9ec5ff"
                                                        ][index % 6]
                                                    }
                                                />
                                            ))}
                                        </Pie>

                                        <Tooltip
                                            formatter={(value, name) => [`${value}`, name]}
                                            contentStyle={{
                                                background: "rgba(255,255,255,0.9)",
                                                border: "1px solid rgba(0,0,0,0.05)",
                                                borderRadius: "10px",
                                                color: "#1E1E2C"
                                            }}
                                            labelStyle={{ color: "#F29F67", fontWeight: 600 }}
                                        />
                                    </PieChart>
                                </ResponsiveContainer>

                                {/* 🔥 CUSTOM LABELS */}
                                <div className="custom-legend">
                                    {data.category_breakdown.map((item, index) => (
                                        <div key={index} className="legend-item">
                                            <span
                                                className="legend-color"
                                                style={{
                                                    backgroundColor: [
                                                        "#F29F67",
                                                        "#3B8FF3",
                                                        "#34B1AA",
                                                        "#E0B50F",
                                                        "#f5b183",
                                                        "#9ec5ff"
                                                    ][index % 6]
                                                }}
                                            ></span>

                                            <span className="legend-text">
                                                {item.category.replace("_", " ")}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>


                        <div className="a4">
                            <h3>Top Reasons</h3>
                            {!data.top_reasons && <p>No insights yet</p>}
                            {Object.entries(data.top_reasons || {}).map(([cat, reasons]) => (
                                <div key={cat} className="reason-block">

                                    <h4>{cat}</h4>

                                    {(reasons || []).slice(0, 3).map((item, i) => (
                                        <div key={i} className="reason-row">

                                            <div className="reason-header">
                                                <span>{item.reason}</span>
                                                <span>{item.percent}%</span>
                                            </div>

                                            <div className="progress-bar">
                                                <div
                                                    className="progress-fill"
                                                    style={{ width: `${item.percent}%` }}
                                                ></div>
                                            </div>

                                        </div>
                                    ))}
                                </div>
                            ))}
                        </div>



                        <div className="a5">
                            <h3>Response by Category</h3>
                            <div className="a5a">

                            {data.category_response.map((item, i) => (
                                <div key={i} className="cat-row">
                                    <div className="cat-header">
                                        <span>{categoryLabels[item.category]}</span>
                                        <span>{item.percent}%</span>
                                    </div>

                                    <div className="progress-bar">
                                        <div
                                            className="progress-fill"
                                            style={{ width: `${item.percent}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                            </div>

                        </div>

                    </div>





                    <div className="c2">
                        <div className="a6">
                            {/* <h3>Insights</h3> */}

                            <div className="a6a">

                                {/* 📊 Response Rate */}
                                <div className="a6aa">
                                    <p>Response Rate</p>
                                    <h2>{data.insights.response_rate}%</h2>
                                </div>

                                {/* ⏳ Pending Pressure */}
                                <div className="a6aa">
                                    <p>Pending Load</p>
                                    <h2>{data.insights.pending_pressure}%</h2>
                                </div>

                                {/* ⚡ Category Load */}
                                <div className="a6aa">
                                    <p>Top Category</p>
                                    <h2>{categoryLabels[data.insights.category_load?.category]}</h2>
                                    <span>{data.insights.category_load?.percent}%</span>
                                </div>

                                {/* 🔥 Top Issue */}
                                <div className="a6aa">
                                    <p>Top Issue</p>
                                    <h2>{data.insights.top_issue?.reason || "-"}</h2>
                                    <span>{data.insights.top_issue?.percent || 0}%</span>
                                </div>

                                {/* 📈 Trend */}
                                {/* <div className="a6aa">
                                    <p>Trend</p>
                                    <h2 style={{ color: data.insights.trend >= 0 ? "#6dffb3" : "#ff6b6b" }}>
                                        {data.insights.trend >= 0 ? "+" : ""}
                                        {data.insights.trend}%
                                    </h2>
                                </div> */}

                                {/* 🎯 Today Focus */}
                                <div className="a6aa">
                                    <p>Today Focus</p>
                                    <h2>{categoryLabels[data.insights.today_focus?.category]}</h2>
                                    <span>{data.insights.today_focus?.count} emails</span>
                                </div>

                                {/* 🕐 Peak Time */}
                                <div className="a6aa">
                                    <p>Peak Hour</p>
                                    <h2>{data.insights.peak_time?.hour}:00</h2>
                                    <span>{data.insights.peak_time?.count} emails</span>
                                </div>

                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};
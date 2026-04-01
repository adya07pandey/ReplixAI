import { useState, useEffect, useRef } from "react";
import { getEmails } from "../api/emails";
import { Category } from "../components/category";
import { UserCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { DashboardHome } from "../components/DashboardHome";
import { authMe } from "../api/auth";

export const Dashboard = () => {
    const [loading, setLoading] = useState(false);

    const [view, setView] = useState("dashboard"); // 🔥 NEW
    const [category, setCategory] = useState("");
    const [emails, setEmails] = useState([]);
    const [org, setOrg] = useState(null);
    const navigate = useNavigate();
    const categoryRef = useRef("");
    categoryRef.current = category;

    const categories = {
        "Order Status": "order_status",
        "Return Request": "return_request",
        "Exchange Request": "exchange_request",
        "Refund Request": "refund_request",
        "Product Question": "product_question",
        "Complaint": "complaint",
        "General": "general"
    };

    
    // ✅ fetch emails
    const fetchEmails = async (cat, showLoader = true) => {
        if (!cat) return;

        try {
            if (showLoader) setLoading(true);

            const res = await getEmails(cat);

            setEmails(prev =>
                JSON.stringify(prev) !== JSON.stringify(res.data)
                    ? res.data
                    : prev
            );

        } catch (err) {
            console.log(err);
        } finally {
            if (showLoader) setLoading(false);
        }
    };

    // ✅ fetch when category changes
    useEffect(() => {
        if (view === "category") {
            fetchEmails(category, true);
        }
    }, [category, view]);
    useEffect(() => {
    const fetchOrg = async () => {
        try {
            const res = await authMe();
            console.log(res.data);
            setOrg(res.data);
        } catch (err) {
            console.log(err);
        }
    };

    fetchOrg();
}, []);
   
    // ✅ websocket
    useEffect(() => {
        const ws = new WebSocket("ws://localhost:8000/emails/ws");

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (
                data.event === "new_email" &&
                data.category === categoryRef.current
            ) {
                fetchEmails(categoryRef.current, false);
            }
        };

        return () => ws.close();
    }, []);

    const handleCategoryClick = (cat) => {
        setCategory(cat);
        setView("category"); // 🔥 switch view
    };

    return (
        <>
            {/* Navbar */}
            <div className="navbar">
                <img className="logo" src="/logo1.png" alt="LOGO" />
                <div className="profile" onClick={() => navigate("/settings")}>
                    <h3>{org ? org.orgname : "Loading..."}</h3>
                    <UserCircle size={32} />
                </div>
            </div>

            <div className="page">

                {/* Sidebar */}
                <div className="sidebar">

                    <button
                        onClick={() => setView("dashboard")}
                        className={view === "dashboard" ? "category-active-btn" : ""}
                    >
                        Dashboard
                    </button>

                    {Object.entries(categories).map(([label, value]) => (
                        <button
                            key={value}
                            onClick={() => handleCategoryClick(value)}
                            className={
                                view === "category" && category === value
                                    ? "category-active-btn"
                                    : ""
                            }
                        >
                            {label}
                        </button>
                    ))}
                </div>

                {/* Main Content */}
                <div className="mainside">

                    {view === "dashboard" ? (
                        <DashboardHome />   // 🔥 clean separation
                    ) : (
                        <Category category={category} emails={emails} />
                    )}

                </div>
            </div>
        </>
    );
};
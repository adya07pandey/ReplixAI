import { useEffect, useState } from "react";
import { openMail, updateMail, sendMail } from "../api/emails";
import { ArrowLeft } from "lucide-react";


export const Category = ({ category, emails }) => {
    const [loading, setLoading] = useState(false);
    const [selectedMail, setSelectedMail] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [search, setSearch] = useState("");

    const open = async (emailid) => {
        try {
            setLoading(true);
            const res = await openMail(emailid);
            setSelectedMail(res.data);
            console.log(res.data);
        }
        catch (err) {
            console.log(err);
        }
        finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (!selectedMail) return;

        const timeout = setTimeout(() => {
            updateMail(selectedMail.id, {
                reply_subject: selectedMail.reply_subject,
                reply_body: selectedMail.reply_body
            });
        }, 1000);

        return () => clearTimeout(timeout);
    }, [selectedMail]);
    useEffect(() => {
        setSelectedMail(null);
    }, [category]);

    const sendmail = async () => {
        try {
            setLoading(true);

            // save latest edits
            await updateMail(selectedMail.id, {
                reply_subject: selectedMail.reply_subject,
                reply_body: selectedMail.reply_body
            });

            // send
            await sendMail(selectedMail.id);

            alert("Email sent!");

            setSelectedMail(null);

        } catch (err) {
            console.log(err);
            alert("Failed to send");
        } finally {
            setLoading(false);
        }
    };
    const categoryLabels = {
        "order_status": "Order Status",
        "return_request": "Return Request",
        "exchange_request": "Exchange Request",
        "refund_request": "Refund Request",
        "product_question": "Product Question",
        "complaint": "Complaint",
        "general": "General"
    };
    const filteredEmails = emails.filter((email) =>
        email.sender_subject?.toLowerCase().includes(search.toLowerCase()) ||
        email.sender_body?.toLowerCase().includes(search.toLowerCase())
    );

    const pendingEmails = filteredEmails
        .filter((email) => email.status !== "sent")
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    const sentEmails = filteredEmails
        .filter((email) => email.status === "sent")
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    return (
        <div className="box">

            {loading ? (
                <div className="loader">
                    <p>Loading...</p>
                </div>
            ) : selectedMail ? (
                <div className="open-mail">
                    <div className="back">
                        <button onClick={() => setSelectedMail(null)}><ArrowLeft size={20} /></button>
                    </div>
                    <div className="main">
                        <div className="reply">
                            <div>
                                <h3>Reply Mail</h3>
                                <div>

                                    {isEditing ? (
                                        <>
                                            {/* EDIT MODE */}
                                            <input
                                                className="subject"
                                                value={selectedMail.reply_subject || ""}
                                                onChange={(e) =>
                                                    setSelectedMail({
                                                        ...selectedMail,
                                                        reply_subject: e.target.value
                                                    })
                                                }
                                            />

                                            <p className="to">
                                                <b>To: </b>{selectedMail.sender_name} ({selectedMail.sender_email})
                                            </p>

                                            <textarea
                                                className="body"
                                                value={selectedMail.reply_body || ""}
                                                onChange={(e) =>
                                                    setSelectedMail({
                                                        ...selectedMail,
                                                        reply_body: e.target.value
                                                    })
                                                }
                                            />
                                        </>
                                    ) : (
                                        <>
                                            {/* VIEW MODE */}

                                            <p className="subject">{selectedMail.reply_subject}</p>

                                            <p className="to">
                                                <b>To: </b>{selectedMail.sender_name} ({selectedMail.sender_email})
                                            </p>

                                            <p className="body">{selectedMail.reply_body}</p>
                                        </>
                                    )}

                                </div>
                            </div>

                            {/* BUTTONS */}
                            <div className="actions">
                                {isEditing ? (
                                    <>
                                        <button
                                            onClick={async () => {
                                                try {
                                                    await updateMail(selectedMail.id, {
                                                        reply_subject: selectedMail.reply_subject,
                                                        reply_body: selectedMail.reply_body
                                                    });
                                                    setIsEditing(false);
                                                } catch (err) {
                                                    console.log(err);
                                                }
                                            }}
                                        >
                                            Save
                                        </button>

                                        <button onClick={() => setIsEditing(false)}>Cancel</button>
                                    </>
                                ) : (
                                    <>
                                        <button onClick={() => setIsEditing(true)}>Edit</button>
                                        <button className="sendbtn" disabled={selectedMail.is_replied} onClick={sendmail}>{selectedMail.is_replied ? "Sent" : "Send"}</button>
                                    </>
                                )}
                            </div>
                        </div>
                        <div className="sender">
                            <h3>Customer Email</h3>
                            <p className="subject">{selectedMail.sender_subject}</p>
                            <p className="from"><b>From: </b>{selectedMail.sender_name} ({selectedMail.sender_email})</p>
                            <p className="body">{selectedMail.sender_body}</p>
                        </div>
                    </div>

                </div>
            ) : (

                /* ✅ OTHERWISE → SHOW LIST */
                <>
                    <div className="searchbox">
                        <h3>{categoryLabels[category]} Mails</h3>
                        <input
                            type="text"
                            placeholder="Search..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>

                    <div className="maillist">
                        {pendingEmails.length === 0 && sentEmails.length === 0 ? (
                            <p>No emails</p>
                        ) : (
                            <>
                                {/* 🔥 PENDING */}
                                {pendingEmails.length > 0 && (
                                    <>
                                        <h4 className="section-title">Pending</h4>
                                        {pendingEmails.map((email) => (
                                            <div
                                                key={email.id}
                                                className="email-card pending"
                                                onClick={() => open(email.id)}
                                            >
                                                <div className="leftbox"></div>
                                                <p className="a">{email.sender_name}</p>
                                                <p className="b">
                                                    {email.sender_subject} - {email.sender_body}
                                                </p>
                                            </div>
                                        ))}
                                    </>
                                )}

                                {/* 🔽 SENT */}
                                {sentEmails.length > 0 && (
                                    <>
                                        <h4 className="section-title sent-title">Sent</h4>
                                        {sentEmails.map((email) => (
                                            <div
                                                key={email.id}
                                                className="email-card sent"
                                                onClick={() => open(email.id)}
                                            >
                                                <div className="leftbox"></div>
                                                <p className="a">{email.sender_name}</p>
                                                <p className="b">
                                                    {email.sender_subject} - {email.sender_body}
                                                </p>
                                            </div>
                                        ))}
                                    </>
                                )}
                            </>
                        )}
                    </div>
                </>
            )}
        </div>
    );
};
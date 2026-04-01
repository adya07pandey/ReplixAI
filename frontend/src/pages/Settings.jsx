import { useState } from "react"
import { connectGoogle, saveSettings, signup } from "../api/auth";

export const Settings = () => {

    const [form, setForm] = useState({ policyfile: null, mode: "" })

    const handleChange = (e) => {

        const { name, value, files } = e.target

        if (name === "policyfile") {
            setForm({ ...form, policyfile: files[0] })
        } else {
            setForm({ ...form, mode: value })
        }
    }
    const handleConnect = async () => {

        try {

            const formData = new FormData()

            formData.append("policyfile", form.policyfile)
            formData.append("mode", form.mode)

            await saveSettings(formData)

            connectGoogle()

        } catch (err) {
            console.log(err)
        }
    }

    return (
        <div className="wholepage">

            <div className="settingsbox">
                <h1>Company Policies</h1>
                <div className="settingsbox-a">

                <input type="file" name="policyfile" accept="application/pdf" className="pdfinput" placeholder="Policy File" onChange={handleChange} />


                <button className="loginbtn" onClick={() => { handleConnect() }}>Submit</button>
                </div>

            </div>

        </div>
    )
}
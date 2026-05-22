def monitor_agent(
    status="info",
    message=""
):

    if status == "success":
        print(f"✅ {message}")

    elif status == "error":
        print(f"❌ {message}")

    else:
        print(f"ℹ️ {message}")
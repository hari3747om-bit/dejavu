"""Streamlit UI.   Run:  streamlit run app.py"""
import streamlit as st

import agent
import memory
from seed_data import DEMO_ALERTS

st.set_page_config(page_title="Deja Vu - Incident Agent", layout="wide")
st.title("Deja Vu: the on-call agent that remembers")

choice = st.selectbox("Incoming alert", [f"{a['id']} - {a['service']}" for a in DEMO_ALERTS] + ["Custom"])
if choice == "Custom":
    alert = {
        "id": "INC-CUSTOM",
        "service": st.text_input("Service", "payments-service"),
        "error": st.text_area("Error / symptom", ""),
    }
else:
    alert = next(a for a in DEMO_ALERTS if choice.startswith(a["id"]))
    st.code(f"{alert['service']}: {alert['error']}")

if st.button("Run triage", type="primary"):
    with st.spinner("Thinking..."):
        st.session_state["baseline"], _ = agent.triage(alert, use_memory=False)
        st.session_state["smart"], st.session_state["mems"] = agent.triage(alert, use_memory=True)
        st.session_state["alert"] = alert


def show(advice):
    st.write(advice.get("summary", ""))
    for i, h in enumerate(advice.get("hypotheses", []), 1):
        st.markdown(f"**{i}. {h['cause']}** ({h.get('confidence', '?')}% confident)")
        st.write(f"Fix: {h['fix']}")
        st.caption(f"Evidence: {h.get('evidence', '-')}")
    if advice.get("skip"):
        st.error("Skip these (known not to work): " + "; ".join(advice["skip"]))


if "smart" in st.session_state:
    left, right = st.columns(2)
    with left:
        st.subheader("Without memory")
        show(st.session_state["baseline"])
    with right:
        st.subheader("With Hindsight memory")
        show(st.session_state["smart"])
        with st.expander(f"Memories used ({len(st.session_state['mems'])})"):
            for m in st.session_state["mems"]:
                st.write("- " + m)

    st.divider()
    st.subheader("Teach the agent")
    hyps = st.session_state["smart"].get("hypotheses", [])
    for i, h in enumerate(hyps):
        c1, c2, c3 = st.columns([4, 1, 1])
        c1.write(h["fix"])
        if c2.button("Worked", key=f"w{i}"):
            agent.record_outcome(st.session_state["alert"], h["fix"], "WORKED")
            st.success("Saved to memory")
        if c3.button("Didn't work", key=f"f{i}"):
            agent.record_outcome(st.session_state["alert"], h["fix"], "DID NOT WORK")
            st.warning("Saved to memory. I'll skip this next time.")

    with st.expander("Close incident (saves a post-mortem)"):
        rc = st.text_input("Actual root cause")
        res = st.text_input("What fixed it")
        if st.button("Save post-mortem") and rc and res:
            agent.close_incident(st.session_state["alert"], rc, res)
            st.success("Incident saved to memory")

st.divider()
if st.button("What patterns has the agent learned?"):
    with st.spinner("Reflecting..."):
        st.write(memory.reflect("What recurring incident patterns and root causes do we have per service? What fixes never work?"))

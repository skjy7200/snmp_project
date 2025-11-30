DEMO_SCRIPT – 15-minute SNMPv1-style Demo

This script outlines a 15-minute live demo of the project, as required by the
homework.

1. Start Agent (Terminal 1)

    cd snmp_project
    python src/agent.py

Explain:

- The Agent listens on 0.0.0.0:16100 using UDP.
- We use the Python socket library directly (no frameworks).
- Supported OIDs:
  - 1 → systemName
  - 2 → uptime
  - 3 → cpu

Show the console output that lists supported OIDs.

2. Start Manager (Terminal 2)

    cd snmp_project
    python src/manager.py

Explain:

- The Manager connects to the Agent host/port.
- It provides a text menu:
  - Show available OIDs
  - GET value by OID
  - Exit

3. Demo steps

1) Select option 1 (Show available OIDs)
   - Confirm that OIDs 1, 2, 3 are listed.

2) Select option 2 (GET value by OID), enter 1
   - Show that the Manager prints the systemName.
   - Point to the Agent terminal to show the received
     SNMP|1|public|GET|...|1 request and the RESPONSE message.

3) GET OID 2 (uptime) several times
   - Show that the uptime value increases as time passes.
   - Explain that this is calculated from the Agent's start time.

4) GET OID 3 (cpu)
   - Show that we get a simulated CPU usage (0–100).
   - Explain that in a real system this would read actual CPU metrics.

5) GET an invalid OID, e.g., 99
   - The Manager should print an error message indicating SNMP error
     (noSuchName).
   - The Agent terminal should show that it responded with error-status = 2.

4. Wrap-up

- Emphasize that:
  - UDP socket APIs are used directly (Python socket, SOCK_DGRAM).
  - The protocol fields are based on SNMPv1 RFC definitions (version, community,
    PDU type, request-id, error-status, error-index, OID, value).
  - ASN.1/BER is simplified to a text format for teaching, but the structure
    is still SNMPv1-inspired.
- Mention that the README and docs explicitly map this design back to the
  homework rubric and SNMPv1.

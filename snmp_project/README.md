Simple SNMPv1-style Network Application (Homework 3)

This project implements a small SNMPv1-style Agent–Manager system using UDP sockets.
The message structure follows the fields defined in SNMPv1 (RFC 1157)
(version, community, PDU type, request-id, error-status, error-index, OID, value),
but is encoded as a simple `|`-separated text format instead of ASN.1/BER for
educational purposes.

1. Team information

Course: [Course Name / Section]
Project: Homework 3 – Network Application
Team name: [Team Name]

Members:
- 김강현 (23011596) – Role: Agent (server), Docs, Testing, demo, documentation
- Vritztanto Joshua (22013086) – Role: Manager (client)
- Arabboeva (22012886) – Role: Protocol design, build scripts



2. Protocol overview (SNMPv1-inspired)

We use a text-based protocol whose fields correspond to SNMPv1 PDU structure.

2.1. GET request (Manager → Agent)

Format:

    SNMP|1|<community>|GET|<request-id>|<OID>

- SNMP        : protocol identifier
- 1           : SNMP version (v1)
- <community> : community string (default: public)
- GET         : PDU type
- <request-id>: integer request identifier
- <OID>       : object identifier (e.g., 1, 2, 3)

Example:

    SNMP|1|public|GET|42|1

2.2. RESPONSE (Agent → Manager)

Format (single VarBind):

    SNMP|1|<community>|RESPONSE|<request-id>|<error-status>|<error-index>|<OID>|<VALUE>

- <error-status>: SNMPv1 error code (subset)
  - 0 = noError
  - 2 = noSuchName
  - 5 = genErr
- <error-index>: index of the failed VarBind (we only use 0 or 1)
- <OID>        : the OID that was requested
- <VALUE>      : the returned value or an error description

Successful example:

    SNMP|1|public|RESPONSE|42|0|0|1|my-hostname

Error (unknown OID) example:

    SNMP|1|public|RESPONSE|42|2|1|99|Unknown OID

Supported OIDs in this educational implementation

- 1 → systemName (hostname of the Agent)
- 2 → uptime (seconds since the Agent process started)
- 3 → cpu (simulated CPU usage, 0–100)

3. How to run (from clean checkout)

Requirements:

- Python 3.x
- Only the Python standard library is used (no external dependencies).

3.1. Run Agent (server)

In terminal 1:

    cd snmp_project
    python src/agent.py

The Agent listens on UDP 0.0.0.0:16100.

3.2. Run Manager (client)

In terminal 2:

    cd snmp_project
    python src/manager.py [agent_host] [agent_port]

Examples:

    # Agent on localhost:16100
    python src/manager.py

    # Agent on another host
    python src/manager.py 192.168.0.10 16100

The Manager provides a simple text menu:

1. Show available OIDs
2. GET value by OID
3. Exit

4. Files in this project

- src/protocol.py – SNMPv1-style protocol helpers (version, community, PDU fields, error codes)
- src/agent.py – SNMPv1-style Agent (UDP server)
- src/manager.py – SNMPv1-style Manager (UDP client)
- docs/PROTOCOL_SPEC.md – protocol format and mapping to SNMPv1 PDU
- docs/DESIGN.md – architecture and design notes
- demo/DEMO_SCRIPT.md – 15-minute demo script
- Makefile – convenience targets for agent and manager
- CONTRIBUTION.md – per-member contribution summary (for individual score)

5. Limitations and scope

- Only a very small subset of SNMPv1 is implemented:
  - GET for a single OID
  - noError / noSuchName / genErr error-status
- This is an educational, SNMPv1-inspired implementation, not a full SNMP stack.
- ASN.1/BER encoding is intentionally replaced with a text format so that
  students can easily inspect and reason about protocol messages.

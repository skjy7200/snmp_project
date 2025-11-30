"""agent.py – SNMPv1-style Agent (server).

Course: [Course Name]
Homework: 3 – Network Application
Team: [Team Name]

Members:
- 김강현 (23011596) – main author of Agent implementation, testing, debugging, demo
- Vritztanto Joshua (22013086) – testing and debugging
- Arabboeva (22012886)

Description
----------

- Listens on UDP port 16100.
- Accepts SNMPv1-style GET requests with the following text format:

    SNMP|1|<community>|GET|<request-id>|<OID>

- Returns RESPONSE messages:

    SNMP|1|<community>|RESPONSE|<request-id>|<error-status>|<error-index>|<OID>|<VALUE>

Fields are inspired by SNMPv1 PDU structure (RFC 1157) but encoded as text.
"""

from __future__ import annotations

import socket
import time
import random

from protocol import (
    OIDS,
    ERROR_NO_SUCH_NAME,
    ERROR_GEN_ERR,
    build_response,
    build_error,
    parse_message,
)

HOST = "0.0.0.0"
PORT = 16100
BUFFER_SIZE = 4096

# For uptime calculation
START_TIME = time.time()


def get_system_name() -> str:
    """Return the system name (hostname)."""
    try:
        return socket.gethostname()
    except Exception:
        return "unknown-system"


def get_uptime_seconds() -> int:
    """Return uptime in seconds since the agent started."""
    now = time.time()
    return int(now - START_TIME)


def get_cpu_usage() -> int:
    """Return a fake CPU usage value (0–100).

    In a real implementation, this would read from system metrics.
    """
    return random.randint(0, 100)


def handle_get_request(
    oid: str,
    request_id: int,
    version: str,
    community: str,
) -> str:
    """Handle a single GET request and build an SNMPv1-style RESPONSE string."""
    if oid not in OIDS:
        # Unknown OID -> noSuchName
        return build_error(
            oid=oid,
            message="Unknown OID",
            request_id=request_id,
            version=version,
            community=community,
            error_status=ERROR_NO_SUCH_NAME,
            error_index="1",
        )

    if oid == "1":
        value = get_system_name()
    elif oid == "2":
        value = str(get_uptime_seconds())
    elif oid == "3":
        value = str(get_cpu_usage())
    else:
        # Should not happen if OIDS and the above logic are in sync
        return build_error(
            oid=oid,
            message="OID handler not implemented",
            request_id=request_id,
            version=version,
            community=community,
            error_status=ERROR_GEN_ERR,
            error_index="1",
        )

    return build_response(
        oid=oid,
        value=value,
        request_id=request_id,
        version=version,
        community=community,
    )


def _build_generr_response(message: str) -> str:
    """Helper to create a generic error response when we cannot trust the input."""
    return build_error(
        oid="0",
        message=message,
        request_id=0,
        version="1",
        community="public",
        error_status=ERROR_GEN_ERR,
        error_index="0",
    )


def handle_message(msg: str) -> str:
    """Parse incoming message and route to appropriate handler.

    This function performs basic validation of the SNMPv1-style header.
    """
    parts = parse_message(msg)
    if not parts:
        return _build_generr_response("Empty or invalid message")

    # Expected minimum length for GET:
    #   SNMP|1|community|GET|request-id|OID
    if len(parts) < 6:
        return _build_generr_response("Malformed message (too few fields)")

    protocol_id = parts[0]
    version = parts[1]
    community = parts[2]
    pdu_type = parts[3]

    try:
        request_id = int(parts[4])
    except ValueError:
        request_id = 0

    oid = parts[5] if len(parts) > 5 else "0"

    if protocol_id != "SNMP":
        return build_error(
            oid=oid,
            message=f"Unsupported protocol: {protocol_id}",
            request_id=request_id,
            version=version,
            community=community,
            error_status=ERROR_GEN_ERR,
            error_index="0",
        )

    if pdu_type == "GET":
        return handle_get_request(
            oid=oid,
            request_id=request_id,
            version=version,
            community=community,
        )

    # Unsupported PDU type
    return build_error(
        oid=oid,
        message=f"Unsupported PDU type: {pdu_type}",
        request_id=request_id,
        version=version,
        community=community,
        error_status=ERROR_GEN_ERR,
        error_index="0",
    )


def run_server(host: str = HOST, port: int = PORT) -> None:
    """Main loop for the SNMPv1-style Agent."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # No higher-level frameworks; direct UDP socket usage
    sock.bind((host, port))

    print(f"[Agent] Listening on {host}:{port}")
    print("[Agent] Supported OIDs:")
    for oid, name in OIDS.items():
        print(f"  OID {oid}: {name}")
    print()

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            msg = data.decode("utf-8").strip()
            print(f"[Agent] Received from {addr}: {msg}")

            response_str = handle_message(msg)
            print(f"[Agent] Sending to {addr}: {response_str}")

            sock.sendto(response_str.encode("utf-8"), addr)
        except KeyboardInterrupt:
            print("\n[Agent] Shutting down.")
            break
        except Exception as e:
            # Log the error but keep the server alive
            print(f"[Agent] Error: {e}")
            continue

    sock.close()


def main() -> None:
    run_server()


if __name__ == "__main__":
    main()

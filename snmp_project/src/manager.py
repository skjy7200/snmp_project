"""manager.py – SNMPv1-style Manager (client).

Course: [Course Name]
Homework: 3 – Network Application
Team: [Team Name]

Members:
- 김강현 (23011596) – Agent implementation, testing, debugging, demo
- Vritztanto Joshua (22013086) – main author of Manager implementation, testing and debugging
- Arabboeva (22012886)

Description
----------

- Builds SNMPv1-style GET PDUs:

    SNMP|1|public|GET|<request-id>|<OID>

- Sends them over UDP to the Agent.
- Receives RESPONSE PDUs and validates protocol-id, PDU type, and request-id.
"""

from __future__ import annotations

import socket
import sys
from typing import Tuple

from protocol import (
    OIDS,
    ERROR_NO_ERROR,
    build_get_request,
    parse_message,
)

DEFAULT_AGENT_HOST = "127.0.0.1"
DEFAULT_AGENT_PORT = 16100  # can change

BUFFER_SIZE = 4096
TIMEOUT_SEC = 3.0

# simple incremental request-id generator
_request_counter = 1


def _next_request_id() -> int:
    """Return the next request-id (increments each call)."""
    global _request_counter
    rid = _request_counter
    _request_counter += 1
    return rid


def send_get_request(
    oid: str,
    agent_host: str = DEFAULT_AGENT_HOST,
    agent_port: int = DEFAULT_AGENT_PORT,
) -> Tuple[bool, str]:
    """Send an SNMPv1-style GET request for the given OID to the Agent.

    Returns:
        (success, message)
        - success = True  -> message is the VALUE from RESPONSE
        - success = False -> message is an error description
    """
    request_id = _next_request_id()

    # Build SNMPv1-style GET PDU:
    #   SNMP|1|public|GET|<request-id>|<OID>
    request_str = build_get_request(oid=oid, request_id=request_id)
    request_bytes = request_str.encode("utf-8")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT_SEC)

    try:
        sock.sendto(request_bytes, (agent_host, agent_port))

        data, _addr = sock.recvfrom(BUFFER_SIZE)
        response_str = data.decode("utf-8").strip()

        parts = parse_message(response_str)
        if len(parts) < 9:
            return False, f"Malformed RESPONSE message: {parts}"

        protocol_id = parts[0]
        version = parts[1]
        community = parts[2]
        pdu_type = parts[3]
        resp_request_id_str = parts[4]
        error_status = parts[5]
        error_index = parts[6]
        resp_oid = parts[7]
        value_or_message = parts[8]

        # Basic validation
        if protocol_id != "SNMP":
            return False, f"Unexpected protocol: {protocol_id}"
        if pdu_type != "RESPONSE":
            return False, f"Unexpected PDU type: {pdu_type}"

        try:
            resp_request_id = int(resp_request_id_str)
        except ValueError:
            return False, f"Invalid request-id in RESPONSE: {resp_request_id_str}"

        if resp_request_id != request_id:
            return False, f"Mismatched request-id (sent {request_id}, got {resp_request_id})"

        if error_status != ERROR_NO_ERROR:
            # Any non-zero error-status is treated as an error.
            return False, f"SNMP error (status={error_status}, index={error_index}): {value_or_message}"

        # Success path
        return True, value_or_message

    except socket.timeout:
        return False, "Timed out waiting for agent response"
    except Exception as e:
        return False, f"Socket error: {e}"
    finally:
        sock.close()


def print_available_oids() -> None:
    """Print list of supported OIDs and their names (from protocol.OIDS)."""
    print("\nAvailable OIDs:")
    for oid, name in OIDS.items():
        print(f"  {oid} : {name}")
    print()


def interactive_menu() -> None:
    """Simple terminal UI for the SNMPv1-style Manager."""
    while True:
        print("******* Simple SNMPv1-style SNMP Manager *******")
        print("1) Show available OIDs")
        print("2) GET value by OID")
        print("3) Exit")
        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            print_available_oids()

        elif choice == "2":
            oid = input("Enter OID (e.g., 1, 2, 3): ").strip()
            if not oid:
                print("OID cannot be empty.\n")
                continue

            print(f"\nSending SNMP GET request for OID {oid}...")
            success, msg = send_get_request(oid)
            if success:
                oid_name = OIDS.get(oid, "Unknown OID")
                print(f"RESPONSE: {oid_name} (OID {oid}) = {msg}\n")
            else:
                print(f"ERROR: {msg}\n")

        elif choice == "3":
            print("Exiting manager.")
            break
        else:
            print("Invalid option. Please select 1, 2, or 3.\n")


def main() -> None:
    """Entry point for the Manager program."""
    agent_host = DEFAULT_AGENT_HOST
    agent_port = DEFAULT_AGENT_PORT

    if len(sys.argv) >= 2:
        agent_host = sys.argv[1]
    if len(sys.argv) >= 3:
        agent_port = int(sys.argv[2])

    print(f"SNMP Manager connecting to agent at {agent_host}:{agent_port}")
    interactive_menu()


if __name__ == "__main__":
    main()

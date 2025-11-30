# SNMPv1-style Project Design

This document outlines the architecture and design of the simple SNMPv1-style
Agent–Manager network application.

## 1. Overall Architecture

The system is designed based on a classic Client-Server model:

- Agent (Server): A UDP-based server that continuously runs, listening for incoming requests on a specific port. It manages a small set of "managed objects" identified by OIDs and responds to queries about them.
- Manager (Client): A UDP-based client that sends requests to the Agent to query the value of specific OIDs. It provides a user-facing interactive command-line interface.

The communication is connectionless, relying on the UDP protocol. The Manager handles potential packet loss by implementing a simple timeout mechanism.

## 2. Component Descriptions

The project is logically divided into three main Python modules in the `src/` directory.

### `src/protocol.py`

This module acts as a shared library for both the Agent and Manager. It isolates all protocol-specific definitions and helper functions.

- Constants: Defines protocol-wide constants such as supported OIDs (`OIDS` dictionary) and SNMP error codes (e.g., `ERROR_NO_ERROR`, `ERROR_NO_SUCH_NAME`).
- Message Builders: Provides functions (`build_get_request`, `build_response`, `build_error`) to construct the `|`-separated string messages, ensuring a consistent format.
- Message Parser: Includes a `parse_message` function that splits a raw string message into its component parts.

### `src/agent.py` (Server-side Logic)

This module contains the full implementation of the Agent.

- Socket Handling: It creates a `SOCK_DGRAM` (UDP) socket and binds it to `0.0.0.0` at port `16100`, allowing it to receive requests from any network interface.
- Main Loop: The `run_server` function contains an infinite `while True` loop to continuously listen for incoming data using `sock.recvfrom()`.
- Message Handling: Upon receiving a message, `handle_message` is called. It parses the message, validates the protocol format (e.g., "SNMP" identifier, PDU type), and routes it to the appropriate handler (`handle_get_request`).
- Data Retrieval: For a valid GET request, it retrieves the requested data by calling local functions (e.g., `get_system_name()`, `get_uptime_seconds()`, `get_cpu_usage()`). It is designed to be extensible for new OIDs.
- Error Handling: If an OID is not found or a message is malformed, it constructs and sends a proper error RESPONSE using helpers from `protocol.py`.

### `src/manager.py` (Client-side Logic)

This module implements the Manager, which initiates communication.

- User Interface: The `interactive_menu` function provides a simple text-based command-line interface for the user to select actions (show OIDs, get value, exit).
- Request Generation: It uses `build_get_request` from the `protocol` module to create a request string based on user input. A unique, incrementing `request-id` is generated for each request.
- Communication: The `send_get_request` function creates a new UDP socket for each request, sends the data using `sock.sendto()`, and then waits for a response with `sock.recvfrom()`.
- Timeout Mechanism: A socket timeout (`TIMEOUT_SEC`) is set to prevent the client from hanging indefinitely if the Agent does not respond.
- Response Validation: After receiving a response, it parses the message and performs several checks: protocol identifier, PDU type ("RESPONSE"), and whether the `request-id` matches the one sent. It also checks the `error-status` field to determine if the request was successful.

## 3. Protocol Design

The protocol is a simplified, text-based version of SNMPv1, as defined in `docs/PROTOCOL_SPEC.md`.

- Format: Fields are separated by a pipe (`|`) character for easy parsing and debugging.
- Encoding: UTF-8 is used for all string data.
- PDU Types: Only a subset of SNMP is implemented, primarily `GET` for requests and `RESPONSE` for replies.

This design choice prioritizes simplicity and readability for the educational context of the project over strict adherence to the binary ASN.1/BER encoding of the official SNMP standard.

## 4. Data Flow (GET Request Example)

1.  The Manager user chooses to get an OID value (e.g., "1").
2.  `manager.py` calls `build_get_request(oid="1", ...)` to create the string `SNMP|1|public|GET|<id>|1`.
3.  The Manager opens a UDP socket and sends this message to the Agent's address (`127.0.0.1:16100`).
4.  The Agent's main loop receives the UDP datagram.
5.  `agent.py` calls `handle_message`, which parses the string. It validates the "SNMP" and "GET" fields.
6.  `handle_get_request` is called with `oid="1"`.
7.  The handler matches `oid="1"` to the `get_system_name()` function.
8.  `get_system_name()` returns the machine's hostname (e.g., "my-desktop").
9.  The Agent calls `build_response(oid="1", value="my-desktop", ...)` to create the string `SNMP|1|public|RESPONSE|<id>|0|0|1|my-desktop`.
10. The Agent sends this response string back to the Manager's address (which it received via `recvfrom`).
11. The Manager receives the response. It validates the `request-id` and checks that `error-status` is "0".
12. It extracts the value "my-desktop" and displays it to the user.
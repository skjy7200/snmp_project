PROTOCOL_SPEC – SNMPv1-style Text Protocol

This document describes our SNMPv1-inspired text protocol. The field layout
mirrors SNMPv1 PDU structure (RFC 1157), but instead of ASN.1/BER encoding we
use a simple |‑separated UTF-8 text format for clarity.

1. GET request (Manager → Agent)

Format:

    SNMP|1|<community>|GET|<request-id>|<OID>

- SNMP         : protocol identifier
- 1            : version (SNMPv1)
- <community>  : community string (default: public)
- GET          : PDU type
- <request-id> : integer request identifier
- <OID>        : object identifier (e.g., 1, 2, 3)

Example:

    SNMP|1|public|GET|42|1

2. RESPONSE (Agent → Manager)

Format (single VarBind):

    SNMP|1|<community>|RESPONSE|<request-id>|<error-status>|<error-index>|<OID>|<VALUE>

- SNMP          : protocol identifier
- 1             : version (SNMPv1)
- <community>   : community string (echoed back)
- RESPONSE      : PDU type
- <request-id>  : same value as in the request
- <error-status>: SNMPv1 error code (subset)
  - 0 = noError
  - 2 = noSuchName
  - 5 = genErr
- <error-index> : index of the failed VarBind (we only use 0 or 1)
- <OID>         : requested OID
- <VALUE>       : returned value for noError, or error description for errors

Successful example:

    SNMP|1|public|RESPONSE|42|0|0|1|my-hostname

Unknown OID example:

    SNMP|1|public|RESPONSE|42|2|1|99|Unknown OID

3. Supported OIDs

Our educational Agent supports a small subset of OIDs:

- 1 – systemName
  - Hostname of the Agent system.
- 2 – uptime
  - Seconds since the Agent process started.
- 3 – cpu
  - Simulated CPU usage (0–100).

4. Transport and APIs

- Transport protocol: UDP
- Default Agent port: 16100
- Encoding: UTF-8 text
- Implementation: Python socket module with SOCK_DGRAM (no higher-level frameworks).

This satisfies the assignment requirement of using standard socket APIs, and the
message structure is explicitly based on SNMPv1 RFC definitions.

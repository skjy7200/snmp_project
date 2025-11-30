"""protocol.py – SNMPv1-style text protocol helpers.

Course: [Course Name]
Homework: 3 – Network Application
Team: [Team Name]

Members:
- 김강현 (23011596)
- Vritztanto Joshua (22013086)
- Arabboeva (22012886)

The message fields follow SNMPv1 PDU structure (RFC 1157):

    version, community, PDU type, request-id, error-status, error-index, OID, VALUE

We encode them as `|`-separated UTF-8 text for educational purposes.
"""

from typing import List, Dict

# Supported OIDs (very small subset for the assignment)
OIDS: Dict[str, str] = {
    "1": "systemName",
    "2": "uptime",
    "3": "cpu",
}

# SNMPv1 error-status codes (subset)
ERROR_NO_ERROR = "0"
ERROR_TOO_BIG = "1"
ERROR_NO_SUCH_NAME = "2"
ERROR_BAD_VALUE = "3"
ERROR_READ_ONLY = "4"
ERROR_GEN_ERR = "5"


def build_get_request(
    oid: str,
    request_id: int,
    version: str = "1",
    community: str = "public",
) -> str:
    """Create an SNMPv1-style GET request message (single OID).

    Format:
        SNMP|<version>|<community>|GET|<request-id>|<OID>
    """
    return f"SNMP|{version}|{community}|GET|{request_id}|{oid}"


def build_response(
    oid: str,
    value: str,
    request_id: int,
    version: str = "1",
    community: str = "public",
) -> str:
    """Create a successful SNMPv1-style RESPONSE message (noError).

    Format:
        SNMP|<version>|<community>|RESPONSE|<request-id>|0|0|<OID>|<VALUE>
    """
    return (
        f"SNMP|{version}|{community}|RESPONSE|{request_id}|{ERROR_NO_ERROR}|0|{oid}|{value}"
    )


def build_error(
    oid: str,
    message: str,
    request_id: int,
    version: str = "1",
    community: str = "public",
    error_status: str = ERROR_NO_SUCH_NAME,
    error_index: str = "1",
) -> str:
    """Create an SNMPv1-style RESPONSE message with an error.

    Format:
        SNMP|<version>|<community>|RESPONSE|<request-id>|<error-status>|<error-index>|<OID>|<MESSAGE>
    """
    return (
        f"SNMP|{version}|{community}|RESPONSE|{request_id}|{error_status}|{error_index}|{oid}|{message}"
    )


def parse_message(msg: str) -> List[str]:
    """Split a received message into its fields (by '|').

    Example:
        'SNMP|1|public|GET|42|1'
        'SNMP|1|public|RESPONSE|42|0|0|1|my-host'
    """
    return msg.strip().split("|")

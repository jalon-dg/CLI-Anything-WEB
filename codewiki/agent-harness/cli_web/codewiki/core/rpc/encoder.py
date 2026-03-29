"""Encode batchexecute RPC requests for Code Wiki."""

from __future__ import annotations

import json
from urllib.parse import urlencode

from .types import BATCHEXECUTE_URL


def build_url(rpc_id: str) -> str:
    """Build the full batchexecute URL with query parameters."""
    params = {
        "rpcids": rpc_id,
        "source-path": "/",
        "hl": "en",
        "rt": "c",
    }
    return f"{BATCHEXECUTE_URL}?{urlencode(params)}"


def encode_request(rpc_id: str, params: list) -> str:
    """Encode an RPC call into a form-encoded f.req body.

    The batchexecute wire format wraps each call as:
      [[[rpc_id, json_string_params, null, "generic"]]]

    No CSRF token needed — Code Wiki is fully public.
    """
    inner = [rpc_id, json.dumps(params), None, "generic"]
    freq = json.dumps([[inner]])
    return urlencode({"f.req": freq})

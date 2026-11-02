"""
MCP Server for Physiological Tremor & Neuromuscular Steadiness.
Exposes JSON-RPC endpoints for spectral microtremor analysis and motor steadiness assessment.
"""

import json
import sys
from client import PhysiologicalTremorClient

client = PhysiologicalTremorClient()


def handle_request(request: dict) -> dict:
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "analyze_tremor_timeseries",
                        "description": "Performs discrete spectral power analysis on acceleration timeseries to evaluate 8-12 Hz physiological tremor, RMS amplitude, and motor fatigue.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "acceleration_samples": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "description": "Acceleration or angular rate timeseries samples (e.g. in m/s² or mg)"
                                },
                                "sample_rate_hz": {
                                    "type": "number",
                                    "default": 50.0,
                                    "description": "Sensor sampling rate in Hertz"
                                },
                                "axis_name": {
                                    "type": "string",
                                    "default": "dominant_axis",
                                    "description": "Axis orientation label"
                                }
                            },
                            "required": ["acceleration_samples"]
                        }
                    },
                    {
                        "name": "assess_postural_vs_rest_ratio",
                        "description": "Evaluates postural vs resting tremor power to verify normal physiological tremor behavior versus pathological resting tremor.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "rest_samples": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "description": "Acceleration samples recorded while limb is supported at complete rest"
                                },
                                "postural_samples": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "description": "Acceleration samples recorded while limb is extended against gravity"
                                },
                                "sample_rate_hz": {
                                    "type": "number",
                                    "default": 50.0,
                                    "description": "Sensor sampling rate in Hertz"
                                }
                            },
                            "required": ["rest_samples", "postural_samples"]
                        }
                    }
                ]
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "analyze_tremor_timeseries":
            res = client.analyze_tremor_timeseries(
                acceleration_samples=args.get("acceleration_samples", []),
                sample_rate_hz=args.get("sample_rate_hz", 50.0),
                axis_name=args.get("axis_name", "dominant_axis")
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }

        elif tool_name == "assess_postural_vs_rest_ratio":
            res = client.assess_postural_vs_rest_ratio(
                rest_samples=args.get("rest_samples", []),
                postural_samples=args.get("postural_samples", []),
                sample_rate_hz=args.get("sample_rate_hz", 50.0)
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method {tool_name} not found"}
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32600, "message": "Invalid Request"}
    }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

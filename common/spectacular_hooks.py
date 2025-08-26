from typing import Any, Dict


def add_global_workspace_header(
    result: Dict[str, Any], generator: Any, request: Any
) -> Dict[str, Any]:
    """Postprocessing hook to add a reusable X-Workspace-ID header param to all operations."""
    comp = result.setdefault("components", {}).setdefault("parameters", {})
    comp["XWorkspaceId"] = {
        "name": "X-Workspace-ID",
        "in": "header",
        "required": False,
        "schema": {"type": "string", "format": "uuid"},
        "description": "Active workspace ID. Required for tenant-scoped endpoints.",
    }

    # Attach to all operations
    for path_item in result.get("paths", {}).values():
        for op in list(path_item.values()):
            if not isinstance(op, dict):
                continue
            params = op.setdefault("parameters", [])
            # Only add if not already present
            if not any(
                p.get("$ref") == "#/components/parameters/XWorkspaceId" for p in params
            ):
                params.append({"$ref": "#/components/parameters/XWorkspaceId"})
    return result

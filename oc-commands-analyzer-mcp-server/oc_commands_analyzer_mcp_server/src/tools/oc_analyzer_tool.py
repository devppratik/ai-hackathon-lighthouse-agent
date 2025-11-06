"""OC Command Analyzer tool for the OC Commands Analyzer MCP Server.

This tool analyzes OpenShift CLI (oc) commands and provides detailed information
about their functionality, parameters, and usage patterns.
"""

import json
import subprocess
from typing import Any, Dict, List, Optional

from oc_commands_analyzer_mcp_server.utils.pylogger import get_python_logger

logger = get_python_logger()


def analyze_oc_command(command: str) -> Dict[str, Any]:
    """Analyze an OpenShift CLI (oc) command and provide detailed insights.

    TOOL_NAME=analyze_oc_command
    DISPLAY_NAME=OC Command Analyzer
    USECASE=Analyze OpenShift CLI commands to understand their structure, purpose, and usage
    INSTRUCTIONS=1. Provide an oc command string, 2. Tool will parse and analyze the command, 3. Receive detailed analysis
    INPUT_DESCRIPTION=Single parameter: command (string). Examples: "oc get pods", "oc describe deployment myapp", "oc logs -f pod/mypod"
    OUTPUT_DESCRIPTION=Dictionary with command breakdown, resource type, operation, flags, and recommendations
    EXAMPLES=analyze_oc_command("oc get pods -n production"), analyze_oc_command("oc apply -f deployment.yaml")
    PREREQUISITES=None - pure command analysis without execution
    RELATED_TOOLS=execute_oc_command, validate_oc_syntax

    This tool parses and analyzes oc commands to help users understand what they do.
    It does NOT execute the command - it only analyzes the syntax and semantics.

    Args:
        command: The oc command to analyze (e.g., "oc get pods -n production")

    Returns:
        Dictionary containing detailed analysis of the command including:
        - status: Success or error status
        - operation: The primary operation (get, create, delete, etc.)
        - resource_type: The resource being operated on
        - flags: List of flags and their values
        - namespace: The namespace if specified
        - analysis: Human-readable explanation of what the command does
        - recommendations: Best practices and suggestions

    Raises:
        ValueError: If the command is not a valid oc command
    """
    try:
        # Validate that it's an oc command
        if not command.strip().startswith("oc "):
            raise ValueError(
                "Command must start with 'oc'. Provided command: " + command
            )

        # Parse the command
        parts = command.strip().split()
        if len(parts) < 2:
            raise ValueError("Command is too short. Format: oc <operation> [args]")

        # Extract operation (second part after 'oc')
        operation = parts[1]

        # Initialize analysis results
        analysis_result = {
            "status": "success",
            "command": command,
            "operation": operation,
            "resource_type": None,
            "flags": {},
            "namespace": None,
            "arguments": [],
            "analysis": "",
            "recommendations": [],
        }

        # Extract resource type (usually third part)
        if len(parts) > 2 and not parts[2].startswith("-"):
            analysis_result["resource_type"] = parts[2]

        # Parse flags and arguments
        i = 2
        while i < len(parts):
            if parts[i].startswith("-"):
                flag = parts[i]
                # Check if flag has a value
                if i + 1 < len(parts) and not parts[i + 1].startswith("-"):
                    value = parts[i + 1]
                    analysis_result["flags"][flag] = value

                    # Special handling for namespace flag
                    if flag in ["-n", "--namespace"]:
                        analysis_result["namespace"] = value
                    i += 2
                else:
                    analysis_result["flags"][flag] = True
                    i += 1
            else:
                if analysis_result["resource_type"] is None:
                    analysis_result["resource_type"] = parts[i]
                else:
                    analysis_result["arguments"].append(parts[i])
                i += 1

        # Generate human-readable analysis
        analysis_text = _generate_analysis(analysis_result)
        analysis_result["analysis"] = analysis_text

        # Generate recommendations
        recommendations = _generate_recommendations(analysis_result)
        analysis_result["recommendations"] = recommendations

        logger.info(
            f"Successfully analyzed oc command",
            operation=operation,
            resource=analysis_result["resource_type"],
        )

        return analysis_result

    except ValueError as e:
        logger.error(f"Validation error in oc command analysis: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Invalid oc command format",
        }
    except Exception as e:
        logger.error(f"Error analyzing oc command: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to analyze oc command",
        }


def _generate_analysis(result: Dict[str, Any]) -> str:
    """Generate human-readable analysis of the command."""
    operation = result["operation"]
    resource = result["resource_type"]
    namespace = result["namespace"]

    operation_descriptions = {
        "get": "retrieve and display",
        "describe": "show detailed information about",
        "create": "create new",
        "apply": "apply configuration to",
        "delete": "delete",
        "edit": "edit configuration of",
        "logs": "view logs from",
        "exec": "execute command in",
        "port-forward": "forward ports to",
        "scale": "scale",
        "rollout": "manage rollout of",
        "expose": "expose",
        "label": "manage labels for",
        "annotate": "manage annotations for",
    }

    action = operation_descriptions.get(operation, operation)

    if resource:
        text = f"This command will {action} {resource} resource(s)"
    else:
        text = f"This command will perform {operation} operation"

    if namespace:
        text += f" in the '{namespace}' namespace"

    if result["flags"]:
        text += f". Additional flags: {', '.join(result['flags'].keys())}"

    return text + "."


def _generate_recommendations(result: Dict[str, Any]) -> List[str]:
    """Generate best practice recommendations based on the command."""
    recommendations = []
    operation = result["operation"]
    flags = result["flags"]

    # Recommend namespace specification for production
    if result["namespace"] is None and operation in ["get", "describe", "delete"]:
        recommendations.append(
            "Consider specifying a namespace with -n or --namespace flag for clarity"
        )

    # Recommend dry-run for destructive operations
    if operation in ["delete", "create", "apply"] and "--dry-run" not in flags:
        recommendations.append(
            "For safety, consider using --dry-run=client to preview changes before applying"
        )

    # Recommend using -o yaml for getting resources
    if operation == "get" and "-o" not in flags and "--output" not in flags:
        recommendations.append(
            "Use -o yaml or -o json to get full resource details in structured format"
        )

    # Recommend using labels for production
    if operation in ["get", "delete"] and "-l" not in flags and "--selector" not in flags:
        recommendations.append(
            "Consider using label selectors (-l) to filter resources precisely"
        )

    # Security recommendation for exec
    if operation == "exec":
        recommendations.append(
            "Be cautious with exec - it provides direct access to container environments"
        )

    return recommendations


def get_oc_help(subcommand: Optional[str] = None) -> Dict[str, Any]:
    """Get help information for oc commands.

    TOOL_NAME=get_oc_help
    DISPLAY_NAME=OC Command Help
    USECASE=Retrieve help documentation for OpenShift CLI commands
    INSTRUCTIONS=1. Optionally provide a subcommand name, 2. Receive help documentation
    INPUT_DESCRIPTION=Optional parameter: subcommand (string). Examples: "get", "apply", None (for general help)
    OUTPUT_DESCRIPTION=Dictionary with help text and available options
    EXAMPLES=get_oc_help("get"), get_oc_help()
    PREREQUISITES=oc CLI must be installed on the system
    RELATED_TOOLS=analyze_oc_command

    Retrieves help information from the oc CLI tool.

    Args:
        subcommand: Optional specific oc subcommand to get help for (e.g., "get", "apply")

    Returns:
        Dictionary containing help information

    Raises:
        RuntimeError: If oc CLI is not available
    """
    try:
        # Build the help command
        cmd = ["oc"]
        if subcommand:
            cmd.extend([subcommand, "--help"])
        else:
            cmd.append("--help")

        # Execute the help command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            raise RuntimeError(f"oc command failed: {result.stderr}")

        logger.info(f"Retrieved oc help", subcommand=subcommand)

        return {
            "status": "success",
            "subcommand": subcommand,
            "help_text": result.stdout,
            "message": f"Help for oc {subcommand if subcommand else 'command'} retrieved successfully",
        }

    except FileNotFoundError:
        logger.error("oc CLI not found on system")
        return {
            "status": "error",
            "error": "oc CLI not found",
            "message": "The oc command-line tool is not installed or not in PATH",
        }
    except subprocess.TimeoutExpired:
        logger.error("oc help command timed out")
        return {
            "status": "error",
            "error": "Command timeout",
            "message": "The help command took too long to execute",
        }
    except Exception as e:
        logger.error(f"Error getting oc help: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to retrieve oc help information",
        }


def explain_oc_resource(resource_type: str) -> Dict[str, Any]:
    """Explain an OpenShift resource type using oc explain.

    TOOL_NAME=explain_oc_resource
    DISPLAY_NAME=OC Resource Explainer
    USECASE=Get detailed documentation about OpenShift resource types and their fields
    INSTRUCTIONS=1. Provide a resource type name, 2. Receive detailed field documentation
    INPUT_DESCRIPTION=Parameter: resource_type (string). Examples: "pod", "deployment", "service", "pod.spec.containers"
    OUTPUT_DESCRIPTION=Dictionary with resource documentation including fields, types, and descriptions
    EXAMPLES=explain_oc_resource("pod"), explain_oc_resource("deployment.spec")
    PREREQUISITES=oc CLI must be installed and configured with cluster access
    RELATED_TOOLS=analyze_oc_command, get_oc_help

    Uses 'oc explain' to provide detailed documentation about resource types.

    Args:
        resource_type: The resource type to explain (e.g., "pod", "deployment.spec.replicas")

    Returns:
        Dictionary containing resource documentation

    Raises:
        RuntimeError: If oc CLI is not available or not connected to a cluster
    """
    try:
        # Execute oc explain command
        result = subprocess.run(
            ["oc", "explain", resource_type],
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode != 0:
            raise RuntimeError(f"oc explain failed: {result.stderr}")

        logger.info(f"Explained oc resource", resource_type=resource_type)

        return {
            "status": "success",
            "resource_type": resource_type,
            "explanation": result.stdout,
            "message": f"Successfully retrieved documentation for {resource_type}",
        }

    except FileNotFoundError:
        logger.error("oc CLI not found on system")
        return {
            "status": "error",
            "error": "oc CLI not found",
            "message": "The oc command-line tool is not installed or not in PATH",
        }
    except subprocess.TimeoutExpired:
        logger.error("oc explain command timed out")
        return {
            "status": "error",
            "error": "Command timeout",
            "message": "The explain command took too long to execute",
        }
    except Exception as e:
        logger.error(f"Error explaining oc resource: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to explain resource {resource_type}",
        }

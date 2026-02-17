"""
Attack Path Router System

Routes user intent to appropriate attack strategies with classification
and approval controls for the AI penetration testing framework.
"""

from enum import Enum
from typing import Dict, List
import logging
import re

logger = logging.getLogger(__name__)


class AttackCategory(str, Enum):
    """Categories of attack paths available to the agent."""
    CVE_EXPLOITATION = "cve_exploitation"
    BRUTE_FORCE = "brute_force"
    WEB_APP_ATTACK = "web_app_attack"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    LATERAL_MOVEMENT = "lateral_movement"
    PASSWORD_SPRAY = "password_spray"
    SOCIAL_ENGINEERING = "social_engineering"
    NETWORK_PIVOT = "network_pivot"
    FILE_EXFILTRATION = "file_exfiltration"
    PERSISTENCE = "persistence"


class AttackPathRouter:
    """
    Routes user intent to attack strategies with classification and approval controls.
    """

    ATTACK_KEYWORDS: Dict[AttackCategory, List[str]] = {
        AttackCategory.CVE_EXPLOITATION: [
            "cve", "exploit", "vulnerability", "advisory", "patch",
            "remote code execution", "rce", "zero-day",
        ],
        AttackCategory.BRUTE_FORCE: [
            "brute force", "brute-force", "crack", "wordlist",
            "dictionary attack", "hydra", "john",
        ],
        AttackCategory.WEB_APP_ATTACK: [
            "sql injection", "sqli", "xss", "cross-site", "web app",
            "webapp", "csrf", "ssrf", "injection", "web application",
        ],
        AttackCategory.PRIVILEGE_ESCALATION: [
            "privilege escalation", "privesc", "priv esc", "root",
            "admin", "sudo", "suid", "escalate",
        ],
        AttackCategory.LATERAL_MOVEMENT: [
            "lateral movement", "lateral", "move laterally",
            "psexec", "wmi", "ssh hop", "spread",
        ],
        AttackCategory.PASSWORD_SPRAY: [
            "password spray", "spray", "credential stuffing",
            "default credentials", "common passwords",
        ],
        AttackCategory.SOCIAL_ENGINEERING: [
            "social engineering", "phishing", "spear phishing",
            "pretexting", "vishing", "smishing",
        ],
        AttackCategory.NETWORK_PIVOT: [
            "network pivot", "pivot", "tunnel", "port forward", "proxy",
            "socks", "chisel", "ligolo", "pivoting",
        ],
        AttackCategory.FILE_EXFILTRATION: [
            "exfiltrate", "exfiltration", "data theft", "steal",
            "extract data", "download files", "dump",
        ],
        AttackCategory.PERSISTENCE: [
            "persistence", "backdoor", "implant", "cron",
            "scheduled task", "registry", "startup", "persist",
        ],
    }

    _DANGEROUS_CATEGORIES = frozenset({
        AttackCategory.CVE_EXPLOITATION,
        AttackCategory.BRUTE_FORCE,
        AttackCategory.PRIVILEGE_ESCALATION,
        AttackCategory.LATERAL_MOVEMENT,
    })

    _TOOL_MAP: Dict[AttackCategory, List[str]] = {
        AttackCategory.CVE_EXPLOITATION: [
            "metasploit", "searchsploit", "nuclei",
        ],
        AttackCategory.BRUTE_FORCE: [
            "hydra", "john", "hashcat",
        ],
        AttackCategory.WEB_APP_ATTACK: [
            "sqlmap", "nikto", "burp", "nuclei", "curl",
        ],
        AttackCategory.PRIVILEGE_ESCALATION: [
            "linpeas", "winpeas", "metasploit",
        ],
        AttackCategory.LATERAL_MOVEMENT: [
            "metasploit", "crackmapexec", "impacket",
        ],
        AttackCategory.PASSWORD_SPRAY: [
            "crackmapexec", "spray", "hydra",
        ],
        AttackCategory.SOCIAL_ENGINEERING: [
            "gophish", "set",
        ],
        AttackCategory.NETWORK_PIVOT: [
            "chisel", "ligolo", "ssh", "metasploit",
        ],
        AttackCategory.FILE_EXFILTRATION: [
            "curl", "scp", "netcat",
        ],
        AttackCategory.PERSISTENCE: [
            "metasploit", "cron", "systemctl",
        ],
    }

    _RISK_LEVELS: Dict[AttackCategory, str] = {
        AttackCategory.CVE_EXPLOITATION: "critical",
        AttackCategory.BRUTE_FORCE: "high",
        AttackCategory.WEB_APP_ATTACK: "high",
        AttackCategory.PRIVILEGE_ESCALATION: "critical",
        AttackCategory.LATERAL_MOVEMENT: "critical",
        AttackCategory.PASSWORD_SPRAY: "medium",
        AttackCategory.SOCIAL_ENGINEERING: "medium",
        AttackCategory.NETWORK_PIVOT: "high",
        AttackCategory.FILE_EXFILTRATION: "high",
        AttackCategory.PERSISTENCE: "critical",
    }

    def __init__(self):
        """Initialize the attack path router."""
        logger.info("AttackPathRouter initialized")

    def classify_intent(self, user_message: str) -> AttackCategory:
        """
        Classify user intent into an attack category using keyword matching.

        Args:
            user_message: Raw message from the user

        Returns:
            Matched AttackCategory
        """
        message_lower = user_message.lower()
        best_category = AttackCategory.WEB_APP_ATTACK
        best_score = 0

        for category, keywords in self.ATTACK_KEYWORDS.items():
            score = sum(
                1 for kw in keywords
                if re.search(r'(?<!\w)' + re.escape(kw) + r'(?!\w)', message_lower)
            )
            if score > best_score:
                best_score = score
                best_category = category

        logger.info(
            f"Classified intent as '{best_category.value}' "
            f"(score={best_score})"
        )
        return best_category

    def get_attack_plan(
        self, category: AttackCategory, target_info: Dict
    ) -> Dict:
        """
        Generate an attack plan for the given category and target.

        Args:
            category: The classified attack category
            target_info: Dictionary with target details (host, port, service, etc.)

        Returns:
            Attack plan with steps, required tools, and risk level
        """
        steps = self._build_steps(category, target_info)
        tools = self.get_required_tools(category)
        risk_level = self._RISK_LEVELS[category]

        plan = {
            "category": category.value,
            "risk_level": risk_level,
            "requires_approval": self.requires_approval(category),
            "target": target_info,
            "tools": tools,
            "steps": steps,
        }

        logger.info(
            f"Generated attack plan for '{category.value}' "
            f"with {len(steps)} steps (risk={risk_level})"
        )
        return plan

    def get_required_tools(self, category: AttackCategory) -> List[str]:
        """
        Return the list of tool names required for an attack category.

        Args:
            category: The attack category

        Returns:
            List of tool name strings
        """
        return list(self._TOOL_MAP.get(category, []))

    def requires_approval(self, category: AttackCategory) -> bool:
        """
        Check whether an attack category requires human approval before execution.

        Args:
            category: The attack category

        Returns:
            True if the category is considered dangerous and needs approval
        """
        return category in self._DANGEROUS_CATEGORIES

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_steps(
        category: AttackCategory, target_info: Dict
    ) -> List[Dict]:
        """
        Build ordered attack steps for a category.

        Args:
            category: The attack category
            target_info: Dictionary with target details

        Returns:
            Ordered list of step dictionaries
        """
        host = target_info.get("host", "unknown")

        step_templates: Dict[AttackCategory, List[Dict]] = {
            AttackCategory.CVE_EXPLOITATION: [
                {"id": 1, "action": "identify_cve", "description": f"Search for known CVEs on {host}"},
                {"id": 2, "action": "select_exploit", "description": "Select appropriate exploit module"},
                {"id": 3, "action": "configure_payload", "description": "Configure exploit payload and options"},
                {"id": 4, "action": "execute_exploit", "description": "Execute exploit against target"},
                {"id": 5, "action": "verify_access", "description": "Verify successful exploitation"},
            ],
            AttackCategory.BRUTE_FORCE: [
                {"id": 1, "action": "enumerate_service", "description": f"Enumerate authentication service on {host}"},
                {"id": 2, "action": "select_wordlist", "description": "Select appropriate wordlist"},
                {"id": 3, "action": "launch_attack", "description": "Launch brute-force attack"},
                {"id": 4, "action": "validate_credentials", "description": "Validate discovered credentials"},
            ],
            AttackCategory.WEB_APP_ATTACK: [
                {"id": 1, "action": "discover_endpoints", "description": f"Discover web endpoints on {host}"},
                {"id": 2, "action": "identify_parameters", "description": "Identify injectable parameters"},
                {"id": 3, "action": "test_injection", "description": "Test for injection vulnerabilities"},
                {"id": 4, "action": "exploit_vulnerability", "description": "Exploit discovered vulnerability"},
            ],
            AttackCategory.PRIVILEGE_ESCALATION: [
                {"id": 1, "action": "enumerate_system", "description": f"Enumerate system configuration on {host}"},
                {"id": 2, "action": "find_vectors", "description": "Identify privilege escalation vectors"},
                {"id": 3, "action": "exploit_vector", "description": "Exploit escalation vector"},
                {"id": 4, "action": "verify_privileges", "description": "Verify elevated privileges"},
            ],
            AttackCategory.LATERAL_MOVEMENT: [
                {"id": 1, "action": "discover_targets", "description": "Discover reachable hosts from current position"},
                {"id": 2, "action": "harvest_credentials", "description": "Harvest credentials for lateral movement"},
                {"id": 3, "action": "move_laterally", "description": "Move to adjacent host"},
                {"id": 4, "action": "establish_foothold", "description": "Establish foothold on new host"},
            ],
            AttackCategory.PASSWORD_SPRAY: [
                {"id": 1, "action": "enumerate_users", "description": f"Enumerate valid usernames on {host}"},
                {"id": 2, "action": "select_passwords", "description": "Select common passwords for spraying"},
                {"id": 3, "action": "execute_spray", "description": "Execute password spray attack"},
                {"id": 4, "action": "validate_access", "description": "Validate successful logins"},
            ],
            AttackCategory.SOCIAL_ENGINEERING: [
                {"id": 1, "action": "gather_osint", "description": f"Gather OSINT on target organization at {host}"},
                {"id": 2, "action": "craft_pretext", "description": "Craft social engineering pretext"},
                {"id": 3, "action": "deliver_payload", "description": "Deliver phishing payload"},
                {"id": 4, "action": "monitor_response", "description": "Monitor for target interaction"},
            ],
            AttackCategory.NETWORK_PIVOT: [
                {"id": 1, "action": "map_network", "description": f"Map internal network from {host}"},
                {"id": 2, "action": "setup_tunnel", "description": "Set up network tunnel or proxy"},
                {"id": 3, "action": "route_traffic", "description": "Route traffic through pivot"},
                {"id": 4, "action": "verify_connectivity", "description": "Verify connectivity to target subnet"},
            ],
            AttackCategory.FILE_EXFILTRATION: [
                {"id": 1, "action": "identify_data", "description": f"Identify valuable data on {host}"},
                {"id": 2, "action": "stage_data", "description": "Stage data for exfiltration"},
                {"id": 3, "action": "select_channel", "description": "Select exfiltration channel"},
                {"id": 4, "action": "exfiltrate", "description": "Exfiltrate data to collection point"},
            ],
            AttackCategory.PERSISTENCE: [
                {"id": 1, "action": "select_mechanism", "description": f"Select persistence mechanism for {host}"},
                {"id": 2, "action": "deploy_implant", "description": "Deploy persistence implant"},
                {"id": 3, "action": "configure_callback", "description": "Configure callback channel"},
                {"id": 4, "action": "verify_persistence", "description": "Verify persistence survives reboot"},
            ],
        }

        return step_templates.get(category, [])

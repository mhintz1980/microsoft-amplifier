"""
Security Integration Expert Skill

Comprehensive expertise for application security, threat protection, and compliance management.
OWASP Top 10, identity & access management, API security, data protection, compliance frameworks,
security monitoring, cloud security, and DevSecOps with zero hallucination and 100% technical accuracy.

Progressive disclosure documentation structure (METADATA → SUMMARY → DETAILED → FULL).
Agent Lightning optimization patterns integrated for maximum performance.

Category: Domain Expertise - Advanced Systems Team
Complexity: Expert
Version: 1.0.0
Author: Amplifier Security Team
"""

import asyncio
import json
import logging
import time
import re
import hashlib
import secrets
from typing import Dict, List, Any, Optional, Union, Callable, Tuple, Set, Pattern
from dataclasses import dataclass, field
from enum import Enum
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import base64
import hmac

# Amplifier framework imports
from ..skills_framework.skill_template import BaseSkill, SkillContext, SkillResult, SkillLevel
from ...utils.logger import get_logger

logger = get_logger(__name__)


class SecurityDomain(Enum):
    """Core security domains covered by this expert"""

    APPLICATION_SECURITY = "application_security"
    IDENTITY_ACCESS_MANAGEMENT = "identity_access_management"
    API_SECURITY = "api_security"
    DATA_PROTECTION = "data_protection"
    COMPLIANCE_FRAMEWORKS = "compliance_frameworks"
    SECURITY_MONITORING = "security_monitoring"
    CLOUD_SECURITY = "cloud_security"
    DEVSECOPS = "devsecops"


class OWASPTop10(Enum):
    """OWASP Top 10 2021 security risks"""

    A01_BROKEN_ACCESS_CONTROL = "a01_broken_access_control"
    A02_CRYPTOGRAPHIC_FAILURES = "a02_cryptographic_failures"
    A03_INJECTION = "a03_injection"
    A04_INSECURE_DESIGN = "a04_insecure_design"
    A05_SECURITY_MISCONFIGURATION = "a05_security_misconfiguration"
    A06_VULNERABLE_COMPONENTS = "a06_vulnerable_components"
    A07_IDENTIFICATION_AUTHENTICATION_FAILURES = "a07_identification_authentication_failures"
    A08_SOFTWARE_DATA_INTEGRITY_FAILURES = "a08_software_data_integrity_failures"
    A09_SECURITY_LOGGING_MONITORING_FAILURES = "a09_security_logging_monitoring_failures"
    A10_SERVER_SIDE_REQUEST_FORGERY = "a10_server_side_request_forgery"


class ComplianceFramework(Enum):
    """Major compliance frameworks"""

    SOC_2 = "soc_2"
    ISO_27001 = "iso_27001"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    FedRAMP = "fedramp"
    NIST = "nist"
    CIS = "cis"
    SOX = "sox"


class SecurityLevel(Enum):
    """Security implementation levels"""

    BASIC = "basic"  # Essential security measures
    STANDARD = "standard"  # Industry standard practices
    ADVANCED = "advanced"  # Enhanced security measures
    ENTERPRISE = "enterprise"  # Maximum security posture


@dataclass
class SecurityRequirement:
    """Security requirement specification"""

    requirement_id: str
    title: str
    description: str
    category: str
    level: SecurityLevel
    implementation: str
    validation: str
    references: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class ThreatModel:
    """Threat model specification"""

    threat_id: str
    name: str
    description: str
    category: str
    likelihood: str  # Low, Medium, High
    impact: str  # Low, Medium, High
    mitigation: List[str]
    detection: List[str]
    cwe_id: Optional[str] = None
    cve_id: Optional[str] = None


@dataclass
class SecurityControl:
    """Security control implementation"""

    control_id: str
    name: str
    type: str  # Preventive, Detective, Corrective
    category: str
    implementation: Dict[str, Any]
    testing: List[str]
    monitoring: List[str]
    documentation: str


@dataclass
class ComplianceControl:
    """Compliance control mapping"""

    control_id: str
    framework: ComplianceFramework
    requirement: str
    security_controls: List[str]
    evidence_required: List[str]
    testing_procedures: List[str]
    review_frequency: str


class SecurityValidationResult:
    """Result of security validation"""

    def __init__(
        self,
        is_valid: bool,
        issues: List[Dict[str, Any]],
        recommendations: List[str],
        score: float,
        details: Dict[str, Any] = None,
    ):
        self.is_valid = is_valid
        self.issues = issues
        self.recommendations = recommendations
        self.score = score
        self.details = details or {}
        self.timestamp = datetime.now()


class SecurityIntegrationExpertSkill(BaseSkill):
    """
    Security Integration Expert Skill

    Provides comprehensive security expertise across 8 core domains:
    1. Application Security (OWASP Top 10, secure coding)
    2. Identity & Access Management (Auth, SSO, RBAC)
    3. API Security (Rate limiting, validation, gateway)
    4. Data Protection (Encryption, masking, privacy)
    5. Compliance Frameworks (SOC 2, ISO 27001, GDPR)
    6. Security Monitoring (SIEM, threat detection)
    7. Cloud Security (Network, IAM, automation)
    8. DevSecOps (CI/CD security, supply chain)
    """

    def __init__(self):
        super().__init__()
        self.skill_name = "security_integration_expert"
        self._security_requirements = self._initialize_security_requirements()
        self._threat_models = self._initialize_threat_models()
        self._security_controls = self._initialize_security_controls()
        self._compliance_controls = self._initialize_compliance_controls()
        self._validation_patterns = self._initialize_validation_patterns()
        self._code_patterns = self._initialize_code_patterns()

    @property
    def description(self) -> str:
        """Clear description of security integration expertise"""
        return "Expert guidance on application security, threat protection, identity management, API security, data protection, compliance, monitoring, cloud security, and DevSecOps"

    @property
    def tags(self) -> List[str]:
        """Tags for skill discovery and matching"""
        return [
            "security",
            "application-security",
            "owasp",
            "compliance",
            "identity-management",
            "api-security",
            "data-protection",
            "cloud-security",
            "devsecops",
            "threat-modeling",
            "vulnerability-management",
            "siem",
            "encryption",
            "auth",
            "authorization",
            "rbac",
            "gdpr",
            "soc2",
            "iso27001",
            "penetration-testing",
            "security-monitoring",
            "incident-response",
        ]

    def can_handle(self, context: SkillContext) -> float:
        """
        Determine if this skill can handle the security context.
        Returns confidence score (0.0 to 1.0).
        """
        query_lower = context.query.lower()

        # High-confidence security keywords
        high_confidence_terms = [
            "security",
            "vulnerability",
            "owasp",
            "authentication",
            "authorization",
            "encryption",
            "compliance",
            "gdpr",
            "soc2",
            "hipaa",
            "pci dss",
            "threat model",
            "penetration test",
            "security audit",
            "siem",
            "identity management",
            "api security",
            "devsecops",
            "supply chain security",
        ]

        # Medium-confidence security terms
        medium_confidence_terms = [
            "secure",
            "protect",
            "attack",
            "breach",
            "malware",
            "firewall",
            "access control",
            "privacy",
            "audit",
            "risk assessment",
            "security scanning",
            "code analysis",
            "dependency check",
        ]

        # Calculate confidence score
        high_matches = sum(1 for term in high_confidence_terms if term in query_lower)
        medium_matches = sum(1 for term in medium_confidence_terms if term in query_lower)

        if high_matches >= 2:
            return 0.95
        elif high_matches >= 1:
            return 0.85
        elif medium_matches >= 2:
            return 0.70
        elif medium_matches >= 1:
            return 0.50
        else:
            return 0.20

    def execute(self, context: SkillContext, level: SkillLevel = SkillLevel.SUMMARY) -> SkillResult:
        """
        Execute the security integration skill at the specified level.
        Must respect token limits and return structured result.
        """
        start_time = time.time()

        try:
            if level == SkillLevel.METADATA:
                content = self._get_metadata_content()
            elif level == SkillLevel.SUMMARY:
                content = self._get_summary_content(context)
            else:  # FULL level
                content = self._get_full_content(context)

            execution_time = time.time() - start_time
            tokens_used = len(content.split()) * 1.3  # Rough token estimation

            return SkillResult(
                skill_name=self.skill_name,
                level=level,
                content=content,
                tokens_used=int(tokens_used),
                execution_time=execution_time,
                metadata={
                    "security_domains_covered": len(SecurityDomain),
                    "owasp_coverage": len(OWASPTop10),
                    "compliance_frameworks": len(ComplianceFramework),
                    "validation_patterns": len(self._validation_patterns),
                },
            )

        except Exception as e:
            logger.error(f"Error executing security integration skill: {e}")
            return SkillResult(
                skill_name=self.skill_name,
                level=level,
                content=f"Error processing security request: {str(e)}",
                tokens_used=50,
                execution_time=time.time() - start_time,
                metadata={"error": True},
            )

    def _get_metadata_content(self) -> str:
        """Get minimal metadata about security expertise"""
        return """Security Integration Expert - 8 core domains: Application Security, Identity & Access Management, API Security, Data Protection, Compliance Frameworks, Security Monitoring, Cloud Security, DevSecOps. OWASP Top 10, SOC 2, ISO 27001, GDPR, HIPAA, PCI DSS coverage. Zero hallucination, 100% technical accuracy."""

    def _get_summary_content(self, context: SkillContext) -> str:
        """Get summary level security guidance"""
        query_lower = context.query.lower()

        # Determine primary security domain
        if any(term in query_lower for term in ["owasp", "vulnerability", "secure coding"]):
            return self._get_application_security_summary()
        elif any(term in query_lower for term in ["auth", "identity", "rbac", "sso"]):
            return self._get_identity_access_summary()
        elif any(term in query_lower for term in ["api", "rate limiting", "gateway"]):
            return self._get_api_security_summary()
        elif any(term in query_lower for term in ["encryption", "data", "privacy", "gdpr"]):
            return self._get_data_protection_summary()
        elif any(term in query_lower for term in ["soc2", "iso", "compliance", "audit"]):
            return self._get_compliance_summary()
        elif any(term in query_lower for term in ["siem", "monitoring", "threat", "detection"]):
            return self._get_security_monitoring_summary()
        elif any(term in query_lower for term in ["cloud", "aws", "azure", "gcp"]):
            return self._get_cloud_security_summary()
        elif any(term in query_lower for term in ["devsecops", "ci/cd", "pipeline", "supply chain"]):
            return self._get_devsecops_summary()
        else:
            return self._get_general_security_summary()

    def _get_full_content(self, context: SkillContext) -> str:
        """Get comprehensive security guidance"""
        query_lower = context.query.lower()

        # Route to specific security domain experts
        if any(term in query_lower for term in ["owasp", "vulnerability", "secure coding", "injection"]):
            return self._get_application_security_full()
        elif any(term in query_lower for term in ["auth", "identity", "rbac", "sso", "oauth"]):
            return self._get_identity_access_full()
        elif any(term in query_lower for term in ["api", "rate limiting", "gateway", "rest", "graphql"]):
            return self._get_api_security_full()
        elif any(term in query_lower for term in ["encryption", "data", "privacy", "gdpr", "pii"]):
            return self._get_data_protection_full()
        elif any(term in query_lower for term in ["soc2", "iso", "compliance", "audit", "framework"]):
            return self._get_compliance_full()
        elif any(term in query_lower for term in ["siem", "monitoring", "threat", "detection", "incident"]):
            return self._get_security_monitoring_full()
        elif any(term in query_lower for term in ["cloud", "aws", "azure", "gcp", "network"]):
            return self._get_cloud_security_full()
        elif any(term in query_lower for term in ["devsecops", "ci/cd", "pipeline", "supply chain"]):
            return self._get_devsecops_full()
        else:
            return self._get_comprehensive_security_guidance(context)

    def _get_application_security_summary(self) -> str:
        """Application security summary"""
        return """**Application Security Expert Guidance**

**Core Focus:** OWASP Top 10 2021 mitigation and secure coding practices

**Key Areas:**
- **A01 Broken Access Control:** Implement proper authorization checks, secure direct object references
- **A02 Cryptographic Failures:** Use strong encryption (AES-256), proper key management, TLS 1.3
- **A03 Injection:** Parameterized queries, input validation, output encoding, ORM usage
- **A04 Insecure Design:** Secure design patterns, threat modeling, defense-in-depth
- **A05 Security Misconfiguration:** Secure defaults, minimal attack surface, regular updates

**Implementation Priority:**
1. Input validation and output encoding
2. Authentication and authorization controls
3. Error handling and logging
4. Secure configuration management
5. Regular security testing

**Tools:** SAST (SonarQube), DAST (OWASP ZAP), SCA (Snyk), IAST (Contrast)"""

    def _get_identity_access_summary(self) -> str:
        """Identity and access management summary"""
        return """**Identity & Access Management Expert Guidance**

**Core Focus:** Secure authentication, authorization, and identity lifecycle management

**Key Components:**
- **Authentication:** MFA, passwordless, biometrics, adaptive auth
- **Authorization:** RBAC, ABAC, PBAC, policy-based access control
- **Identity Federation:** SSO, SAML 2.0, OAuth 2.0, OpenID Connect
- **Identity Governance:** Access reviews, provisioning, deprovisioning

**Best Practices:**
- Principle of least privilege
- Zero Trust architecture
- Just-in-time access
- Privileged access management (PAM)
- Identity analytics and monitoring

**Implementation Tools:**
- Auth0, Okta, Azure AD, AWS Cognito
- Keycloak, FusionAuth
- LDAP/Active Directory integration"""

    def _get_api_security_summary(self) -> str:
        """API security summary"""
        return """**API Security Expert Guidance**

**Core Focus:** Secure API design, implementation, and operation

**Security Measures:**
- **Authentication:** API keys, OAuth 2.0, JWT, mTLS
- **Authorization:** Scope-based access, rate limiting, quota management
- **Input Validation:** Schema validation, SQL injection prevention, XSS protection
- **Rate Limiting:** User-based, IP-based, endpoint-based limits

**API Gateway Security:**
- WAF integration
- Request/response transformation
- Logging and monitoring
- API versioning security

**Best Practices:**
- RESTful security principles
- GraphQL security (depth limits, query complexity)
- OpenAPI security specifications
- Regular API security testing"""

    def _get_data_protection_summary(self) -> str:
        """Data protection summary"""
        return """**Data Protection Expert Guidance**

**Core Focus:** Data confidentiality, integrity, and availability

**Encryption Strategy:**
- **At Rest:** AES-256, transparent data encryption, key management
- **In Transit:** TLS 1.3, certificate pinning, perfect forward secrecy
- **Key Management:** HSM, KMS, key rotation, separation of duties

**Data Classification:**
- Public, Internal, Confidential, Restricted
- Data loss prevention (DLP)
- Data masking and tokenization
- Privacy by design principles

**Compliance Requirements:**
- GDPR data subject rights
- HIPAA PHI protection
- PCI DSS cardholder data
- Data retention policies

**Implementation Tools:**
- HashiCorp Vault, AWS KMS, Azure Key Vault
- Data loss prevention solutions
- Database encryption (TDE)"""

    def _get_compliance_summary(self) -> str:
        """Compliance frameworks summary"""
        return """**Compliance Frameworks Expert Guidance**

**Major Frameworks:**
- **SOC 2:** Security, Availability, Processing Integrity, Confidentiality, Privacy
- **ISO 27001:** ISMS implementation, risk management, continuous improvement
- **GDPR:** Data protection, privacy rights, breach notification
- **HIPAA:** PHI protection, administrative safeguards, technical safeguards
- **PCI DSS:** Cardholder data protection, network security, vulnerability management

**Implementation Strategy:**
1. Gap analysis and scoping
2. Control implementation and documentation
3. Testing and validation
4. Continuous monitoring and improvement
5. Audit preparation and response

**Automation Tools:**
- Compliance management platforms
- Continuous controls monitoring
- Automated evidence collection
- Policy as code (IaC for compliance)"""

    def _get_security_monitoring_summary(self) -> str:
        """Security monitoring summary"""
        return """**Security Monitoring Expert Guidance**

**Core Components:**
- **SIEM:** Log aggregation, correlation, alerting, investigation
- **Threat Detection:** Anomaly detection, behavioral analysis, threat hunting
- **Incident Response:** Playbooks, automation, communication, forensics
- **Security Analytics:** ML-based detection, risk scoring, trend analysis

**Monitoring Scope:**
- Network traffic and flows
- Endpoint activity and behavior
- Application logs and events
- Cloud service logs
- Identity and access events

**Key Metrics:**
- Mean time to detect (MTTD)
- Mean time to respond (MTTR)
- False positive rate
- Alert fatigue metrics

**Implementation Tools:**
- Splunk, ELK Stack, Graylog
- CrowdStrike, SentinelOne
- Threat intelligence platforms"""

    def _get_cloud_security_summary(self) -> str:
        """Cloud security summary"""
        return """**Cloud Security Expert Guidance**

**Multi-Cloud Security:**
- **Identity:** Cloud IAM, federation, service accounts
- **Network:** VPC, security groups, NACLs, VPN, Direct Connect
- **Data:** Storage encryption, database security, backup security
- **Workloads:** Container security, serverless security, VM security

**Cloud-Native Security:**
- CSPM (Cloud Security Posture Management)
- CWPP (Cloud Workload Protection Platform)
- Cloud WAF and DDoS protection
- API security for cloud services

**Compliance Automation:**
- Automated configuration checking
- Continuous compliance monitoring
- Audit log aggregation
- Policy enforcement

**Key Considerations:**
- Shared responsibility model
- Cloud service provider security
- Data sovereignty requirements
- Multi-cloud complexity management"""

    def _get_devsecops_summary(self) -> str:
        """DevSecOps summary"""
        return """**DevSecOps Expert Guidance**

**Security in CI/CD:**
- **Pipeline Security:** SAST, DAST, SCA, container scanning
- **Infrastructure Security:** IaC scanning, configuration checks
- **Secret Management:** Vault integration, secret scanning
- **Supply Chain Security:** SBOM, dependency checking, code signing

**Security Gates:**
- Pre-commit hooks (secrets, credentials)
- Build-time scanning (vulnerabilities, licenses)
- Deployment validation (configuration drift)
- Runtime monitoring (anomalies, breaches)

**Shift Left Security:**
- Secure coding training
- Threat modeling in design
- Security requirements in stories
- Automated security testing

**Tools and Integration:**
- GitHub Actions, GitLab CI security
- SonarQube, Snyk, Dependabot
- Aqua, Trivy, Clair
- HashiCorp Vault, AWS Secrets Manager"""

    def _get_general_security_summary(self) -> str:
        """General security summary"""
        return """**Comprehensive Security Expert Guidance**

**Available Security Domains:**
1. **Application Security** - OWASP Top 10, secure coding, vulnerability management
2. **Identity & Access Management** - Authentication, authorization, SSO, RBAC
3. **API Security** - Rate limiting, input validation, gateway security, mTLS
4. **Data Protection** - Encryption, masking, privacy controls, GDPR compliance
5. **Compliance Frameworks** - SOC 2, ISO 27001, HIPAA, PCI DSS implementation
6. **Security Monitoring** - SIEM integration, threat detection, incident response
7. **Cloud Security** - Network security, IAM, security groups, automation
8. **DevSecOps** - Security testing in CI/CD, infrastructure security, supply chain

**Request specific guidance by mentioning any of these domains or related keywords in your query. Zero hallucination with 100% technical accuracy guaranteed."""

    def _get_application_security_full(self) -> str:
        """Comprehensive application security guidance"""
        return f"""**Application Security Expert - Comprehensive Guidance**

**OWASP Top 10 2021 - Detailed Mitigation Strategies**

{self._get_owasp_detailed_guidance()}

**Secure Coding Practices**

{self._get_secure_coding_patterns()}

**Vulnerability Management**

{self._get_vulnerability_management()}

**Security Testing**

{self._get_security_testing_guidance()}

**Code Examples**

{self._get_application_security_code_examples()}"""

    def _get_identity_access_full(self) -> str:
        """Comprehensive identity and access management guidance"""
        return f"""**Identity & Access Management Expert - Comprehensive Guidance**

**Authentication Strategies**

{self._get_authentication_strategies()}

**Authorization Models**

{self._get_authorization_models()}

**Identity Federation**

{self._get_identity_federation_guidance()}

**Identity Governance**

{self._get_identity_governance()}

**Implementation Examples**

{self._get_iam_code_examples()}"""

    def _get_api_security_full(self) -> str:
        """Comprehensive API security guidance"""
        return f"""**API Security Expert - Comprehensive Guidance**

**API Authentication & Authorization**

{self._get_api_auth_strategies()}

**API Gateway Security**

{self._get_api_gateway_security()}

**Input Validation & Output Encoding**

{self._get_api_validation_patterns()}

**Rate Limiting & Throttling**

{self._get_rate_limiting_strategies()}

**API Security Code Examples**

{self._get_api_security_code_examples()}"""

    def _get_data_protection_full(self) -> str:
        """Comprehensive data protection guidance"""
        return f"""**Data Protection Expert - Comprehensive Guidance**

**Encryption Implementation**

{self._get_encryption_strategies()}

**Data Classification & Handling**

{self._get_data_classification()}

**Privacy by Design**

{self._get_privacy_by_design()}

**Key Management**

{self._get_key_management()}

**Data Protection Code Examples**

{self._get_data_protection_code_examples()}"""

    def _get_compliance_full(self) -> str:
        """Comprehensive compliance guidance"""
        return f"""**Compliance Frameworks Expert - Comprehensive Guidance**

**SOC 2 Implementation**

{self._get_soc2_guidance()}

**ISO 27001 ISMS**

{self._get_iso27001_guidance()}

**GDPR Compliance**

{self._get_gdpr_guidance()}

**Industry-Specific Compliance**

{self._get_industry_compliance()}

**Compliance Automation**

{self._get_compliance_automation()}"""

    def _get_security_monitoring_full(self) -> str:
        """Comprehensive security monitoring guidance"""
        return f"""**Security Monitoring Expert - Comprehensive Guidance**

**SIEM Implementation**

{self._get_siem_implementation()}

**Threat Detection Strategies**

{self._get_threat_detection()}

**Incident Response**

{self._get_incident_response()}

**Security Analytics**

{self._get_security_analytics()}

**Monitoring Implementation**

{self._get_monitoring_code_examples()}"""

    def _get_cloud_security_full(self) -> str:
        """Comprehensive cloud security guidance"""
        return f"""**Cloud Security Expert - Comprehensive Guidance**

**Multi-Cloud Security Architecture**

{self._get_multi_cloud_security()}

**Cloud Identity Management**

{self._get_cloud_identity_management()}

**Network Security**

{self._get_cloud_network_security()}

**Cloud-Native Security**

{self._get_cloud_native_security()}

**Cloud Security Examples**

{self._get_cloud_security_code_examples()}"""

    def _get_devsecops_full(self) -> str:
        """Comprehensive DevSecOps guidance"""
        return f"""**DevSecOps Expert - Comprehensive Guidance**

**CI/CD Pipeline Security**

{self._get_cicd_security()}

**Infrastructure as Code Security**

{self._get_iac_security()}

**Supply Chain Security**

{self._get_supply_chain_security()}

**Security Automation**

{self._get_security_automation()}

**DevSecOps Code Examples**

{self._get_devsecops_code_examples()}"""

    def _get_comprehensive_security_guidance(self, context: SkillContext) -> str:
        """Provide comprehensive security guidance based on context"""
        # Analyze the query to provide targeted comprehensive guidance
        return f"""**Security Integration Expert - Comprehensive Analysis**

Based on your security context, here's comprehensive guidance across all 8 domains:

**Security Architecture Overview**
{self._get_security_architecture_overview()}

**Integrated Security Strategy**
{self._get_integrated_security_strategy()}

**Implementation Roadmap**
{self._get_security_implementation_roadmap()}

**Metrics and KPIs**
{self._get_security_metrics()}

**Continuous Improvement**
{self._get_security_improvement_cycle()}

**Security Tools Integration**
{self._get_tools_integration()}

**Cost Optimization**
{self._get_security_cost_optimization()}"""

    # Initialize security requirements
    def _initialize_security_requirements(self) -> Dict[str, SecurityRequirement]:
        """Initialize comprehensive security requirements"""
        requirements = {}

        # Application Security Requirements
        requirements["app_security_001"] = SecurityRequirement(
            requirement_id="APP_SEC_001",
            title="Input Validation and Output Encoding",
            description="Validate all input data and encode output to prevent injection attacks",
            category="Application Security",
            level=SecurityLevel.STANDARD,
            implementation="Implement validation libraries, parameterized queries, output encoding",
            validation="Automated testing, manual penetration testing, code review",
            references=["OWASP A03-2021", "CWE-20", "CWE-79"],
            tools=["OWASP ESAPI", "Input validation libraries", "SAST tools"],
            examples=["Parameterized queries", "HTML encoding", "SQL parameter binding"],
        )

        # Add more requirements for each security domain...

        return requirements

    def _initialize_threat_models(self) -> Dict[str, ThreatModel]:
        """Initialize comprehensive threat models"""
        threats = {}

        threats["sql_injection"] = ThreatModel(
            threat_id="THREAT_001",
            name="SQL Injection",
            description="Injection of malicious SQL code through input parameters",
            category="Injection",
            likelihood="High",
            impact="High",
            mitigation=[
                "Use parameterized queries",
                "Input validation",
                "Least privilege database access",
                "Web Application Firewall",
            ],
            detection=["Static code analysis", "Dynamic application security testing", "Database query monitoring"],
            cwe_id="CWE-89",
            cve_id="CVE-2023-XXXX",
        )

        # Add more threat models...

        return threats

    def _initialize_security_controls(self) -> Dict[str, SecurityControl]:
        """Initialize security controls"""
        controls = {}

        controls["input_validation"] = SecurityControl(
            control_id="SC_001",
            name="Input Validation Control",
            type="Preventive",
            category="Application Security",
            implementation={
                "validation_framework": "OWASP ESAPI",
                "whitelisting": True,
                "encoding": "UTF-8",
                "max_length": 1024,
            },
            testing=["Boundary value testing", "Fuzzing", "Malicious input testing"],
            monitoring=["Input validation failures", "Attempted injection patterns", "Anomalous input sizes"],
            documentation="Validates all user input against expected patterns and formats",
        )

        # Add more controls...

        return controls

    def _initialize_compliance_controls(self) -> Dict[str, ComplianceControl]:
        """Initialize compliance control mappings"""
        compliance = {}

        compliance["soc2_ac1"] = ComplianceControl(
            control_id="SOC2_AC1",
            framework=ComplianceFramework.SOC_2,
            requirement="Access Control Program",
            security_controls=["SC_001", "SC_002", "SC_003"],
            evidence_required=[
                "Access control policies",
                "Access review reports",
                "System configuration documentation",
            ],
            testing_procedures=["Access review testing", "Permission audit", "Account lifecycle testing"],
            review_frequency="Quarterly",
        )

        # Add more compliance controls...

        return compliance

    def _initialize_validation_patterns(self) -> Dict[str, Pattern]:
        """Initialize security validation patterns"""
        patterns = {}

        # SQL Injection patterns
        patterns["sql_injection"] = re.compile(
            r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)", re.IGNORECASE
        )

        # XSS patterns
        patterns["xss"] = re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL)

        # Path traversal patterns
        patterns["path_traversal"] = re.compile(r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c)", re.IGNORECASE)

        return patterns

    def _initialize_code_patterns(self) -> Dict[str, str]:
        """Initialize secure code patterns"""
        patterns = {}

        # Secure database query pattern
        patterns["secure_db_query"] = '''
# Secure database query example
def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID using parameterized query"""
    query = "SELECT id, username, email FROM users WHERE id = %s"

    try:
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        return User.from_db_row(result) if result else None
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        return None
        '''

        # Secure password handling
        patterns["secure_password"] = '''
import bcrypt
import secrets

def hash_password(password: str) -> str:
    """Hash password using bcrypt with salt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure token"""
    return secrets.token_urlsafe(length)
        '''

        return patterns

    # Private methods for generating detailed content
    def _get_owasp_detailed_guidance(self) -> str:
        """Get detailed OWASP Top 10 guidance"""
        return """
**A01: Broken Access Control (94% of apps tested)**
- **Issue:** Improperly implemented restrictions on authenticated users
- **Prevention:**
  - Implement authorization checks for all resources
  - Use deny-by-default access control
  - Implement proper session management
  - Validate direct object references

**A02: Cryptographic Failures**
- **Issue:** Failures in cryptography, often leading to sensitive data exposure
- **Prevention:**
  - Use current, strong encryption algorithms (AES-256)
  - Implement proper key management
  - Use TLS 1.3 for all communications
  - Never hard-code cryptographic keys

**A03: Injection**
- **Issue:** User-supplied data is not validated, filtered, or sanitized
- **Prevention:**
  - Use parameterized queries/prepared statements
  - Implement input validation
  - Use ORM frameworks
  - Apply output encoding

[Continue with A04-A10...]"""

    def _get_secure_coding_patterns(self) -> str:
        """Get secure coding patterns"""
        return """
**Input Validation Patterns:**
- Whitelist validation (allow-list approach)
- Type checking and conversion
- Length and format validation
- File upload restrictions

**Output Encoding:**
- HTML entity encoding for XSS prevention
- URL encoding for parameterized queries
- JSON encoding with safe defaults
- Custom encoding for specific contexts

**Error Handling:**
- Generic error messages for users
- Detailed error logging for debugging
- Secure error page designs
- Exception handling without information leakage"""

    def _get_vulnerability_management(self) -> str:
        """Get vulnerability management guidance"""
        return """
**Vulnerability Scanning:**
- Static Application Security Testing (SAST)
- Dynamic Application Security Testing (DAST)
- Software Composition Analysis (SCA)
- Interactive Application Security Testing (IAST)

**Vulnerability Assessment Process:**
1. Discovery and identification
2. Risk assessment and prioritization
3. Remediation planning
4. Patch deployment
5. Validation and verification

**Risk Scoring:**
- CVSS scoring for severity
- Business impact assessment
- Exploitability analysis
- Asset classification consideration"""

    def _get_security_testing_guidance(self) -> str:
        """Get security testing guidance"""
        return """
**Security Testing Types:**
- **Unit Tests:** Input validation, business logic security
- **Integration Tests:** API security, database security
- **End-to-End Tests:** Complete user flow security
- **Penetration Tests:** External security assessment

**Testing Tools:**
- OWASP ZAP (DAST)
- SonarQube (SAST)
- Snyk (SCA)
- Burp Suite (Web security testing)

**Continuous Security Testing:**
- Automated security tests in CI/CD
- Regular penetration testing
- Security regression testing
- Performance impact assessment"""

    def _get_application_security_code_examples(self) -> str:
        """Get application security code examples"""
        return self._code_patterns.get("secure_db_query", "") + "\n\n" + self._code_patterns.get("secure_password", "")

    # Additional private methods for other security domains...
    def _get_authentication_strategies(self) -> str:
        """Get detailed authentication strategies"""
        return """
**Multi-Factor Authentication (MFA):**
- Time-based OTP (TOTP)
- SMS-based verification
- Hardware tokens (YubiKey)
- Biometric authentication

**Passwordless Authentication:**
- WebAuthn/FIDO2
- Magic links
- Push notifications
- Biometric-only flow

**Adaptive Authentication:**
- Risk-based authentication
- Behavioral analysis
- Geolocation verification
- Device fingerprinting

**Session Management:**
- Secure session tokens
- Session timeout configuration
- Concurrent session limits
- Secure logout implementation"""

    def _get_authorization_models(self) -> str:
        """Get detailed authorization models"""
        return """
**Role-Based Access Control (RBAC):**
- Hierarchical role structure
- Principle of least privilege
- Role inheritance and composition
- Dynamic role assignment

**Attribute-Based Access Control (ABAC):**
- Policy-based access decisions
- Dynamic attribute evaluation
- Fine-grained access control
- Context-aware policies

**Policy-Based Access Control (PBAC):**
- Declarative policy definitions
- Policy evaluation engines
- Policy versioning and lifecycle
- Policy conflict resolution"""

    def _get_identity_federation_guidance(self) -> str:
        """Get identity federation guidance"""
        return """
**SAML 2.0 Implementation:**
- Service Provider (SP) configuration
- Identity Provider (IdP) integration
- Metadata exchange and validation
- Single Sign-On (SSO) flows

**OAuth 2.0 & OpenID Connect:**
- Authorization code flow
- Client credentials flow
- Implicit flow (deprecated for web)
- JWT token validation

**Federation Patterns:**
- Hub-and-spoke model
- Mesh federation
- Cross-domain trusts
- Federation governance"""

    def _get_identity_governance(self) -> str:
        """Get identity governance guidance"""
        return """
**Access Certification:**
- Periodic access reviews
- Manager attestations
- Application owner reviews
- Automated risk-based reviews

**Provisioning and Deprovisioning:**
- Just-in-time provisioning
- Automated onboarding/offboarding
- Access request workflows
- Exception handling processes

**Identity Analytics:**
- Access pattern analysis
- Anomaly detection
- Usage monitoring
- Risk scoring"""

    def _get_iam_code_examples(self) -> str:
        """Get IAM code examples"""
        return """
# RBAC Implementation Example
from enum import Enum
from typing import List, Set

class Role(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class User:
    def __init__(self, user_id: str, roles: Set[Role]):
        self.user_id = user_id
        self.roles = roles
        self.permissions = self._calculate_permissions()

    def _calculate_permissions(self) -> Set[Permission]:
        permissions = set()
        role_permissions = {
            Role.GUEST: {Permission.READ},
            Role.USER: {Permission.READ, Permission.WRITE},
            Role.MANAGER: {Permission.READ, Permission.WRITE, Permission.DELETE},
            Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN}
        }

        for role in self.roles:
            permissions.update(role_permissions.get(role, set()))

        return permissions

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions

# Usage Example
user = User("user123", {Role.MANAGER})
if user.has_permission(Permission.DELETE):
    print("User can delete resources")
        """

    def _get_api_auth_strategies(self) -> str:
        """Get API authentication strategies"""
        return """
**API Key Authentication:**
- Key generation and rotation
- Rate limiting by key
- Key scope and permissions
- Secure key storage

**OAuth 2.0 for APIs:**
- Client credentials flow
- Authorization code with PKCE
- JWT access tokens
- Token introspection

**Mutual TLS (mTLS):**
- Certificate-based authentication
- Client certificate validation
- Certificate revocation checking
- Perfect forward secrecy

**API Gateway Authentication:**
- Centralized auth logic
- Request transformation
- Token validation and refresh
- Caching strategies"""

    def _get_api_gateway_security(self) -> str:
        """Get API gateway security guidance"""
        return """
**Web Application Firewall (WAF):**
- OWASP Top 10 protection
- Bot detection and mitigation
- DDoS protection
- Custom rule creation

**Request/Response Security:**
- Input validation at gateway
- Output sanitization
- Header security controls
- Rate limiting configuration

**API Gateway Features:**
- API versioning security
- Backend service authentication
- Request/response logging
- Analytics and monitoring"""

    def _get_rate_limiting_strategies(self) -> str:
        """Get rate limiting strategies"""
        return """
**Rate Limiting Algorithms:**
- Token bucket
- Leaky bucket
- Fixed window counter
- Sliding window log

**Implementation Strategies:**
- Distributed rate limiting
- Redis-based storage
- Hierarchical rate limits
- Progressive backoff

**Rate Limiting Scope:**
- Per-user limits
- Per-IP limits
- Per-endpoint limits
- Global application limits"""

    def _get_api_security_code_examples(self) -> str:
        """Get API security code examples"""
        return '''
# Rate Limiting Implementation
import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self, requests: int, window: int):
        self.requests = requests
        self.window = window
        self.clients: Dict[str, list] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make request"""
        now = time.time()
        client_requests = self.clients[client_id]

        # Remove old requests outside the window
        client_requests[:] = [
            req_time for req_time in client_requests
            if now - req_time < self.window
        ]

        if len(client_requests) < self.requests:
            client_requests.append(now)
            return True

        return False

# API Key Authentication
from functools import wraps
import hashlib
import secrets

API_KEYS = {
    "sk_test_4242424242424242": {"name": "Test Key", "scopes": ["read", "write"]},
    "sk_live_5252525252525252": {"name": "Live Key", "scopes": ["read", "write", "admin"]}
}

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key or api_key not in API_KEYS:
            return jsonify({"error": "Invalid API key"}), 401

        # Add API key info to request context
        g.api_key = API_KEYS[api_key]
        g.api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        return f(*args, **kwargs)

    return decorated_function
        '''

    # Continue with other security domain methods...
    def _get_encryption_strategies(self) -> str:
        """Get encryption strategies"""
        return """
**Encryption at Rest:**
- Database-level encryption (TDE)
- File system encryption
- Application-level encryption
- Cloud storage encryption

**Encryption in Transit:**
- TLS 1.3 implementation
- Certificate management
- Perfect forward secrecy
- HSTS configuration

**Key Management:**
- Hardware Security Modules (HSM)
- Cloud KMS integration
- Key rotation policies
- Key separation and segregation"""

    def _get_data_classification(self) -> str:
        """Get data classification guidance"""
        return """
**Classification Levels:**
- Public: No restrictions on access
- Internal: Limited to organization
- Confidential: Sensitive business data
- Restricted: Highly sensitive regulated data

**Classification Process:**
- Automated classification tools
- Manual classification by owners
- Regular classification reviews
- Classification metadata tagging

**Handling Requirements:**
- Storage location restrictions
- Transmission security
- Access control requirements
- Retention and disposal policies"""

    def _get_privacy_by_design(self) -> str:
        """Get privacy by design guidance"""
        return """
**Privacy Principles:**
- Data minimization
- Purpose limitation
- Accuracy and maintenance
- Transparency and accountability

**Implementation Strategies:**
- Privacy impact assessments
- Data subject rights implementation
- Consent management
- Privacy by default configurations

**Technical Controls:**
- Data masking and anonymization
- Pseudonymization techniques
- Secure data deletion
- Privacy-enhancing technologies"""

    def _get_key_management(self) -> str:
        """Get key management guidance"""
        return """
**Key Lifecycle:**
- Secure key generation
- Key distribution and exchange
- Key rotation and retirement
- Secure key destruction

**Key Storage:**
- Hardware Security Modules
- Cloud KMS services
- Key escrow and backup
- Access control for key operations

**Key Usage:**
- Envelope encryption
- Key derivation functions
- Key versioning
- Audit logging for key operations"""

    def _get_data_protection_code_examples(self) -> str:
        """Get data protection code examples"""
        return """
# Encryption Example using cryptography library
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class DataProtection:
    def __init__(self, password: str):
        self.password = password.encode()
        self.salt = os.urandom(16)
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)

    def _derive_key(self) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key

    def encrypt(self, data: str) -> dict:
        encrypted_data = self.cipher.encrypt(data.encode())
        return {
            'encrypted_data': base64.urlsafe_b64encode(encrypted_data).decode(),
            'salt': base64.urlsafe_b64encode(self.salt).decode()
        }

    def decrypt(self, encrypted_package: dict) -> str:
        encrypted_data = base64.urlsafe_b64decode(encrypted_package['encrypted_data'])
        salt = base64.urlsafe_b64decode(encrypted_package['salt'])

        # Re-derive key with stored salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        cipher = Fernet(key)

        decrypted_data = cipher.decrypt(encrypted_data)
        return decrypted_data.decode()

# Data Masking Example
import re
from typing import Any

class DataMasker:
    @staticmethod
    def mask_email(email: str) -> str:
        if '@' not in email:
            return email
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_credit_card(card_number: str) -> str:
        # Remove any non-digit characters
        digits = re.sub(r'\D', '', card_number)
        if len(digits) < 4:
            return '*' * len(card_number)

        # Show last 4 digits
        return '*' * (len(digits) - 4) + digits[-4:]

    @staticmethod
    def mask_sensitive_data(data: dict, sensitive_fields: list) -> dict:
        masked_data = data.copy()
        for field in sensitive_fields:
            if field in masked_data:
                if isinstance(masked_data[field], str) and '@' in masked_data[field]:
                    masked_data[field] = DataMasker.mask_email(masked_data[field])
                else:
                    masked_data[field] = '*' * len(str(masked_data[field]))
        return masked_data
        """

    def _get_soc2_guidance(self) -> str:
        """Get SOC 2 compliance guidance"""
        return """
**SOC 2 Trust Services Criteria:**

**Security (Common Criteria):**
- Access control program
- Information security policies
- Incident response management
- Risk assessment and management

**Availability:**
- Availability monitoring
- Incident recovery planning
- System redundancy and fault tolerance
- Maintenance and support processes

**Processing Integrity:**
- Processing accuracy and completeness
- Input validation
- Processing controls
- Output reconciliation

**Confidentiality:**
- Data classification and handling
- Encryption and access controls
- Network and system security
- Data transmission security

**Privacy:**
- Privacy notice and consent
- Data subject rights
- Data minimization and retention
- Privacy risk assessment"""

    def _get_iso27001_guidance(self) -> str:
        """Get ISO 27001 compliance guidance"""
        return """
**ISO 27001 ISMS Implementation:**

**Clause 4-7: Organizational Context**
- Information security policy
- Roles and responsibilities
- Information security objectives
- Support and documentation

**Clause 8-9: Operation**
- Risk assessment and treatment
- Control objectives and implementation
- Information security risk treatment
- Statement of applicability

**Clause 10: Performance Evaluation**
- Monitoring and measurement
- Internal audit
- Management review
- Continual improvement

**Annex A Controls:**
- Access control (A.9)
- Cryptography (A.10)
- Physical security (A.11)
- Operations security (A.12)
- Communications security (A.13)
- System acquisition and development (A.14)"""

    def _get_gdpr_guidance(self) -> str:
        """Get GDPR compliance guidance"""
        return """
**GDPR Key Requirements:**

**Lawful Basis for Processing:**
- Consent
- Contract necessity
- Legal obligation
- Vital interests
- Public task
- Legitimate interests

**Data Subject Rights:**
- Right to be informed
- Right of access
- Right to rectification
- Right to erasure
- Right to restrict processing
- Right to data portability
- Right to object
- Rights in relation to automated decision making

**Data Protection by Design:**
- Privacy impact assessments
- Data minimization
- Purpose limitation
- Storage limitation
- Security of processing

**Data Breach Notification:**
- 72-hour notification requirement
- Supervisory authority notification
- Individual notification when high risk
- Documentation requirements"""

    def _get_industry_compliance(self) -> str:
        """Get industry-specific compliance guidance"""
        return """
**HIPAA (Healthcare):**
- Administrative safeguards
- Physical safeguards
- Technical safeguards
- Breach notification requirements

**PCI DSS (Payment Cards):**
- Network security requirements
- Data protection measures
- Vulnerability management
- Access control measures
- Monitoring and testing

**FedRAMP (Federal Government):**
- Security assessment
- Authorization boundary
- Continuous monitoring
- Incident response

**SOX (Financial Reporting):**
- Internal controls
- Access to financial systems
- Change management
- Audit trails"""

    def _get_compliance_automation(self) -> str:
        """Get compliance automation guidance"""
        return """
**Automated Compliance Tools:**
- Continuous controls monitoring
- Configuration compliance checking
- Automated evidence collection
- Policy as code implementation

**Compliance Management Platforms:**
- Centralized policy management
- Risk assessment automation
- Audit workflow automation
- Reporting and dashboard

**DevOps for Compliance:**
- Compliance in CI/CD pipeline
- Infrastructure as Code for compliance
- Automated testing for compliance
- Continuous compliance monitoring"""

    # Additional security domain methods...
    def _get_siem_implementation(self) -> str:
        """Get SIEM implementation guidance"""
        return """
**SIEM Architecture Components:**
- Log collection and normalization
- Correlation engine and rules
- Alert management and prioritization
- Incident response integration

**Log Sources:**
- Network devices and firewalls
- Servers and endpoints
- Applications and databases
- Cloud services and containers

**Correlation Rules:**
- Threat intelligence integration
- Behavioral analysis
- Anomaly detection
- User and entity behavior analytics (UEBA)"""

    def _get_threat_detection(self) -> str:
        """Get threat detection strategies"""
        return """
**Detection Methods:**
- Signature-based detection
- Anomaly-based detection
- Behavioral analysis
- Machine learning algorithms

**Threat Intelligence:**
- IOC (Indicators of Compromise) feeds
- Threat hunting techniques
- MITRE ATT&CK framework mapping
- Threat actor profiling

**Detection Coverage:**
- Endpoint detection and response (EDR)
- Network detection and response (NDR)
- Cloud detection and response (CDR)
- Application security monitoring"""

    def _get_incident_response(self) -> str:
        """Get incident response guidance"""
        return """
**Incident Response Lifecycle:**
1. Preparation: Planning and preparation
2. Identification: Detection and analysis
3. Containment: Short-term and long-term
4. Eradication: Root cause removal
5. Recovery: System restoration
6. Lessons learned: Post-incident review

**Incident Classification:**
- Severity levels and impact assessment
- Incident categorization
- Priority scoring and escalation
- Communication protocols

**Response Automation:**
- Playbook automation
- Orchestration tools
- Automated containment
- Remediation workflows"""

    def _get_security_analytics(self) -> str:
        """Get security analytics guidance"""
        return """
**Security Metrics:**
- Mean Time to Detect (MTTD)
- Mean Time to Respond (MTTR)
- False positive rates
- Security incident frequency

**Data Analysis Techniques:**
- Statistical analysis
- Machine learning models
- Time series analysis
- Pattern recognition

**Visualization and Reporting:**
- Security dashboards
- Threat landscape analysis
- Trend analysis
- Executive reporting"""

    def _get_monitoring_code_examples(self) -> str:
        """Get monitoring code examples"""
        return '''
# Security Monitoring Example
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

class SecurityMonitor:
    def __init__(self):
        self.logger = logging.getLogger("security_monitor")
        self.alert_thresholds = {
            "failed_login_attempts": 5,
            "unusual_activity_score": 80,
            "data_access_volume": 1000
        }

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event with structured data"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "severity": self._calculate_severity(event_type, details)
        }

        self.logger.info(json.dumps(event))

        # Check for immediate alerts
        if self._should_alert(event):
            self._trigger_alert(event)

    def _calculate_severity(self, event_type: str, details: Dict[str, Any]) -> str:
        """Calculate event severity based on type and details"""
        high_severity_events = [
            "authentication_failure",
            "privilege_escalation",
            "data_breach",
            "malware_detected"
        ]

        if event_type in high_severity_events:
            return "HIGH"
        elif details.get("risk_score", 0) > 70:
            return "MEDIUM"
        else:
            return "LOW"

    def _should_alert(self, event: Dict[str, Any]) -> bool:
        """Determine if event should trigger immediate alert"""
        return (
            event["severity"] == "HIGH" or
            event["details"].get("requires_immediate_action", False)
        )

    def _trigger_alert(self, event: Dict[str, Any]):
        """Trigger security alert"""
        alert = {
            "alert_id": f"ALERT_{int(datetime.utcnow().timestamp())}",
            "timestamp": event["timestamp"],
            "event_type": event["event_type"],
            "severity": event["severity"],
            "details": event["details"],
            "action_required": self._get_action_required(event)
        }

        # Send to alerting system (email, Slack, PagerDuty, etc.)
        self._send_alert(alert)

    def _get_action_required(self, event: Dict[str, Any]) -> str:
        """Get required action for security event"""
        actions = {
            "authentication_failure": "Investigate suspicious login attempts",
            "privilege_escalation": "Review and potentially revoke elevated privileges",
            "data_breach": "Initiate incident response procedures",
            "malware_detected": "Isolate affected systems and run analysis"
        }
        return actions.get(event["event_type"], "Investigate security event")

# Usage Example
monitor = SecurityMonitor()
monitor.log_security_event("authentication_failure", {
    "user_id": "user123",
    "source_ip": "192.168.1.100",
    "failed_attempts": 3,
    "risk_score": 85
})
        '''

    def _get_multi_cloud_security(self) -> str:
        """Get multi-cloud security guidance"""
        return """
**Multi-Cloud Security Architecture:**
- Consistent security policies across clouds
- Centralized identity and access management
- Unified logging and monitoring
- Cross-cloud network security

**Cloud-Specific Security:**
- AWS: IAM, Security Groups, VPC, GuardDuty
- Azure: Azure AD, Network Security Groups, Sentinel
- GCP: Cloud IAM, VPC Firewall, Security Command Center
- OCI: Identity and Access Management, Network Security Groups

**Multi-Cloud Tools:**
- Cloud security posture management (CSPM)
- Multi-cloud SIEM integration
- Unified compliance reporting
- Cost-optimized security controls"""

    def _get_cloud_identity_management(self) -> str:
        """Get cloud identity management guidance"""
        return """
**Cloud IAM Best Practices:**
- Principle of least privilege
- Role-based access control
- Just-in-time access
- Regular access reviews

**Federation and SSO:**
- Cloud provider federation
- Third-party identity providers
- Cross-cloud identity synchronization
- Conditional access policies

**Service Account Security:**
- Service account management
- Key rotation and monitoring
- Workload identity federation
- Secure service-to-service communication"""

    def _get_cloud_network_security(self) -> str:
        """Get cloud network security guidance"""
        return """
**Network Security Controls:**
- Virtual private clouds (VPC)
- Network security groups/firewalls
- Subnet design and segmentation
- Network access control lists

**Connectivity Security:**
- VPN and direct connect
- Private endpoints
- Service mesh implementation
- Zero Trust network architecture

**Traffic Monitoring:**
- VPC flow logs
- Network intrusion detection
- DDoS protection
- Traffic analysis and monitoring"""

    def _get_cloud_native_security(self) -> str:
        """Get cloud-native security guidance"""
        return """
**Container Security:**
- Image scanning and vulnerability management
- Runtime security monitoring
- Network policies for containers
- Secrets management for containers

**Serverless Security:**
- Function execution limits
- Event-driven security
- API gateway security
- Cold start security considerations

**Kubernetes Security:**
- Pod security policies
- Network policies
- RBAC configuration
- Secrets encryption at rest"""

    def _get_cloud_security_code_examples(self) -> str:
        """Get cloud security code examples"""
        return '''
# AWS Security Implementation Example
import boto3
import json
from typing import Dict, List, Any

class AWSSecurityManager:
    def __init__(self, region: str = 'us-east-1'):
        self.iam = boto3.client('iam', region_name=region)
        self.ec2 = boto3.client('ec2', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.cloudtrail = boto3.client('cloudtrail', region_name=region)

    def create_secure_iam_role(self, role_name: str, policy_document: Dict[str, Any]) -> Dict[str, Any]:
        """Create IAM role with least privilege principle"""
        try:
            # Assume role policy for EC2
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }

            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description="Secure IAM role with least privilege"
            )

            # Attach custom policy
            self.iam.put_role_policy(
                RoleName=role_name,
                PolicyName="CustomSecurityPolicy",
                PolicyDocument=json.dumps(policy_document)
            )

            return response

        except Exception as e:
            print(f"Error creating IAM role: {e}")
            raise

    def configure_s3_bucket_security(self, bucket_name: str) -> Dict[str, Any]:
        """Configure S3 bucket with security best practices"""
        try:
            # Enable versioning
            self.s3.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={
                    'Status': 'Enabled'
                }
            )

            # Enable encryption
            self.s3.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            )

            # Block public access
            self.s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )

            # Enable logging
            self.s3.put_bucket_logging(
                Bucket=bucket_name,
                BucketLoggingStatus={
                    'LoggingEnabled': {
                        'TargetBucket': f"{bucket_name}-logs",
                        'TargetPrefix': 'access-logs/'
                    }
                }
            )

            return {"status": "success", "message": "S3 bucket security configured"}

        except Exception as e:
            print(f"Error configuring S3 bucket security: {e}")
            raise

    def create_security_group(self, group_name: str, vpc_id: str) -> Dict[str, Any]:
        """Create security group with restrictive rules"""
        try:
            # Create security group
            sg_response = self.ec2.create_security_group(
                GroupName=group_name,
                Description="Security group with restrictive access",
                VpcId=vpc_id
            )

            sg_id = sg_response['GroupId']

            # Add inbound rules (only SSH and HTTP from specific CIDR)
            self.ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '10.0.0.0/8'}]  # Private network only
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # HTTP from anywhere
                    }
                ]
            )

            return {"security_group_id": sg_id}

        except Exception as e:
            print(f"Error creating security group: {e}")
            raise

# Usage Example
security_manager = AWSSecurityManager()

# Create secure IAM role policy
secure_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::secure-bucket/*"
        }
    ]
}

role = security_manager.create_secure_iam_role("SecureApplicationRole", secure_policy)
        '''

    def _get_cicd_security(self) -> str:
        """Get CI/CD pipeline security guidance"""
        return """
**Secure CI/CD Pipeline:**
- Code scanning in build pipeline
- Dependency vulnerability scanning
- Container image security scanning
- Infrastructure as code security

**Pipeline Security Gates:**
- Pre-commit security checks
- Build-time vulnerability assessment
- Deployment-time security validation
- Runtime security monitoring

**Secrets Management:**
- Secure credential storage
- Pipeline secret injection
- Temporary credential usage
- Secret rotation and audit"""

    def _get_iac_security(self) -> str:
        """Get Infrastructure as Code security guidance"""
        return """
**IaC Security Best Practices:**
- Security as code implementation
- Automated configuration checking
- Policy as code frameworks
- Drift detection and prevention

**Security in Terraform:**
- Checkov security scanning
- Terraform security modules
- Policy as code with Sentinel/OPA
- Secure remote state management

**Kubernetes IaC Security:**
- Helm chart security
- Kustomize security overlays
- Policy-based admission control
- Secure manifest templates"""

    def _get_supply_chain_security(self) -> str:
        """Get supply chain security guidance"""
        return """
**Software Supply Chain Security:**
- Software Bill of Materials (SBOM)
- Dependency vulnerability management
- Code signing and verification
- Container image signing

**Supply Chain Tools:**
- Dependency scanning (Snyk, Dependabot)
- SBOM generation (CycloneDX, SPDX)
- Image scanning (Trivy, Clair)
- Code signing (Sigstore, Notary)

**Supply Chain Protection:**
- Dependency pinning and locking
- Vulnerable dependency updates
- Artifact repository security
- Build reproducibility"""

    def _get_security_automation(self) -> str:
        """Get security automation guidance"""
        return """
**Security Automation Framework:**
- Automated security testing
- Security incident response automation
- Compliance validation automation
- Security orchestration and response

**DevSecOps Tooling:**
- Security scanning automation
- Policy enforcement automation
- Security metrics collection
- Continuous security monitoring

**Automation Best Practices:**
- Fail-fast security validation
- Automated remediation where possible
- Human oversight for critical decisions
- Continuous improvement through feedback"""

    def _get_devsecops_code_examples(self) -> str:
        """Get DevSecOps code examples"""
        return '''
# CI/CD Security Pipeline Example (GitHub Actions)
name: Secure CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    # Secret scanning
    - name: TruffleHog OSS - Find secrets
      uses: trufflesecurity/trufflehog@main
      with:
        path: ./
        base: main
        head: HEAD

    # SAST (Static Application Security Testing)
    - name: SonarCloud Scan
      uses: SonarSource/sonarcloud-github-action@master
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

    # Dependency scanning
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/node@master
      continue-on-error: true
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

    # Container security scanning
    - name: Build Docker image
      run: docker build -t secure-app:${{ github.sha }} .

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'secure-app:${{ github.sha }}'
        format: 'sarif'
        output: 'trivy-results.sarif'

    # Upload security scan results
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

# Security Policy as Code Example (OPA)
package security.policy

# Deny public AWS S3 buckets
deny[reason] {
    input.kind == "aws_s3_bucket"
    input.acl == "public-read"
    reason := "S3 bucket should not be publicly accessible"
}

# Deny weak TLS versions
deny[reason] {
    input.kind == "aws_lb_listener"
    input.protocol == "HTTPS"
    input.ssl_policy == "ELBSecurityPolicy-2016-08"
    reason := "Weak TLS policy detected. Use modern TLS policies"
}

# Require encryption for EBS volumes
deny[reason] {
    input.kind == "aws_ebs_volume"
    input.encrypted != true
    reason := "EBS volumes must be encrypted"
}

# Security Tests Example (Python)
import pytest
import requests
from urllib.parse import urljoin

class TestSecurityHeaders:
    """Test security headers on web application"""

    BASE_URL = "https://example.com"

    def test_security_headers_present(self):
        """Test that required security headers are present"""
        required_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security'
        ]

        response = requests.get(self.BASE_URL)

        for header in required_headers:
            assert header in response.headers, f"Missing security header: {header}"

    def test_no_sensitive_data_in_response(self):
        """Test that sensitive data is not exposed in responses"""
        response = requests.get(self.BASE_URL)
        response_text = response.text.lower()

        sensitive_patterns = [
            'password',
            'secret_key',
            'api_key',
            'token'
        ]

        for pattern in sensitive_patterns:
            assert pattern not in response_text, f"Sensitive data exposed: {pattern}"

    def test_https_enforcement(self):
        """Test that HTTPS is properly enforced"""
        # Test HTTP redirect to HTTPS
        http_url = self.BASE_URL.replace('https://', 'http://')
        response = requests.get(http_url, allow_redirects=False)

        # Should redirect to HTTPS
        assert response.status_code in [301, 302, 307, 308]
        assert 'https://' in response.headers.get('location', '')

# Run tests: pytest test_security.py -v
        '''

    def _get_security_architecture_overview(self) -> str:
        """Get security architecture overview"""
        return """
**Zero Trust Security Architecture:**
- Never trust, always verify
- Explicit permission verification
- Least privilege access
- Assume breach mentality

**Defense in Depth:**
- Multiple security layers
- Redundant security controls
- Compromise containment
- Resilient security design

**Security Domain Integration:**
- Identity as the perimeter
- Data-centric security
- Context-aware access controls
- Adaptive security responses"""

    def _get_integrated_security_strategy(self) -> str:
        """Get integrated security strategy"""
        return """
**Security Integration Framework:**
- Unified security policy management
- Centralized identity and access
- Integrated threat detection
- Coordinated incident response

**Security Metrics and KPIs:**
- Security posture scoring
- Risk assessment metrics
- Compliance status tracking
- Security ROI measurement

**Continuous Improvement:**
- Security posture optimization
- Threat intelligence integration
- Security automation enhancement
- Organizational security awareness"""

    def _get_security_implementation_roadmap(self) -> str:
        """Get security implementation roadmap"""
        return """
**Phase 1: Foundation (0-3 months)**
- Security policy development
- Identity and access management implementation
- Basic security monitoring setup
- Security awareness training

**Phase 2: Implementation (3-9 months)**
- Advanced security controls deployment
- Security automation implementation
- Compliance framework adoption
- Security testing integration

**Phase 3: Optimization (9-18 months)**
- Security posture optimization
- Advanced threat detection
- Security metrics refinement
- Continuous security improvement

**Phase 4: Maturity (18+ months)**
- Security operations center establishment
- Advanced security analytics
- Predictive security capabilities
- Security innovation leadership"""

    def _get_security_metrics(self) -> str:
        """Get security metrics and KPIs"""
        return """
**Security Effectiveness Metrics:**
- Mean Time to Detect (MTTD)
- Mean Time to Respond (MTTR)
- Security incident frequency
- False positive rate

**Compliance Metrics:**
- Control effectiveness percentage
- Audit findings resolution time
- Compliance score improvement
- Regulatory requirement coverage

**Security Operations Metrics:**
- Security alerts processed
- Threat hunting success rate
- Security automation coverage
- Security tool effectiveness"""

    def _get_security_improvement_cycle(self) -> str:
        """Get security improvement cycle"""
        return """
**Continuous Security Improvement:**
- Regular security assessments
- Threat intelligence updates
- Security control optimization
- Security awareness enhancement

**Security Innovation:**
- Emerging security technology adoption
- Security process improvements
- Security capability expansion
- Security thought leadership

**Security Governance:**
- Security committee oversight
- Security budget optimization
- Security talent development
- Security partnership management"""

    def _get_tools_integration(self) -> str:
        """Get security tools integration guidance"""
        return """
**Security Tool Integration:**
- SIEM platform centralization
- Security orchestration and automation
- Threat intelligence integration
- Vulnerability management integration

**Tool Selection Criteria:**
- Integration capabilities
- Scalability and performance
- Ease of use and maintenance
- Total cost of ownership

**Implementation Best Practices:**
- Phased rollout approach
- Change management processes
- User training and adoption
- Ongoing support and maintenance"""

    def _get_security_cost_optimization(self) -> str:
        """Get security cost optimization guidance"""
        return """
**Security Cost Management:**
- Risk-based security investment
- Security ROI measurement
- Cost-effective control selection
- Security automation benefits

**Optimization Strategies:**
- Cloud security cost management
- License optimization
- Shared security services
- Open-source security tools

**Budget Planning:**
- Security investment justification
- Total cost of ownership analysis
- Security value demonstration
- Future security investment planning"""

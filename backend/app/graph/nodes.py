"""
Neo4j Node Types Implementation.
Implements all 17 node types for the attack surface graph database.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from app.db.neo4j_client import Neo4jClient
import logging

logger = logging.getLogger(__name__)


class BaseNode:
    """Base class for all node types with common multi-tenancy properties."""
    
    def __init__(self, neo4j_client: Neo4jClient):
        self.client = neo4j_client
    
    def _add_tenant_info(
        self, 
        properties: Dict[str, Any], 
        user_id: Optional[str] = None, 
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add user_id and project_id for multi-tenancy."""
        if user_id:
            properties['user_id'] = user_id
        if project_id:
            properties['project_id'] = project_id
        properties['created_at'] = datetime.utcnow().isoformat()
        return properties


class DomainNode(BaseNode):
    """Domain node (root of attack surface)."""
    
    def create(
        self,
        name: str,
        whois_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a Domain node.
        
        Args:
            name: Domain name (e.g., 'example.com')
            whois_data: WHOIS information
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'name': name,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        # Add WHOIS properties
        if whois_data:
            properties.update({
                'registrar': whois_data.get('registrar'),
                'creation_date': whois_data.get('creation_date'),
                'expiration_date': whois_data.get('expiration_date'),
                'org': whois_data.get('org'),
                'country': whois_data.get('country'),
                'name_servers': whois_data.get('name_servers', []),
                'status': whois_data.get('status', []),
            })
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        return self.client.create_node('Domain', properties, merge=True)


class SubdomainNode(BaseNode):
    """Subdomain node."""
    
    def create(
        self,
        name: str,
        parent_domain: str,
        dns_records: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a Subdomain node.
        
        Args:
            name: Subdomain name (e.g., 'www.example.com')
            parent_domain: Parent domain name
            dns_records: DNS resolution information
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'name': name,
            'parent_domain': parent_domain,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        if dns_records:
            properties['dns_records'] = dns_records
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        return self.client.create_node('Subdomain', properties, merge=True)


class IPNode(BaseNode):
    """IP address node."""
    
    def create(
        self,
        address: str,
        cdn_info: Optional[Dict[str, Any]] = None,
        asn_info: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create an IP node.
        
        Args:
            address: IP address
            cdn_info: CDN detection information
            asn_info: ASN information
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'address': address,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        if cdn_info:
            properties.update({
                'is_cdn': cdn_info.get('is_cdn', False),
                'cdn_name': cdn_info.get('cdn_name'),
            })
        
        if asn_info:
            properties.update({
                'asn': asn_info.get('asn'),
                'asn_org': asn_info.get('org'),
                'asn_country': asn_info.get('country'),
            })
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        return self.client.create_node('IP', properties, merge=True)


class PortNode(BaseNode):
    """Port node."""
    
    def create(
        self,
        ip: str,
        number: int,
        protocol: str = 'tcp',
        state: str = 'open',
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a Port node.
        
        Args:
            ip: Associated IP address
            number: Port number
            protocol: Protocol (tcp/udp)
            state: Port state (open/closed/filtered)
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'ip': ip,
            'number': number,
            'protocol': protocol,
            'state': state,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        # Create unique identifier
        properties['id'] = f"{ip}:{number}/{protocol}"
        
        return self.client.create_node('Port', properties, merge=True)


class ServiceNode(BaseNode):
    """Service node."""
    
    def create(
        self,
        name: str,
        version: Optional[str] = None,
        banner: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a Service node.
        
        Args:
            name: Service name
            version: Service version
            banner: Service banner
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'name': name,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        if version:
            properties['version'] = version
        if banner:
            properties['banner'] = banner
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        # Create unique identifier
        properties['id'] = f"{name}:{version or 'unknown'}"
        
        return self.client.create_node('Service', properties, merge=True)


class BaseURLNode(BaseNode):
    """BaseURL node (HTTP endpoint)."""
    
    def create(
        self,
        url: str,
        http_metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a BaseURL node.
        
        Args:
            url: Base URL
            http_metadata: HTTP probe metadata
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'url': url,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        if http_metadata:
            properties.update({
                'status_code': http_metadata.get('status_code'),
                'content_type': http_metadata.get('content_type'),
                'content_length': http_metadata.get('content_length'),
                'server': http_metadata.get('server'),
                'title': http_metadata.get('title'),
                'response_time': http_metadata.get('response_time'),
            })
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        return self.client.create_node('BaseURL', properties, merge=True)


class EndpointNode(BaseNode):
    """Endpoint node (API/web endpoint)."""
    
    def create(
        self,
        path: str,
        method: str = 'GET',
        base_url: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create an Endpoint node.
        
        Args:
            path: Endpoint path
            method: HTTP method
            base_url: Associated base URL
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'path': path,
            'method': method,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        if base_url:
            properties['base_url'] = base_url
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        # Create unique identifier
        properties['id'] = f"{method}:{path}"
        
        return self.client.create_node('Endpoint', properties, merge=True)


class ParameterNode(BaseNode):
    """Parameter node (URL/POST parameter)."""
    
    def create(
        self,
        name: str,
        param_type: str = 'query',  # query, body, header, path
        example_value: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a Parameter node.
        
        Args:
            name: Parameter name
            param_type: Parameter type (query/body/header/path)
            example_value: Example value
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'name': name,
            'type': param_type,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        if example_value:
            properties['example_value'] = example_value
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        # Create unique identifier
        properties['id'] = f"{name}:{param_type}"
        
        return self.client.create_node('Parameter', properties, merge=True)


class TechnologyNode(BaseNode):
    """Technology node (detected technology)."""
    
    def create(
        self,
        name: str,
        version: Optional[str] = None,
        confidence: Optional[float] = None,
        categories: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a Technology node.
        
        Args:
            name: Technology name
            version: Technology version
            confidence: Detection confidence (0-100)
            categories: Technology categories
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'name': name,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        if version:
            properties['version'] = version
        if confidence is not None:
            properties['confidence'] = confidence
        if categories:
            properties['categories'] = categories
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        return self.client.create_node('Technology', properties, merge=True)


class HeaderNode(BaseNode):
    """HTTP Header node."""
    
    def create(
        self,
        name: str,
        value: str,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a Header node.
        
        Args:
            name: Header name
            value: Header value
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'name': name,
            'value': value,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        # Create unique identifier
        properties['id'] = f"{name}:{value}"
        
        return self.client.create_node('Header', properties, merge=True)


class CertificateNode(BaseNode):
    """TLS/SSL Certificate node."""
    
    def create(
        self,
        subject: str,
        issuer: Optional[str] = None,
        valid_from: Optional[str] = None,
        valid_to: Optional[str] = None,
        serial_number: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a Certificate node.
        
        Args:
            subject: Certificate subject
            issuer: Certificate issuer
            valid_from: Validity start date
            valid_to: Validity end date
            serial_number: Certificate serial number
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'subject': subject,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        if issuer:
            properties['issuer'] = issuer
        if valid_from:
            properties['valid_from'] = valid_from
        if valid_to:
            properties['valid_to'] = valid_to
        if serial_number:
            properties['serial_number'] = serial_number
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        # Create unique identifier
        properties['id'] = serial_number or f"{subject}:{issuer}"
        
        return self.client.create_node('Certificate', properties, merge=True)


class DNSRecordNode(BaseNode):
    """DNS Record node."""
    
    def create(
        self,
        record_type: str,
        value: str,
        subdomain: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a DNSRecord node.
        
        Args:
            record_type: DNS record type (A, AAAA, MX, TXT, etc.)
            value: Record value
            subdomain: Associated subdomain
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'type': record_type,
            'value': value,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        if subdomain:
            properties['subdomain'] = subdomain
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        # Create unique identifier
        properties['id'] = f"{record_type}:{value}"
        
        return self.client.create_node('DNSRecord', properties, merge=True)


class VulnerabilityNode(BaseNode):
    """Vulnerability node."""
    
    def create(
        self,
        name: str,
        severity: str,
        category: Optional[str] = None,
        source: str = 'nuclei',  # nuclei, gvm, security_check
        description: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a Vulnerability node.
        
        Args:
            name: Vulnerability name/title
            severity: Severity level (info, low, medium, high, critical)
            category: Vulnerability category
            source: Detection source
            description: Vulnerability description
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'name': name,
            'severity': severity,
            'source': source,
            'discovered_at': datetime.utcnow().isoformat(),
        }
        
        if category:
            properties['category'] = category
        if description:
            properties['description'] = description
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        # Create unique identifier
        import hashlib
        vuln_str = f"{name}:{severity}:{source}"
        properties['id'] = hashlib.md5(vuln_str.encode()).hexdigest()
        
        return self.client.create_node('Vulnerability', properties, merge=True)


class CVENode(BaseNode):
    """CVE (Common Vulnerabilities and Exposures) node."""
    
    def create(
        self,
        cve_id: str,
        cvss_score: Optional[float] = None,
        severity: Optional[str] = None,
        description: Optional[str] = None,
        published_date: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a CVE node.
        
        Args:
            cve_id: CVE identifier (e.g., 'CVE-2021-12345')
            cvss_score: CVSS score (0-10)
            severity: Severity level
            description: CVE description
            published_date: Publication date
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'id': cve_id,
            'cve_id': cve_id,
        }
        
        if cvss_score is not None:
            properties['cvss_score'] = cvss_score
        if severity:
            properties['severity'] = severity
        if description:
            properties['description'] = description
        if published_date:
            properties['published_date'] = published_date
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        return self.client.create_node('CVE', properties, merge=True)


class MitreDataNode(BaseNode):
    """MITRE CWE (Common Weakness Enumeration) node."""
    
    def create(
        self,
        cwe_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a MitreData (CWE) node.
        
        Args:
            cwe_id: CWE identifier (e.g., 'CWE-79')
            name: CWE name
            description: CWE description
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'id': cwe_id,
            'cwe_id': cwe_id,
        }
        
        if name:
            properties['name'] = name
        if description:
            properties['description'] = description
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        return self.client.create_node('MitreData', properties, merge=True)


class CapecNode(BaseNode):
    """CAPEC (Common Attack Pattern Enumeration and Classification) node."""
    
    def create(
        self,
        capec_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        likelihood: Optional[str] = None,
        severity: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a Capec node.
        
        Args:
            capec_id: CAPEC identifier (e.g., 'CAPEC-63')
            name: Attack pattern name
            description: Attack pattern description
            likelihood: Likelihood of attack
            severity: Attack severity
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'id': capec_id,
            'capec_id': capec_id,
        }
        
        if name:
            properties['name'] = name
        if description:
            properties['description'] = description
        if likelihood:
            properties['likelihood'] = likelihood
        if severity:
            properties['severity'] = severity
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        return self.client.create_node('Capec', properties, merge=True)


class ExploitNode(BaseNode):
    """Exploit node."""
    
    def create(
        self,
        exploit_id: str,
        name: str,
        exploit_type: Optional[str] = None,
        platform: Optional[str] = None,
        author: Optional[str] = None,
        published_date: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create an Exploit node.
        
        Args:
            exploit_id: Exploit identifier
            name: Exploit name
            exploit_type: Type of exploit
            platform: Target platform
            author: Exploit author
            published_date: Publication date
            user_id: User identifier for multi-tenancy
            project_id: Project identifier for multi-tenancy
            **kwargs: Additional properties
            
        Returns:
            Created node properties
        """
        properties = {
            'id': exploit_id,
            'name': name,
        }
        
        if exploit_type:
            properties['type'] = exploit_type
        if platform:
            properties['platform'] = platform
        if author:
            properties['author'] = author
        if published_date:
            properties['published_date'] = published_date
        
        properties.update(kwargs)
        properties = self._add_tenant_info(properties, user_id, project_id)
        
        return self.client.create_node('Exploit', properties, merge=True)

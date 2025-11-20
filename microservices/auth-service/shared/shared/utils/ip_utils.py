"""
Utilitaires pour la gestion des IPs et User Agents
Fichier: shared/shared/utils/ip_utils.py
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Tentative d'import de user-agents (optionnel)
try:
    from user_agents import parse
    HAS_USER_AGENTS = True
except ImportError:
    HAS_USER_AGENTS = False
    logger.warning("user-agents library not installed. Using fallback parser.")


def get_client_ip(request) -> Optional[str]:
    """
    Récupérer l'IP du client en tenant compte des proxies
    
    Args:
        request: Objet request Django
        
    Returns:
        IP du client ou None
    """
    # Vérifier X-Forwarded-For (proxy/load balancer)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Prendre la première IP de la liste
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    # Vérifier X-Real-IP (nginx)
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip.strip()
    
    # Fallback sur REMOTE_ADDR
    remote_addr = request.META.get('REMOTE_ADDR')
    return remote_addr


def get_user_agent(request) -> Optional[str]:
    """
    Récupérer le user agent de la requête
    
    Args:
        request: Objet request Django
        
    Returns:
        User agent string ou None
    """
    return request.META.get('HTTP_USER_AGENT')


def parse_user_agent(user_agent: str) -> dict:
    """
    Parser le user agent pour extraire device, browser, OS
    
    Args:
        user_agent: String user agent
        
    Returns:
        Dictionnaire avec device, browser, os
    """
    if not user_agent:
        return {
            'device': 'Unknown',
            'browser': 'Unknown',
            'os': 'Unknown'
        }
    
    # Utiliser la bibliothèque user-agents si disponible
    if HAS_USER_AGENTS:
        return _parse_with_library(user_agent)
    
    # Sinon, utiliser le parser de fallback
    return _parse_fallback(user_agent)


def _parse_with_library(user_agent: str) -> dict:
    """Parser avec la bibliothèque user-agents"""
    try:
        ua = parse(user_agent)
        
        return {
            'device': ua.device.family if ua.device.family != 'Other' else 'Desktop',
            'browser': f"{ua.browser.family} {ua.browser.version_string}".strip(),
            'os': f"{ua.os.family} {ua.os.version_string}".strip()
        }
    except Exception as e:
        logger.error(f"Error parsing user agent with library: {str(e)}")
        return _parse_fallback(user_agent)


def _parse_fallback(user_agent: str) -> dict:
    """Parser de fallback simple sans dépendance externe"""
    result = {
        'device': 'Unknown',
        'browser': 'Unknown',
        'os': 'Unknown'
    }
    
    user_agent_lower = user_agent.lower()
    
    # Detect OS
    if 'windows nt 10' in user_agent_lower:
        result['os'] = 'Windows 10'
    elif 'windows nt 6.3' in user_agent_lower:
        result['os'] = 'Windows 8.1'
    elif 'windows nt 6.2' in user_agent_lower:
        result['os'] = 'Windows 8'
    elif 'windows nt 6.1' in user_agent_lower:
        result['os'] = 'Windows 7'
    elif 'windows' in user_agent_lower:
        result['os'] = 'Windows'
    elif 'mac os x' in user_agent_lower:
        # Extraire la version si possible
        import re
        match = re.search(r'mac os x (\d+[._]\d+)', user_agent_lower)
        if match:
            version = match.group(1).replace('_', '.')
            result['os'] = f'macOS {version}'
        else:
            result['os'] = 'macOS'
    elif 'linux' in user_agent_lower and 'android' not in user_agent_lower:
        result['os'] = 'Linux'
    elif 'android' in user_agent_lower:
        # Extraire la version Android
        import re
        match = re.search(r'android (\d+\.?\d*)', user_agent_lower)
        if match:
            result['os'] = f'Android {match.group(1)}'
        else:
            result['os'] = 'Android'
    elif 'iphone' in user_agent_lower or 'ipad' in user_agent_lower:
        # Extraire la version iOS
        import re
        match = re.search(r'os (\d+[._]\d+)', user_agent_lower)
        if match:
            version = match.group(1).replace('_', '.')
            result['os'] = f'iOS {version}'
        else:
            result['os'] = 'iOS'
    
    # Detect Browser
    if 'edg/' in user_agent_lower or 'edge/' in user_agent_lower:
        import re
        match = re.search(r'edg[e]?/(\d+\.?\d*)', user_agent_lower)
        if match:
            result['browser'] = f'Edge {match.group(1)}'
        else:
            result['browser'] = 'Edge'
    elif 'chrome/' in user_agent_lower and 'edg' not in user_agent_lower:
        import re
        match = re.search(r'chrome/(\d+\.?\d*)', user_agent_lower)
        if match:
            result['browser'] = f'Chrome {match.group(1)}'
        else:
            result['browser'] = 'Chrome'
    elif 'firefox/' in user_agent_lower:
        import re
        match = re.search(r'firefox/(\d+\.?\d*)', user_agent_lower)
        if match:
            result['browser'] = f'Firefox {match.group(1)}'
        else:
            result['browser'] = 'Firefox'
    elif 'safari/' in user_agent_lower and 'chrome' not in user_agent_lower:
        import re
        match = re.search(r'version/(\d+\.?\d*)', user_agent_lower)
        if match:
            result['browser'] = f'Safari {match.group(1)}'
        else:
            result['browser'] = 'Safari'
    elif 'opera' in user_agent_lower or 'opr/' in user_agent_lower:
        result['browser'] = 'Opera'
    
    # Detect Device Type
    if 'mobile' in user_agent_lower or 'android' in user_agent_lower:
        if 'iphone' in user_agent_lower:
            result['device'] = 'iPhone'
        elif 'android' in user_agent_lower:
            result['device'] = 'Android Phone'
        else:
            result['device'] = 'Mobile'
    elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
        if 'ipad' in user_agent_lower:
            result['device'] = 'iPad'
        else:
            result['device'] = 'Tablet'
    else:
        result['device'] = 'Desktop'
    
    return result


def is_suspicious_login(
    current_ip: str,
    previous_ip: Optional[str],
    current_country: Optional[str],
    previous_country: Optional[str]
) -> bool:
    """
    Déterminer si une connexion est suspecte basée sur l'IP et la localisation
    
    Args:
        current_ip: IP actuelle
        previous_ip: IP précédente
        current_country: Pays actuel
        previous_country: Pays précédent
        
    Returns:
        True si la connexion est suspecte
    """
    # Si pas d'historique, pas suspect
    if not previous_ip or not previous_country:
        return False
    
    # Si l'IP a changé et le pays aussi, c'est suspect
    if current_ip != previous_ip and current_country != previous_country:
        return True
    
    return False


def sanitize_ip(ip: str) -> str:
    """
    Nettoyer et valider une adresse IP
    
    Args:
        ip: Adresse IP à nettoyer
        
    Returns:
        IP nettoyée ou 'unknown'
    """
    if not ip:
        return 'unknown'
    
    # Supprimer les espaces
    ip = ip.strip()
    
    # Validation basique IPv4
    parts = ip.split('.')
    if len(parts) == 4:
        try:
            if all(0 <= int(part) <= 255 for part in parts):
                return ip
        except ValueError:
            pass
    
    # Validation basique IPv6
    if ':' in ip:
        # Simple check pour IPv6
        if ip.count(':') >= 2:
            return ip
    
    return 'unknown'
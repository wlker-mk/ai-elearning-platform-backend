from typing import Optional


def get_client_ip(request) -> Optional[str]:
    """Récupérer l'IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request) -> Optional[str]:
    """Récupérer le user agent"""
    return request.META.get('HTTP_USER_AGENT')


def parse_user_agent(user_agent: str) -> dict:
    """Parser le user agent pour extraire device, browser, OS"""
    # Simplified parsing - en production, utilisez user_agents library
    result = {
        'device': 'Unknown',
        'browser': 'Unknown',
        'os': 'Unknown'
    }
    
    if not user_agent:
        return result
    
    user_agent_lower = user_agent.lower()
    
    # Detect OS
    if 'windows' in user_agent_lower:
        result['os'] = 'Windows'
    elif 'mac' in user_agent_lower or 'darwin' in user_agent_lower:
        result['os'] = 'macOS'
    elif 'linux' in user_agent_lower:
        result['os'] = 'Linux'
    elif 'android' in user_agent_lower:
        result['os'] = 'Android'
    elif 'ios' in user_agent_lower or 'iphone' in user_agent_lower:
        result['os'] = 'iOS'
    
    # Detect Browser
    if 'chrome' in user_agent_lower and 'edg' not in user_agent_lower:
        result['browser'] = 'Chrome'
    elif 'firefox' in user_agent_lower:
        result['browser'] = 'Firefox'
    elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
        result['browser'] = 'Safari'
    elif 'edg' in user_agent_lower:
        result['browser'] = 'Edge'
    
    # Detect Device
    if 'mobile' in user_agent_lower or 'android' in user_agent_lower:
        result['device'] = 'Mobile'
    elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
        result['device'] = 'Tablet'
    else:
        result['device'] = 'Desktop'
    
    return result


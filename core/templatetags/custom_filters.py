from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get dictionary item by key.
    Usage: {{ mydict|get_item:key }}
    
    Args:
        dictionary: The dictionary to access
        key: The key to lookup
        
    Returns:
        The value at dictionary[key] or None if not found
    """
    if dictionary is None:
        return None
    
    if not isinstance(dictionary, dict):
        return None
    
    return dictionary.get(key)
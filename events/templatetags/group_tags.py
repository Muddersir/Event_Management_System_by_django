from django import template

register = template.Library()

@register.filter(name="has_group")
def has_group(user, group_name):
    """
    Template filter to check if a user belongs to a group.

    Usage in templates:
      {% load group_tags %}
      {% if user|has_group:"Participant" %}
        ...
      {% endif %}
    """
    try:
        if user is None:
            return False
        return user.groups.filter(name=group_name).exists()
    except Exception:
        return False
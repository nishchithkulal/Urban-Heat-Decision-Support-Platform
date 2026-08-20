"""Current weather conditions for a location.

No database persistence yet — every request calls the upstream provider live. Adding a
cache is deferred until there is a demonstrated need (CLAUDE.md section 9); the module
boundary here is drawn so a cache can be introduced later purely inside
``service.py``/``dependencies.py`` without changing the router or the provider
interface.
"""

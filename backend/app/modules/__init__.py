"""Domain modules land here, one directory per module.

Each module owns its router, service logic, schemas, and (later) its database tables.
A module may import another module only through that module's public interface, never
its internals — this is what keeps future microservice extraction to "move the
directory" rather than "untangle the coupling" (CLAUDE.md sections 7 and 39).
"""

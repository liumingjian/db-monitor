"""Runtime inspection HTTP surface (processlist / sessions / waits / ...).

Holds ADR-0005 style `展示走采集` endpoints. Mounted at `/instances/{id}/...`
without the `/control/` prefix; write/command counterparts (e.g. kill) will
land in the same package in child #2.
"""

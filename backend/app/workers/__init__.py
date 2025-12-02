"""
Garden System Workers.

Background workers for lifecycle management, climate monitoring, and composting.

Workers:
- lifecycle_worker: Runs every 5 minutes, transitions seeds through states
- climate_worker: Runs every hour, records community health snapshots
- compost_worker: Runs daily at 3am, archives expired content and cleans up
"""

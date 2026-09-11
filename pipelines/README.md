# RocketRide pipelines

Planned pipelines:

- `zone_analysis.pipe`: receives one geographic zone plus normalized reports, uses HotData as an isolated analytical workspace, and returns structured incident updates.
- `disaster_chat.pipe`: receives user question/location plus current incident context and returns grounded navigation/safety assistance.

Do not store secrets directly in `.pipe` files. Use RocketRide/environment secret configuration.

# Crisismap back-end

## Purpose

Ideally, almost a logic-less proxying service acting in the middle of DB (supplied by **workers**) and **clients**.

If some comprehensive business logic appears, it could potentially be associated with this service.

All data gathering/parsing/transforming/storing logic should be up to corresponding **workers**.

**Client**, on the other hand, is aimed for data representation and UX/UI (map/clustering + filtering/pagination).
So the API itself acts "as a client", meaning serving JSON instead of explicit UI capabilities.

Main responsibilities:
* internally: storage accessor and data mapper
* externally: RESTful API wrapper for **clients** (e.g. `crisismap-frontend` and possible mobile natives)

## Generic scheme

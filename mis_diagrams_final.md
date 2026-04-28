# Cyber Incident Reporting & Analysis MIS
## Diagrams for Academic Project Report

**Student:** Sourish Phate | **Roll No:** 231070072 | **Branch:** Third Year C.S. | **Batch:** C

> All diagrams are generated using [Mermaid.js](https://mermaid.live).  
> Paste each code block at [mermaid.live](https://mermaid.live) to render and export as PNG/SVG.

---

## Figure 1 — System Architecture Diagram

*Interaction between users, frontend, Flask backend, and SQLite database.*

```mermaid
flowchart TD
    subgraph U["Users"]
        R[Reporter]
        AN[Analyst]
        AD[Admin]
        MG[Management]
    end

    subgraph F["Frontend (HTML + Bootstrap)"]
        UI[Web User Interface]
    end

    subgraph B["Flask Backend — app.py"]
        AU[Authentication and Session Management]
        RB[Role-Based Access Control]
        RL[Application Routes]
        IL[Incident Management Logic]
        AL[Audit Logging — log_action]
    end

    subgraph DB["SQLite Database — database.db"]
        T1[(users)]
        T2[(incidents)]
        T3[(classifications)]
        T4[(assignments)]
        T5[(investigations)]
        T6[(audit_log)]
    end

    R --> UI
    AN --> UI
    AD --> UI
    MG --> UI

    UI -- HTTP Request --> RL
    RL --> AU
    AU --> RB
    RB --> IL
    IL --> AL

    IL <--> T1
    IL <--> T2
    IL <--> T3
    IL <--> T4
    IL <--> T5
    AL --> T6

    RL -- HTTP Response --> UI
```

---

## Figure 2 — Use Case Diagram

*Capabilities of each user role in the system.*

```mermaid
flowchart LR
    Reporter([Reporter])
    Analyst([Analyst])
    Admin([Admin])
    Management([Management])

    subgraph S["Cyber Incident Reporting and Analysis MIS"]
        direction TB

        UC1(Login)
        UC2(Register)
        UC3(Submit incident)
        UC4(View own incidents)
        UC5(View and print ticket)
        UC6(View closure details)

        UC7(View assigned incidents)
        UC8(View incident details)
        UC9(Update investigation findings)
        UC10(Record actions taken)
        UC11(Add resolution details)
        UC12(Update incident status)

        UC13(View all incidents)
        UC14(Classify incident)
        UC15(Assign incident to analyst)
        UC16(Close resolved incident)
        UC17(Add new users)
        UC18(Activate or deactivate users)
        UC19(View audit log)

        UC20(View analytics dashboard)
        UC21(Filter incidents)
        UC22(View charts — type, severity, status, monthly)
        UC23(Expand full incident records)
    end

    Reporter --> UC1
    Reporter --> UC2
    Reporter --> UC3
    Reporter --> UC4
    Reporter --> UC5
    Reporter --> UC6

    Analyst --> UC1
    Analyst --> UC7
    Analyst --> UC8
    Analyst --> UC9
    Analyst --> UC10
    Analyst --> UC11
    Analyst --> UC12

    Admin --> UC1
    Admin --> UC13
    Admin --> UC14
    Admin --> UC15
    Admin --> UC16
    Admin --> UC17
    Admin --> UC18
    Admin --> UC19

    Management --> UC1
    Management --> UC20
    Management --> UC21
    Management --> UC22
    Management --> UC23
```

---

## Figure 3 — DFD Level 0 (Context Diagram)

*System boundary and external entity data flows.*

```mermaid
flowchart TD
    REP[[Reporter]]
    ANA[[Analyst]]
    ADM[[Admin]]
    MGT[[Management]]

    MIS((Cyber Incident
Reporting and Analysis
MIS))

    REP -- Incident details --> MIS
    MIS -- Ticket, status, closure details --> REP

    ADM -- Classification, assignment, user management actions --> MIS
    MIS -- All incidents, user records, audit log --> ADM

    ANA -- Findings, actions taken, status updates --> MIS
    MIS -- Assigned incidents --> ANA

    MGT -- Filter criteria --> MIS
    MIS -- Dashboards, charts, incident records --> MGT
```

---

## Figure 4 — DFD Level 1

*Internal processes and data stores.*

```mermaid
flowchart TD
    REP[[Reporter]]
    ANA[[Analyst]]
    ADM[[Admin]]
    MGT[[Management]]

    P1((1. Login
and Session))
    P2((2. Incident
Reporting))
    P3((3. Classification
and Assignment))
    P4((4. Investigation
and Closure))
    P5((5. Analytics
and Reporting))
    P6((6. User and
Audit Management))

    D1[(D1 Users)]
    D2[(D2 Incidents)]
    D3[(D3 Classifications
and Assignments)]
    D4[(D4 Investigations)]
    D5[(D5 Audit Log)]

    REP --> P1
    ANA --> P1
    ADM --> P1
    MGT --> P1
    P1 <--> D1

    REP --> P2
    P2 --> D2
    P2 -. log .-> D5
    P2 --> REP

    ADM --> P3
    P3 <--> D2
    P3 --> D3
    P3 -. log .-> D5

    ANA --> P4
    ADM --> P4
    P4 <--> D2
    P4 --> D4
    P4 -. log .-> D5

    MGT --> P5
    D2 --> P5
    D3 --> P5
    D4 --> P5
    P5 --> MGT

    ADM --> P6
    P6 <--> D1
    P6 --> D5
```

---

## Figure 5 — ER Diagram

*SQLite database schema and all foreign key relationships (verified from init_db).*

```mermaid
erDiagram
    USERS ||--o{ INCIDENTS : "reported_by"
    USERS ||--o{ CLASSIFICATIONS : "classified_by"
    USERS ||--o{ ASSIGNMENTS : "assigned_to"
    USERS ||--o{ ASSIGNMENTS : "assigned_by"
    USERS ||--o{ INVESTIGATIONS : "updated_by"
    USERS ||--o{ AUDIT_LOG : "user_id"

    INCIDENTS ||--o| CLASSIFICATIONS : "has"
    INCIDENTS ||--o| ASSIGNMENTS : "has"
    INCIDENTS ||--o| INVESTIGATIONS : "has"

    USERS {
        INTEGER id PK
        TEXT name
        TEXT email
        TEXT password
        TEXT role
        TEXT department
        TEXT phone
        INTEGER is_active
        TEXT created_at
    }

    INCIDENTS {
        INTEGER id PK
        TEXT incident_id UK
        TEXT type
        TEXT description
        TEXT severity
        TEXT affected_resources
        TEXT affected_systems
        TEXT estimated_impact
        TEXT no_of_users_affected
        TEXT location
        TEXT occurred_at
        TEXT discovered_at
        TEXT status
        INTEGER reported_by FK
        TEXT created_at
    }

    CLASSIFICATIONS {
        INTEGER id PK
        INTEGER incident_id FK
        TEXT severity_category
        TEXT impact_level
        TEXT priority
        INTEGER classified_by FK
        TEXT classified_at
    }

    ASSIGNMENTS {
        INTEGER id PK
        INTEGER incident_id FK
        INTEGER assigned_to FK
        INTEGER assigned_by FK
        TEXT assigned_at
    }

    INVESTIGATIONS {
        INTEGER id PK
        INTEGER incident_id FK
        TEXT findings
        TEXT actions_taken
        TEXT resolution_details
        INTEGER updated_by FK
        TEXT updated_at
    }

    AUDIT_LOG {
        INTEGER id PK
        INTEGER user_id FK
        TEXT user_name
        TEXT user_role
        TEXT action
        TEXT details
        TEXT timestamp
    }
```

---

## Figure 6 — Activity Diagram

*Lifecycle of an incident from submission to closure.*

```mermaid
flowchart TD
    Start([Start]) --> Login[User Login]
    Login --> Valid{Valid credentials?}
    Valid -- No --> Login
    Valid -- Yes --> Role{User Role?}

    Role -- Reporter --> Submit[Reporter submits incident form]
    Submit --> GenID[System generates incident ID
e.g. INC-001]
    GenID --> Classify[Admin classifies incident
severity, priority, impact]
    Classify --> Assign[Admin assigns analyst]

    Assign --> Investigate[Analyst investigates incident]
    Investigate --> Update[Analyst updates findings
and actions taken]
    Update --> Resolved{Status = Resolved?}

    Resolved -- No --> Investigate
    Resolved -- Yes --> MarkResolved[Analyst marks status as Resolved]
    MarkResolved --> AdminClose[Admin reviews and closes incident]

    AdminClose --> TicketView[Reporter views closure
details and prints ticket]
    AdminClose --> MgmtView[Management views
analytics dashboard]

    Role -- Analyst --> Investigate
    Role -- Admin --> Classify
    Role -- Management --> MgmtView

    TicketView --> End([End])
    MgmtView --> End
```

---

## Figure 7 — Sequence Diagram

*Main workflow from incident reporting to closure and analytics.*

```mermaid
sequenceDiagram
    actor Reporter
    participant UI as Frontend
    participant APP as Flask Backend
    participant DB as SQLite Database
    actor Admin
    actor Analyst
    actor Management

    Reporter->>UI: Fill and submit incident form
    UI->>APP: POST /reporter/submit
    APP->>APP: Validate fields and generate incident ID
    APP->>DB: INSERT into incidents
    DB-->>APP: Success
    APP-->>UI: Redirect to reporter dashboard
    UI-->>Reporter: Display new incident ticket

    Admin->>UI: Open admin dashboard
    UI->>APP: GET /admin
    APP->>DB: SELECT all incidents with joins
    DB-->>APP: Incident data
    APP-->>UI: Render admin dashboard

    Admin->>UI: Submit classification form
    UI->>APP: POST /admin/classify/inc_id
    APP->>DB: INSERT or UPDATE classifications
    DB-->>APP: Success

    Admin->>UI: Submit assignment form
    UI->>APP: POST /admin/assign/inc_id
    APP->>DB: INSERT or UPDATE assignments
    APP->>DB: UPDATE incidents status to Under Investigation
    DB-->>APP: Success

    Analyst->>UI: Open analyst dashboard
    UI->>APP: GET /analyst
    APP->>DB: SELECT assigned incidents with joins
    DB-->>APP: Data returned
    APP-->>UI: Render analyst dashboard

    Analyst->>UI: Submit investigation update
    UI->>APP: POST /analyst/update/inc_id
    APP->>DB: INSERT or UPDATE investigations
    APP->>DB: UPDATE incidents status
    DB-->>APP: Success

    Admin->>UI: Close incident
    UI->>APP: POST /admin/close/inc_id
    APP->>DB: UPDATE incidents status to Closed
    DB-->>APP: Success

    Reporter->>UI: Click view ticket
    UI->>APP: GET /reporter/ticket/INC-001
    APP->>DB: SELECT incident, reporter, investigation
    DB-->>APP: Data returned
    APP-->>UI: Return printable HTML ticket
    UI-->>Reporter: Browser opens print dialog

    Management->>UI: Open management dashboard
    UI->>APP: GET /management
    APP->>DB: Aggregate queries for charts and KPIs
    DB-->>APP: Summary data
    APP-->>UI: Render dashboard with charts
    UI-->>Management: Display analytics and incident records
```

---

## Figure 8 — Logical Class Diagram

*System entities, attributes, and route-level operations.*

```mermaid
classDiagram
    class User {
        +Integer id
        +String name
        +String email
        +String password
        +String role
        +String department
        +String phone
        +Integer is_active
        +String created_at
        +login()
        +register()
        +logout()
    }

    class Incident {
        +Integer id
        +String incident_id
        +String type
        +String description
        +String severity
        +String affected_resources
        +String affected_systems
        +String estimated_impact
        +String no_of_users_affected
        +String location
        +String occurred_at
        +String discovered_at
        +String status
        +Integer reported_by
        +submit_incident()
        +update_status()
        +generate_incident_id()
    }

    class Classification {
        +Integer id
        +Integer incident_id
        +String severity_category
        +String impact_level
        +String priority
        +Integer classified_by
        +String classified_at
        +classify_incident()
    }

    class Assignment {
        +Integer id
        +Integer incident_id
        +Integer assigned_to
        +Integer assigned_by
        +String assigned_at
        +assign_incident()
    }

    class Investigation {
        +Integer id
        +Integer incident_id
        +String findings
        +String actions_taken
        +String resolution_details
        +Integer updated_by
        +String updated_at
        +update_investigation()
    }

    class AuditLog {
        +Integer id
        +Integer user_id
        +String user_name
        +String user_role
        +String action
        +String details
        +String timestamp
        +log_action()
    }

    User "1" --> "0..*" Incident : reports
    User "1" --> "0..*" Classification : classifies
    User "1" --> "0..*" Assignment : assigns or is assigned
    User "1" --> "0..*" Investigation : updates
    User "1" --> "0..*" AuditLog : triggers

    Incident "1" --> "0..1" Classification : has
    Incident "1" --> "0..1" Assignment : has
    Incident "1" --> "0..1" Investigation : has
```

---

## Figure 9 — UI Screen Flow Diagram

*Navigation paths for each role based on session role check.*

```mermaid
flowchart TD
    Login["Login Page
[ / ]"]
    Register["Register Page
[ /register ]"]

    Login -->|New user| Register
    Register -->|Account created successfully| Login

    Login -->|role = reporter| RepDash["Reporter Dashboard
[ /reporter ]"]
    Login -->|role = analyst| AnaDash["Analyst Dashboard
[ /analyst ]"]
    Login -->|role = admin| AdmDash["Admin Dashboard
[ /admin ]"]
    Login -->|role = management| MgmtDash["Management Dashboard
[ /management ]"]

    RepDash -->|POST /reporter/submit| RepDash
    RepDash -->|GET /reporter/ticket/INC-xxx| Ticket["Ticket Print Page
[ /reporter/ticket/inc-id ]"]
    Ticket -->|window.print auto-triggers| RepDash

    AnaDash -->|POST /analyst/update/inc-id| AnaDash

    AdmDash -->|POST /admin/classify/inc-id| AdmDash
    AdmDash -->|POST /admin/assign/inc-id| AdmDash
    AdmDash -->|POST /admin/close/inc-id| AdmDash
    AdmDash -->|POST /admin/add_user| AdmDash
    AdmDash -->|POST /admin/toggle_user/user-id| AdmDash

    MgmtDash -->|GET /management with filter params| MgmtDash

    RepDash -->|GET /logout| Login
    AnaDash -->|GET /logout| Login
    AdmDash -->|GET /logout| Login
    MgmtDash -->|GET /logout| Login
```

---

*Generated for MIS Project — Cyber Incident Reporting & Analysis System*  
*Sourish Phate | Roll No: 231070072 | Third Year C.S. | Batch C*

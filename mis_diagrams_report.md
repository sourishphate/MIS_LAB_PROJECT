# Cyber Incident Reporting & Analysis Management Information System
## Academic Project Report Diagrams

This document contains the diagrams reverse-engineered from the Flask `app.py` codebase for the **Cyber Incident Reporting & Analysis Management Information System**.

All diagrams are generated using [Mermaid.js](https://mermaid-js.github.io/), which renders natively in standard Markdown viewers (like GitHub, GitLab, and most modern Markdown editors). You can right-click the rendered SVG graphs to save or export them as images (PNG/SVG) for your report.

---

### 1. System Architecture Diagram
**Figure 1:** *System Architecture showing interaction between Users, Frontend, Backend, and Database.*

```mermaid
flowchart TD
    subgraph Users
        R[Reporter]
        An[Analyst]
        Ad[Admin]
        M[Management]
    end

    subgraph Frontend["Frontend (HTML, Bootstrap, Chart.js)"]
        UI[Web User Interface]
    end

    subgraph Backend["Flask Backend (app.py)"]
        Auth[Authentication & Sessions]
        RBAC[Role-Based Access Control]
        Routes[Application Routes]
        IL[Incident Logic]
        AL[Audit Logging]
    end

    subgraph Database["SQLite Database (database.db)"]
        DB_Users[(users)]
        DB_Inc[(incidents)]
        DB_Class[(classifications)]
        DB_Assign[(assignments)]
        DB_Inv[(investigations)]
        DB_Audit[(audit_log)]
    end

    R --> UI
    An --> UI
    Ad --> UI
    M --> UI

    UI -- HTTP Requests --> Routes
    Routes --> Auth
    Auth --> RBAC
    RBAC --> IL
    IL --> AL

    IL <--> DB_Users
    IL <--> DB_Inc
    IL <--> DB_Class
    IL <--> DB_Assign
    IL <--> DB_Inv
    AL --> DB_Audit

    Routes -- HTTP Response (Dashboards/Tickets) --> UI
```

---

### 2. Use Case Diagram
**Figure 2:** *Use Case Diagram outlining the capabilities of each user role.*

```mermaid
flowchart LR
    %% Actors
    Reporter([Reporter])
    Analyst([Analyst])
    Admin([Admin])
    Management([Management])

    %% Use Cases
    subgraph System ["Cyber Incident Reporting & Analysis MIS"]
        direction TB
        %% Reporter UCs
        UC_Login(Login)
        UC_Reg(Register)
        UC_SubInc(Submit incident)
        UC_ViewOwn(View own incidents)
        UC_Print(Print/download ticket)
        UC_ViewClosure(View closure details)

        %% Analyst UCs
        UC_ViewAssigned(View assigned incidents)
        UC_ViewIncDet(View incident details)
        UC_AddFind(Add investigation findings)
        UC_RecAct(Record actions taken)
        UC_AddRes(Add resolution details)
        UC_UpdStat(Update status)

        %% Admin UCs
        UC_ViewAll(View all incidents)
        UC_Classify(Classify incident)
        UC_Assign(Assign incident to analyst)
        UC_Close(Close resolved incident)
        UC_AddUser(Add users)
        UC_TogUser(Activate/deactivate users)
        UC_ViewAud(View audit log)

        %% Mgmt UCs
        UC_ViewDash(View analytics dashboard)
        UC_Filter(Filter incidents)
        UC_ViewCharts(View charts)
        UC_ExpRep(Expand incident records)
    end

    Reporter --> UC_Login
    Reporter --> UC_Reg
    Reporter --> UC_SubInc
    Reporter --> UC_ViewOwn
    Reporter --> UC_Print
    Reporter --> UC_ViewClosure

    Analyst --> UC_Login
    Analyst --> UC_ViewAssigned
    Analyst --> UC_ViewIncDet
    Analyst --> UC_AddFind
    Analyst --> UC_RecAct
    Analyst --> UC_AddRes
    Analyst --> UC_UpdStat

    Admin --> UC_Login
    Admin --> UC_ViewAll
    Admin --> UC_Classify
    Admin --> UC_Assign
    Admin --> UC_Close
    Admin --> UC_AddUser
    Admin --> UC_TogUser
    Admin --> UC_ViewAud

    Management --> UC_Login
    Management --> UC_ViewDash
    Management --> UC_Filter
    Management --> UC_ViewCharts
    Management --> UC_ExpRep
```

---

### 3. DFD Level 0 / Context Diagram
**Figure 3:** *Context Diagram (DFD Level 0) illustrating the system boundary and external entities.*

```mermaid
flowchart TD
    %% External Entities
    Reporter[[Reporter]]
    Analyst[[Analyst]]
    Admin[[Admin]]
    Management[[Management]]

    %% Central Process
    MIS((Cyber Incident\nReporting & Analysis\nMIS))

    %% Data flows
    Reporter -- Incident details --> MIS
    MIS -- Ticket / Status / Closure details --> Reporter

    Admin -- Classification & Assignment data --> MIS
    Admin -- User Management & Activation --> MIS
    MIS -- All Incidents & Audit Logs --> Admin

    MIS -- Assigned Incidents --> Analyst
    Analyst -- Investigation findings & Status updates --> MIS

    MIS -- Reports, Dashboards & Analytics --> Management
    Management -- Filters --> MIS
```

---

### 4. DFD Level 1
**Figure 4:** *DFD Level 1 displaying internal processes and data stores.*

```mermaid
flowchart TD
    %% Processes
    P1((1. User Auth\n& Session Mgmt))
    P2((2. Incident\nReporting))
    P3((3. Classification\n& Assignment))
    P4((4. Investigation\n& Resolution))
    P5((5. User\nManagement))
    P6((6. Analytics\n& Reporting))
    P7((7. Audit\nLogging))

    %% Data Stores
    D1[(D1 Users)]
    D2[(D2 Incidents)]
    D3[(D3 Classifications)]
    D4[(D4 Assignments)]
    D5[(D5 Investigations)]
    D6[(D6 Audit Log)]

    %% External Entities
    Reporter[[Reporter]]
    Analyst[[Analyst]]
    Admin[[Admin]]
    Management[[Management]]

    %% Flows
    Reporter -- Login/Register --> P1
    P1 <--> D1
    P1 -- Session info --> Reporter

    Reporter -- Incident details --> P2
    P2 --> D2
    D2 -- Incident info --> P2
    P2 -- Ticket/Status --> Reporter

    Admin -- Classify/Assign --> P3
    P3 --> D3
    P3 --> D4
    P3 -- Update status --> D2

    Analyst -- Assigned to --> P4
    D4 -- Read assignment --> P4
    D2 -- Read incident --> P4
    P4 -- Update findings/actions --> D5
    P4 -- Update status --> D2

    Admin -- Close incident --> P4

    Admin -- Add/Toggle Users --> P5
    P5 --> D1

    Management -- Filter criteria --> P6
    D2 --> P6
    D3 --> P6
    D4 --> P6
    D5 --> P6
    P6 -- Dashboard/Charts --> Management

    %% Audit
    P1 -. Log action .-> P7
    P2 -. Log action .-> P7
    P3 -. Log action .-> P7
    P4 -. Log action .-> P7
    P5 -. Log action .-> P7
    P7 --> D6
    Admin -- View logs --> P7
```

---

### 5. ER Diagram
**Figure 5:** *Entity-Relationship Diagram depicting the SQLite database schema and foreign key relationships.*

```mermaid
erDiagram
    USERS ||--o{ INCIDENTS : "reported_by"
    USERS ||--o{ ASSIGNMENTS : "assigned_to"
    USERS ||--o{ ASSIGNMENTS : "assigned_by"
    USERS ||--o{ CLASSIFICATIONS : "classified_by"
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

### 6. Activity Diagram
**Figure 6:** *Activity Diagram showing the lifecycle of an incident and system decision points.*

```mermaid
flowchart TD
    Start([Start]) --> Login(User Login)
    Login --> ValidLogin{Valid Login?}
    ValidLogin -- No --> Login
    ValidLogin -- Yes --> RoleCheck{Role?}

    RoleCheck -- Reporter --> SubmitInc(Reporter submits incident)
    SubmitInc --> GenID(System generates incident ID)
    GenID --> Classify(Admin classifies incident)
    Classify --> Assign(Admin assigns Analyst)

    Assign --> Investigate(Analyst investigates)
    Investigate --> RecFindings(Analyst records findings/actions)

    RecFindings --> ResolveCheck{Status Resolved?}
    ResolveCheck -- No --> Investigate
    ResolveCheck -- Yes --> MarkResolved(Analyst marks Resolved)

    MarkResolved --> CloseCheck{Admin Validation}
    CloseCheck -- Admin closes --> CloseInc(Admin closes incident)

    CloseInc --> RepView(Reporter views closure details/ticket)
    CloseInc --> MgmtView(Management views analytics)

    RepView --> End([End])
    MgmtView --> End
```

---

### 7. Sequence Diagram
**Figure 7:** *Sequence Diagram for the main workflow from reporting to closure and analytics.*

```mermaid
sequenceDiagram
    actor Reporter
    participant Frontend
    participant Flask Backend
    participant SQLite Database
    actor Admin
    actor Analyst
    actor Management

    Reporter->>Frontend: Submit Incident Form
    Frontend->>Flask Backend: POST /reporter/submit
    Flask Backend->>Flask Backend: Validate data & Generate ID
    Flask Backend->>SQLite Database: INSERT INTO incidents
    SQLite Database-->>Flask Backend: Success
    Flask Backend-->>Frontend: Redirect to Reporter Dashboard
    Frontend-->>Reporter: Display new incident ticket

    Admin->>Frontend: View all incidents
    Frontend->>Flask Backend: GET /admin
    Flask Backend->>SQLite Database: SELECT * FROM incidents
    SQLite Database-->>Flask Backend: Data
    Flask Backend-->>Frontend: Admin Dashboard UI
    Admin->>Frontend: Submit Classification & Assignment
    Frontend->>Flask Backend: POST /admin/classify & /admin/assign
    Flask Backend->>SQLite Database: INSERT/UPDATE classifications & assignments
    Flask Backend->>SQLite Database: UPDATE incidents SET status='Under Investigation'

    Analyst->>Frontend: View assigned incidents
    Frontend->>Flask Backend: GET /analyst
    Flask Backend->>SQLite Database: SELECT assigned incidents
    SQLite Database-->>Flask Backend: Data
    Flask Backend-->>Frontend: Analyst Dashboard UI
    Analyst->>Frontend: Update status & findings
    Frontend->>Flask Backend: POST /analyst/update
    Flask Backend->>SQLite Database: INSERT/UPDATE investigations
    Flask Backend->>SQLite Database: UPDATE incidents SET status='Resolved'

    Admin->>Frontend: Close incident
    Frontend->>Flask Backend: POST /admin/close
    Flask Backend->>SQLite Database: UPDATE incidents SET status='Closed'

    Reporter->>Frontend: Download closed ticket
    Frontend->>Flask Backend: GET /reporter/ticket
    Flask Backend->>SQLite Database: SELECT incident & investigation details
    SQLite Database-->>Flask Backend: Data
    Flask Backend-->>Frontend: Generate Ticket HTML with Closure Details
    Frontend-->>Reporter: Print/Download PDF

    Management->>Frontend: View Analytics
    Frontend->>Flask Backend: GET /management
    Flask Backend->>SQLite Database: Execute analytical queries
    SQLite Database-->>Flask Backend: Aggregate Data
    Flask Backend-->>Frontend: Render Dashboard & Charts
    Frontend-->>Management: Display Analytics Dashboard
```

---

### 8. Logical Class Diagram
**Figure 8:** *Logical Class Diagram representing the system entities, attributes, and route operations.*

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
        +String status
        +String occurred_at
        +Integer reported_by
        +submit_incident()
        +update_status()
        +close_incident()
        +generate_ticket()
    }

    class Classification {
        +Integer id
        +Integer incident_id
        +String severity_category
        +String impact_level
        +String priority
        +Integer classified_by
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
        +update_investigation()
    }

    class AuditLog {
        +Integer id
        +Integer user_id
        +String user_role
        +String action
        +String details
        +String timestamp
        +log_action()
    }

    User "1" -- "0..*" Incident : reports
    User "1" -- "0..*" Classification : classifies
    User "1" -- "0..*" Assignment : assigns/assigned_to
    User "1" -- "0..*" Investigation : updates
    User "1" -- "0..*" AuditLog : triggers

    Incident "1" -- "0..1" Classification : has
    Incident "1" -- "0..1" Assignment : has
    Incident "1" -- "0..1" Investigation : has
```

---

### 9. UI Navigation / Screen Flow Diagram
**Figure 9:** *Screen Flow Diagram showing navigation paths based on user roles.*

```mermaid
flowchart TD
    Login[Login Page /]
    Register[Register Page /register]

    Login -- Unauthenticated --> Register
    Register -- Success --> Login

    Login -- Role == Reporter --> RepDash[Reporter Dashboard /reporter]
    Login -- Role == Analyst --> AnaDash[Analyst Dashboard /analyst]
    Login -- Role == Admin --> AdmDash[Admin Dashboard /admin]
    Login -- Role == Management --> MgmtDash[Management Dashboard /management]

    %% Reporter Flow
    RepDash -- Submit Form --> RepDash
    RepDash -- Click Ticket --> Ticket[Ticket Print Page /reporter/ticket]
    Ticket -- Close/Print --> RepDash

    %% Analyst Flow
    AnaDash -- Submit Update Form --> AnaDash

    %% Admin Flow
    AdmDash -- Submit Classify Form --> AdmDash
    AdmDash -- Submit Assign Form --> AdmDash
    AdmDash -- Submit Close Form --> AdmDash
    AdmDash -- Submit Add User --> AdmDash
    AdmDash -- Submit Toggle User --> AdmDash

    %% Management Flow
    MgmtDash -- Apply Filters --> MgmtDash

    %% Logout
    RepDash -- Logout --> Login
    AnaDash -- Logout --> Login
    AdmDash -- Logout --> Login
    MgmtDash -- Logout --> Login
```

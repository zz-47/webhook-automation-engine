# Dark Kitchen Automation Engine

A repository dedicated to tracking the architecture of a real-time conversational ordering system, headless task routers, and server-to-server webhook integration. This workspace serves as a technical R&D showcase for exploring asynchronous data routing, state-machine conversational logic, and real-time backend notifications.

---

### ⚡ Featured R&D Case Study: Conversational Ordering Pipeline

This infrastructure was engineered as a centralized system designed to interface with external mobile messaging platform components. While public-facing production deployments were paused due to platform-side business verification constraints, the sandbox architecture successfully validates full stack, server-to-server transaction loops.

#### Core Technical Milestones Validated:
* **Asynchronous Webhook Ingestion:** Engineered custom Flask endpoints to catch, sanitize, and validate incoming HTTP POST payloads from external application endpoints.
* **Stateful Conversational Trees:** Implemented an independent Natural Language Understanding (`nlu`) module to handle dynamic intent recognition and route customer inquiries down deterministic transaction paths without state drift.
* **Real-Time Data Distribution:** Architected a multi-role notification pipeline enabling background order logs to instantly update a merchant dashboard view via event-driven handlers.

---

### 📊 System Architecture & Data Flow

```text
+----------------------------------------------------------+
|                        EXTERNAL CLIENT                   |
|  +----------------+   +----------------+                 |
|  | Customer Mini  |   | Merchant Mini  |                 |
|  |   or Chatbot   |   | (Admin Access) |                 |
|  +----------------+   +----------------+                 |
|           |                      |                       |
+-----------+----------------------+-----------------------+
            |                      |
            +----------+-----------+
                       |
               HTTPS / WebSockets
                       |
          +---------------------------------+
          |        Flask Backend API        |
          |---------------------------------|
          | State Engine / Intent Parsing   |
          | Orders CRUD / Webhook Event API |
          | Real-Time System Updates        |
          | Local Storage / DB Handlers     |
          +---------------------------------+

### 🗂️ Architectural File Structure
The project layout scales from an agile local file matrix up to a modular, production-ready backend framework:

Plaintext
dark_kitchen_chatbot/
├── app/
│   ├── __init__.py
│   ├── app.py             # Flask core engine with webhook endpoints
│   ├── config.py          # Environment & secret configuration
│   ├── nlu_module.py      # Core intent parsing & NLP processing layer
│   ├── models.py          # Order and Menu object definitions
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── menu.py        # Menu lookup & catalog extraction
│   │   ├── orders.py      # Transaction CRUD processing
│   │   └── webhooks.py    # Asynchronous external client ingestion
│   └── utils/
│       ├── db.py          # Operational storage initialization
│       └── validation.py  # Input sanitization and schema checking
├── requirements.txt       # Engine software dependencies
└── README.md              # Architectural documentation

# 🛡️ FraudTrix: Real-Time Fraud Analytics Suite (v2.0)

FraudTrix is an industrial-grade, real-time fraud detection pipeline designed to process high-velocity financial transactions. It utilizes a microservices architecture to ingest streaming data, calculate multi-factor risk scores, and visualize insights on a geospatial dashboard.



## 🏗️ System Architecture
The project follows a decoupled, event-driven architecture:

* **Ingestion Layer**: A Python-based **Producer** simulating global transaction traffic (amount, type, location, and device metadata).
* **Streaming Layer**: **Apache Kafka (KRaft mode)** acts as the high-throughput message broker, ensuring sub-second latency and fault tolerance.
* **Processing Layer**: A **Risk Engine** that consumes Kafka events, applies a multi-factor scoring algorithm, and flags high-risk transactions.
* **Storage Layer**: **MongoDB** serves as the document store for persistent audit logs and historical analysis.
* **Visualization Layer**: A professional **Streamlit** dashboard featuring geospatial mapping, device vulnerability charts, and live risk metrics.

## 🚀 Key Features
* **Real-Time Processing**: End-to-end data flow from transaction generation to UI update in under 2 seconds.
* **Geospatial Intelligence**: Visualizes transaction origins using live Mapbox integration.
* **Advanced Risk Scoring**: Moves beyond simple rules to a weighted scoring system (Amount + Type + Device context).
* **Behavioral Insights**: Sunburst and Scatter analytics to identify which devices or transaction types are most targeted.
* **Interactive Controls**: Sidebar filters for real-time data drilling and threshold management.



## 🛠️ Tech Stack
| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.9+ |
| **Message Broker** | Apache Kafka |
| **NoSQL Database** | MongoDB |
| **UI/Frontend** | Streamlit |
| **Visualization** | Plotly, Matplotlib |
| **Containerization** | Docker & Docker Compose |

## 📦 Installation & Setup

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
* Allocated RAM: Minimum 4GB (Recommended in Docker settings).

### Execution
1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/siddhigangan/fraud-detection-system.git](https://github.com/siddhigangan/fraud-detection-system.git)
    cd fraud-detection-system
    ```

2.  **Launch the Suite**:
    ```bash
    docker-compose up -d --build
    ```

3.  **Access the Dashboard**:
    Open your browser and go to `http://localhost:8501`.

## 📜 Project Structure
```text
fraud-detection-system/
├── producer/    # Generates live mock transactions
├── processor/   # Logic for risk scoring and database writes
├── dashboard/   # Streamlit UI and visual analytics
└── docker-compose.yml
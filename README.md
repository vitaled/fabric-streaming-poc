# Contoso Real-Time Analytics Platform

A proof-of-concept demonstrating **multiple approaches** for real-time log analytics using **Microsoft Fabric**, **Azure Event Hub**, and **Kusto (KQL)**. This repository showcases different ingestion patterns to help you choose the best fit for your use case.

## 🎯 Approaches Demonstrated

This repository implements **three different real-time ingestion patterns**:

| Approach | Source | Processing | Destination | Use Case |
|----------|--------|------------|-------------|----------|
| **1. Spark Notebook** | Azure Event Hub | Spark Structured Streaming | Kusto | Complex transformations, custom logic |
| **2. Eventstream (Processed)** | Custom Endpoint | Fabric Eventstream | Kusto | Low-code, built-in processing |
| **3. Eventstream (Direct)** | Custom Endpoint | None (passthrough) | Kusto | Lowest latency, raw ingestion |

## 🏗️ Architecture Overview

### Approach 1: Spark Structured Streaming
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Log Sources   │────▶│  Azure Event    │────▶│ Spark Structured│────▶│ Kusto/Eventhouse│
│ (Python Script) │     │      Hub        │     │    Streaming    │     │   (KQL DB)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```
- Full control over transformations
- Schema validation and parsing in PySpark
- Checkpointing in Lakehouse

### Approach 2: Eventstream with Processed Ingestion
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Log Sources   │────▶│   Eventstream   │────▶│   Eventstream   │────▶│ Kusto/Eventhouse│
│  (HTTP POST)    │     │ Custom Endpoint │     │   Processing    │     │   (KQL DB)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```
- Low-code/no-code setup
- Built-in transformations (filter, aggregate, etc.)
- Managed by Fabric

### Approach 3: Eventstream with Direct Ingestion
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Log Sources   │────▶│   Eventstream   │────▶│ Kusto/Eventhouse│
│  (HTTP POST)    │     │ Custom Endpoint │     │   (KQL DB)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```
- Lowest latency
- Raw data passthrough
- Best for high-volume scenarios

## 📁 Repository Structure

```
├── terraform/              # Infrastructure as Code (Terraform)
│   ├── main.tf            # Main resource definitions
│   ├── variables.tf       # Variable declarations
│   ├── terraform.tfvars   # Variable values (gitignored)
│   ├── outputs.tf         # Output values
│   ├── eventstream.json.tmpl        # Eventstream template (processed)
│   └── eventstream-direct.json.tmpl # Eventstream template (direct)
│
├── notebooks/              # Microsoft Fabric Notebooks
│   └── eventhub_to_kusto_streaming.py  # Spark streaming notebook
│
├── scripts/                # Utility scripts
│   ├── send_logs_to_eventhub.py       # Send test events to Event Hub
│   ├── generate_partitioned_logs.py   # Generate partitioned log files
│   └── requirements.txt               # Python dependencies
│
└── README.md              # This file
```

## 🚀 Getting Started

### Prerequisites

- **Azure Subscription** with permissions to create resources
- **Microsoft Fabric** capacity (F2 or higher recommended)
- **Terraform** >= 1.5.0
- **Python** >= 3.9
- **Azure CLI** (logged in: `az login`)

### 1. Deploy Infrastructure

```bash
cd terraform

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Deploy
terraform init
terraform plan
terraform apply
```

This creates:
- Azure Resource Group
- Microsoft Fabric Capacity
- Fabric Workspace with Lakehouse and Eventhouse
- Azure Event Hub Namespace and Hub
- **Two Eventstreams** (processed and direct ingestion)
- Spark Notebook for streaming

### 2. Choose Your Ingestion Approach

#### Option A: Spark Notebook (Event Hub → Kusto)
```bash
# Send test data to Event Hub
cd scripts
python send_logs_to_eventhub.py --config eventhub_config.yaml

# Then run the notebook in Fabric portal
```

#### Option B: Eventstream with Custom Endpoint
1. Open Microsoft Fabric portal
2. Navigate to the deployed workspace
3. Open the Eventstream (`contoso_eventstream` or `contoso_eventstream_direct`)
4. Copy the Custom Endpoint URL from the source
5. POST JSON data directly to the endpoint:
```bash
curl -X POST "<custom-endpoint-url>" \
  -H "Content-Type: application/json" \
  -d '{"timestamp":"2026-01-23T10:00:00Z","severity":"info",...}'
```

### 3. Verify Data in Kusto

```kql
// In KQL Database
logs
| take 10

// Or for eventstream tables
logs_processed
| take 10
```

## 📊 Comparison of Approaches

| Feature | Spark Notebook | Eventstream (Processed) | Eventstream (Direct) |
|---------|---------------|------------------------|---------------------|
| **Latency** | Medium (micro-batch) | Low | Lowest |
| **Complexity** | High (code required) | Low (visual designer) | Lowest |
| **Transformations** | Full PySpark | Built-in operators | None |
| **Schema Control** | Full control | JSON mapping | Auto-infer |
| **Checkpointing** | Lakehouse | Managed | N/A |
| **Cost** | Spark compute | Eventstream CU | Eventstream CU |
| **Best For** | Complex ETL | Light processing | Raw ingestion |

## 📊 Log Schema

The system processes docCreator application logs with the following structure:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 timestamp |
| `severity` | string | Log level (info, warning, error, debug) |
| `namespace` | string | Kubernetes namespace |
| `pod` | string | Pod name |
| `host` | string | Host identifier |
| `container` | string | Container name |
| `source` | string | Log source (e.g., kubernetes) |
| `data` | object (JSON string) | Document generation details |

The `data` field contains document processing metrics like `timeTotal`, `templateName`, `logType`, etc.

## 🔐 Authentication

| Component | Auth Method |
|-----------|-------------|
| Event Hub (Send) | Azure Entra ID (DefaultAzureCredential) |
| Event Hub (Read) | SAS Token (Connection String) |
| Kusto/Eventhouse | Fabric Managed Identity |
| Terraform | Azure CLI |

## 📚 Documentation

- [Terraform README](terraform/README.md) - Infrastructure details
- [Scripts README](scripts/README.md) - Utility scripts guide
- [Notebooks README](notebooks/README.md) - Notebook documentation

## 🛠️ Development

### Local Testing

```bash
# Generate sample log files locally
cd scripts
python generate_partitioned_logs.py
# Output: scripts/output/year=2026/month=01/...
```

### Streaming Modes

The `send_logs_to_eventhub.py` script supports:
- **Batch mode**: Send all events at once
- **Streaming mode**: Send events at a specified rate (events/second)

## 📝 License

This project is for demonstration purposes.

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test with `terraform plan`
4. Submit a pull request

# Utility Scripts

This folder contains Python scripts for generating and sending test log data to Azure Event Hub.

## 📁 Files

| File | Description |
|------|-------------|
| `send_logs_to_eventhub.py` | Send generated log events to Azure Event Hub |
| `generate_partitioned_logs.py` | Generate partitioned log files locally |
| `fake-data-generator.py` | Basic log data generator |
| `requirements.txt` | Python dependencies |
| `eventhub_config.example.yaml` | Example configuration for Event Hub |
| `config.example.yaml` | Example configuration for local generation |

## 🚀 Quick Start

### Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

### Send Events to Event Hub

```bash
# Copy and edit the config file
cp eventhub_config.example.yaml eventhub_config.yaml
# Edit eventhub_config.yaml with your Event Hub details

# Send events in batch mode
python send_logs_to_eventhub.py --config eventhub_config.yaml

# Send events in streaming mode (real-time)
python send_logs_to_eventhub.py --config eventhub_config.yaml --mode streaming
```

### Generate Local Files

```bash
# Generate partitioned log files
python generate_partitioned_logs.py

# Output: output/year=2026/month=01/day=XX/hour=XX/minute=XX/
```

## ⚙️ Configuration

### eventhub_config.yaml

```yaml
# Authentication (choose one method)
auth_method: cli                # Options: cli, default, managed_identity, client_secret

# Event Hub Connection
namespace: ehns-contoso         # Event Hub namespace name
eventhub_name: contoso-logs     # Event Hub name

# Or use connection string directly
# connection_string: "Endpoint=sb://..."

# Event Generation
mode: batch                     # batch or streaming
total_events: 1000              # For batch mode
events_per_second: 10           # For streaming mode
duration_seconds: 60            # For streaming mode
```

### Authentication Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| `cli` | Azure CLI credentials | Local development |
| `default` | DefaultAzureCredential chain | Flexible (tries multiple methods) |
| `managed_identity` | Azure Managed Identity | Azure VMs, App Service |
| `client_secret` | Service Principal | CI/CD pipelines |
| Connection String | SAS Token | Quick testing |

## 📊 Generated Log Schema

The scripts generate logs matching the docCreator application format:

```json
{
  "timestamp": "2026-01-23T10:30:00.000Z",
  "severity": "info",
  "namespace": "prd-doccreator",
  "pod": "doccreator-backend-...",
  "host": "aks-applications-...",
  "container": "doccreator-backend",
  "source": "kubernetes",
  "data": {
    "logType": "DocGeneration",
    "templateName": "Bond Certificate",
    "timeTotal": 1234,
    "client": "Contoso Standard PIB",
    ...
  }
}
```

## 🔧 Script Options

### send_logs_to_eventhub.py

```bash
python send_logs_to_eventhub.py [OPTIONS]

Options:
  --config FILE           Path to YAML config file
  --mode MODE             batch or streaming (default: batch)
  --total-events N        Number of events for batch mode
  --events-per-second N   Rate for streaming mode
  --duration-seconds N    Duration for streaming mode
  --dry-run               Generate events without sending
```

### generate_partitioned_logs.py

```bash
python generate_partitioned_logs.py [OPTIONS]

Options:
  --start DATETIME        Start time for log generation
  --end DATETIME          End time for log generation
  --output-dir PATH       Output directory (default: output/)
```

## 📝 Output

### Batch Mode
```
Sending 1000 events to Event Hub...
Batch 1/10: Sent 100 events
Batch 2/10: Sent 100 events
...
Complete! Sent 1000 events in 5.2 seconds
```

### Streaming Mode
```
Streaming events at 10/second for 60 seconds...
[00:10] Sent 100 events (10.0 events/sec)
[00:20] Sent 200 events (10.0 events/sec)
...
Complete! Sent 600 events
```

## ⚠️ Notes

- The `eventhub_config.yaml` file may contain sensitive connection strings - it's gitignored
- For production, use Managed Identity or DefaultAzureCredential
- Event Hub has retention limits (default 1 day) - old events are automatically deleted
- Use `--dry-run` to test event generation without sending to Event Hub

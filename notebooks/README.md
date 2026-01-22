# Microsoft Fabric Notebooks

This folder contains PySpark notebooks designed to run in Microsoft Fabric.

## 📁 Notebooks

### eventhub_to_kusto_streaming.py

A Spark Structured Streaming notebook that:
1. **Reads** real-time events from Azure Event Hub
2. **Parses** JSON log messages
3. **Writes** to Kusto/Eventhouse for analytics

## 🏗️ Architecture

```
Azure Event Hub  ──▶  Spark Streaming  ──▶  Kusto/Eventhouse
                            │
                            ▼
                      Lakehouse
                    (Checkpoints)
```

## 🔧 Configuration

The notebook uses **Terraform token substitution**. Before deployment, tokens like `{{ .EventHubNamespace }}` are replaced with actual values:

| Token | Description |
|-------|-------------|
| `{{ .EventHubNamespace }}` | Event Hub namespace FQDN |
| `{{ .EventHubName }}` | Event Hub name |
| `{{ .EventHubConnectionString }}` | SAS connection string for reading |
| `{{ .KustoClusterUri }}` | Kusto query service URI |
| `{{ .KustoDatabaseName }}` | Target KQL database |
| `{{ .KustoTableName }}` | Target table name |

## 🔐 Authentication

| Connection | Method |
|------------|--------|
| Event Hub | SAS Token (via connection string) |
| Kusto | Fabric Managed Identity (`mssparkutils.credentials.getToken()`) |

## 📊 Schema

The notebook parses logs into a flattened schema:

**Extracted Fields:**
- `enqueued_time` - When Event Hub received the message
- `sequence_number` - Event Hub sequence number
- `container`, `host`, `namespace`, `pod` - Kubernetes metadata
- `severity`, `source`, `type` - Log classification
- `log_timestamp` - Original timestamp from the log
- `data` - Nested JSON as string (document generation details)
- `ingestion_time` - When Spark processed the message

## 🚀 Running the Notebook

### Prerequisites
1. Notebook deployed to Fabric workspace (via Terraform)
2. Lakehouse attached for checkpointing
3. Events in Event Hub

### Steps
1. Open the notebook in Microsoft Fabric portal
2. Attach to a Lakehouse (for checkpoint storage)
3. Run cells sequentially:
   - **Cell 1**: Configuration and checkpoint setup
   - **Cell 2**: Event Hub connection setup
   - **Cell 3**: Test batch read (verify connectivity)
   - **Cell 4**: Define JSON schema
   - **Cell 5**: Create streaming DataFrame
   - **Cell 6**: Configure Kusto sink
   - **Cell 7**: Start streaming query
   - **Cell 8**: Monitor query status

### Stopping the Stream
```python
# In a new cell
query.stop()
```

## 🔄 Checkpoint Management

Checkpoints are stored in the Lakehouse at:
```
Files/checkpoints/eventhub_to_kusto/<table_name>/
```

To restart from the beginning:
```python
CLEAR_CHECKPOINT = True  # In configuration cell
```

## ⚠️ Notes

- The notebook uses `azure-eventhubs-spark` connector (bundled in Fabric)
- Kusto Spark connector writes in micro-batches (default: 30 seconds)
- The `tableCreateOptions: CreateIfNotExist` auto-creates the Kusto table
- For schema changes, clear the checkpoint and drop/recreate the Kusto table

## 🔧 Troubleshooting

### "No events found in Event Hub"
- Check Event Hub retention period (events may have expired)
- Run `send_logs_to_eventhub.py` to send test data
- Verify connection string has `listen` permission

### Authentication errors
- Ensure Fabric workspace identity has Event Hub Data Receiver role
- Verify SAS token hasn't expired

### Streaming query fails
- Check checkpoint path is accessible
- Verify Lakehouse is attached
- Review Spark UI for detailed errors

## 📝 Format

This file uses Fabric's `.py` notebook format with special markers:
- `# METADATA ********************` - Notebook metadata (JSON)
- `# MARKDOWN ********************` - Markdown cells
- `# CELL ********************` - Code cells

The file is deployed and rendered as a notebook in Fabric portal.

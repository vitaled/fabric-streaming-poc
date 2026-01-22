# Terraform Infrastructure

This folder contains Terraform configurations for deploying the complete real-time analytics infrastructure on Azure and Microsoft Fabric.

## 🏗️ Resources Created

### Azure Resources
| Resource | Description |
|----------|-------------|
| **Resource Group** | Container for all Azure resources |
| **Event Hub Namespace** | Messaging namespace for event streaming |
| **Event Hub** | The actual event hub for log ingestion |
| **Authorization Rules** | `send-rule` (send only) and `listen-rule` (listen only) |
| **Storage Account** | Data Lake Storage Gen2 for Fabric integration |

### Microsoft Fabric Resources
| Resource | Description |
|----------|-------------|
| **Fabric Capacity** | Compute capacity (F2 SKU by default) |
| **Workspace** | Container for Fabric items |
| **Lakehouse** | Storage for checkpoints and data |
| **Eventhouse** | Real-time analytics with KQL database |
| **KQL Database** | Kusto database for log storage |
| **Eventstream (Processed)** | Custom endpoint → processing → Kusto |
| **Eventstream (Direct)** | Custom endpoint → direct ingestion → Kusto |
| **Notebook** | Spark streaming notebook (auto-deployed) |

## 📋 Prerequisites

1. **Terraform**: Version 1.5.0 or later
2. **Azure CLI**: Install and authenticate with `az login`
3. **Azure Subscription**: With permissions to create Fabric Capacity
4. **Fabric License**: Ensure your tenant has Fabric enabled
5. **Permissions**:
   - Azure: Contributor on subscription
   - Entra ID: User.Read.All (to resolve admin UPNs)
   - Fabric: Capacity administrator

## Authentication

The configuration uses Azure CLI authentication. Run:

```bash
az login
az account set --subscription "<your-subscription-id>"
```

## 🚀 Usage

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Configure Variables

Copy the example variables file and update with your values:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your:
- Azure Subscription ID
- Fabric admin email addresses
- Desired resource names and locations

### 3. Plan the Deployment

```bash
terraform plan
```

### 4. Apply the Configuration

```bash
terraform apply
```

### 5. Destroy Resources (when no longer needed)

```bash
terraform destroy
```

## Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `subscription_id` | Azure Subscription ID | (required) |
| `resource_group_name` | Resource group name | `rg-fabric-contoso` |
| `location` | Azure region | `eastus` |
| `fabric_capacity_name` | Fabric Capacity name | `fabriccapcontoso` |
| `fabric_sku` | Fabric SKU (F2-F2048) | `F2` |
| `fabric_admins` | List of admin UPNs | (required) |
| `workspace_name` | Workspace display name | `contoso Analytics Workspace` |
| `lakehouse_name` | Lakehouse display name | `contoso_lakehouse` |

## Fabric SKU Options

| SKU | Capacity Units | Best For |
|-----|----------------|----------|
| F2 | 2 CU | Development/Testing |
| F4 | 4 CU | Small workloads |
| F8 | 8 CU | Medium workloads |
| F16 | 16 CU | Production workloads |
| F32+ | 32+ CU | Enterprise workloads |

## 📤 Outputs

After deployment, Terraform will output:
- Resource Group ID and name
- Fabric Capacity ID and name
- Workspace ID and name
- Lakehouse ID and name
- Event Hub connection strings (send and listen)
- Kusto cluster URI

```bash
# Get all outputs
terraform output

# Get specific output
terraform output eventhub_send_connection_string
```

## 🔄 Notebook Deployment

The Spark notebook is automatically deployed from `../notebooks/eventhub_to_kusto_streaming.py`. Terraform performs token substitution for:

| Token | Injected Value |
|-------|----------------|
| `{{ .EventHubNamespace }}` | Event Hub namespace FQDN |
| `{{ .EventHubName }}` | Event Hub name |
| `{{ .EventHubConnectionString }}` | SAS connection string |
| `{{ .KustoClusterUri }}` | Kusto query service URI |
| `{{ .KustoDatabaseName }}` | KQL database name |
| `{{ .KustoTableName }}` | Target table name |

## 🌊 Eventstream Deployment

Two Eventstreams are deployed with different ingestion modes:

### Processed Ingestion (`eventstream.json.tmpl`)
- Custom Endpoint source for HTTP ingestion
- Passes through Eventstream processing engine
- Can add transformations in Fabric portal
- Target table: `logs` (configurable)

### Direct Ingestion (`eventstream-direct.json.tmpl`)
- Custom Endpoint source for HTTP ingestion
- Bypasses processing for lowest latency
- Raw JSON passthrough to Kusto
- Target table: `logs_direct` (configurable)

**Eventstream Token Substitution:**

| Token | Injected Value |
|-------|----------------|
| `{{ .WorkspaceID }}` | Fabric workspace ID |
| `{{ .DatabaseID }}` | KQL database ID |
| `{{ .DatabaseName }}` | KQL database name |
| `{{ .TableName }}` | Target table name |
| `{{ .EventstreamName }}` | Eventstream display name |

## ⚠️ Important Notes

- The Fabric provider is relatively new; check for updates at [Microsoft Fabric Provider](https://registry.terraform.io/providers/microsoft/fabric/latest)
- F2 is the smallest SKU and suitable for development/testing
- Fabric Capacity incurs costs even when paused; destroy when not in use
- Ensure your Azure AD user has appropriate permissions for Fabric administration
- The `terraform.tfstate` file contains sensitive data (SAS keys). Consider using remote state.
- Storage account and Event Hub namespace names must be globally unique

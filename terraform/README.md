# Microsoft Fabric Terraform Configuration

This Terraform configuration provisions a Microsoft Fabric Workspace with a Lakehouse.

## Resources Created

- **Azure Resource Group**: Container for the Fabric Capacity
- **Azure Fabric Capacity**: The compute capacity for Microsoft Fabric (F SKU)
- **Fabric Workspace**: A collaborative environment for Fabric items
- **Fabric Lakehouse**: A data lake with SQL analytics capabilities

## Prerequisites

1. **Terraform**: Version 1.5.0 or later
2. **Azure CLI**: Install and authenticate with `az login`
3. **Azure Subscription**: With permissions to create Fabric Capacity
4. **Fabric License**: Ensure your tenant has Fabric enabled

## Authentication

The configuration uses Azure CLI authentication. Run:

```bash
az login
az account set --subscription "<your-subscription-id>"
```

## Usage

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

## Outputs

After deployment, Terraform will output:
- Resource Group ID and name
- Fabric Capacity ID and name
- Workspace ID and name
- Lakehouse ID and name

## Notes

- The Fabric provider is relatively new; check for updates at [Microsoft Fabric Provider](https://registry.terraform.io/providers/microsoft/fabric/latest)
- F2 is the smallest SKU and suitable for development/testing
- Fabric Capacity incurs costs even when paused; destroy when not in use
- Ensure your Azure AD user has appropriate permissions for Fabric administration

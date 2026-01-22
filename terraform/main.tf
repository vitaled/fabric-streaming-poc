# Microsoft Fabric Workspace with Lakehouse
# Terraform configuration for provisioning Fabric resources

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.80.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = ">= 2.47.0"
    }
    fabric = {
      source  = "microsoft/fabric"
      version = ">= 0.1.0"
    }
  }
}

# Configure the Azure Provider
provider "azurerm" {
  features {}
  subscription_id     = var.subscription_id
  storage_use_azuread = true  # Use Azure AD auth instead of shared key for storage operations
}

# Configure the Microsoft Fabric Provider
provider "fabric" {
  # Uses Azure CLI or environment variables for authentication
  # Set FABRIC_TENANT_ID and use Azure CLI: az login
}

# Configure the Azure AD Provider
provider "azuread" {
  # Uses Azure CLI or environment variables for authentication
}

# Look up admin users by their UPN to get object IDs
data "azuread_user" "admins" {
  for_each            = toset(var.fabric_admins)
  user_principal_name = each.value
}

# Resource Group for Fabric Capacity
resource "azurerm_resource_group" "fabric_rg" {
  name     = var.resource_group_name
  location = var.location

  tags = var.tags
}

# Microsoft Fabric Capacity (F SKU)
resource "azurerm_fabric_capacity" "fabric_capacity" {
  name                = var.fabric_capacity_name
  resource_group_name = azurerm_resource_group.fabric_rg.name
  location            = azurerm_resource_group.fabric_rg.location

  sku {
    name = var.fabric_sku
    tier = "Fabric"
  }

  administration_members = var.fabric_admins

  tags = var.tags
}

# Data source to get the Fabric Capacity ID (UUID) from the capacity name
data "fabric_capacity" "main" {
  display_name = azurerm_fabric_capacity.fabric_capacity.name

  depends_on = [azurerm_fabric_capacity.fabric_capacity]
}

# Microsoft Fabric Workspace
resource "fabric_workspace" "main" {
  display_name = var.workspace_name
  description  = var.workspace_description
  capacity_id  = data.fabric_capacity.main.id

  identity = {
    type = "SystemAssigned"
  }

  depends_on = [data.fabric_capacity.main]
}

# Microsoft Fabric Lakehouse
resource "fabric_lakehouse" "main" {
  display_name = var.lakehouse_name
  description  = var.lakehouse_description
  workspace_id = fabric_workspace.main.id

  depends_on = [fabric_workspace.main]
}

# Azure Event Hub Namespace
resource "azurerm_eventhub_namespace" "main" {
  name                = var.eventhub_namespace_name
  location            = azurerm_resource_group.fabric_rg.location
  resource_group_name = azurerm_resource_group.fabric_rg.name
  sku                 = var.eventhub_sku
  capacity            = var.eventhub_capacity

  tags = var.tags
}

# Azure Event Hub
resource "azurerm_eventhub" "main" {
  name                = var.eventhub_name
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = azurerm_resource_group.fabric_rg.name
  partition_count     = var.eventhub_partition_count
  message_retention   = var.eventhub_message_retention
}

# Event Hub Authorization Rule for sending data
resource "azurerm_eventhub_authorization_rule" "send" {
  name                = "send-rule"
  namespace_name      = azurerm_eventhub_namespace.main.name
  eventhub_name       = azurerm_eventhub.main.name
  resource_group_name = azurerm_resource_group.fabric_rg.name

  listen = false
  send   = true
  manage = false
}

# Event Hub Authorization Rule for listening
resource "azurerm_eventhub_authorization_rule" "listen" {
  name                = "listen-rule"
  namespace_name      = azurerm_eventhub_namespace.main.name
  eventhub_name       = azurerm_eventhub.main.name
  resource_group_name = azurerm_resource_group.fabric_rg.name

  listen = true
  send   = false
  manage = false
}

# Assign Event Hub Data Sender role to Fabric Workspace Managed Identity
resource "azurerm_role_assignment" "workspace_eventhub_sender" {
  scope                = azurerm_eventhub_namespace.main.id
  role_definition_name = "Azure Event Hubs Data Sender"
  principal_id         = fabric_workspace.main.identity.service_principal_id

  depends_on = [
    fabric_workspace.main,
    azurerm_eventhub_namespace.main
  ]
}

# Assign Event Hub Data Receiver role to Fabric Workspace Managed Identity
resource "azurerm_role_assignment" "workspace_eventhub_receiver" {
  scope                = azurerm_eventhub_namespace.main.id
  role_definition_name = "Azure Event Hubs Data Receiver"
  principal_id         = fabric_workspace.main.identity.service_principal_id

  depends_on = [
    fabric_workspace.main,
    azurerm_eventhub_namespace.main
  ]
}

# Assign Event Hub Data Sender role to Fabric Admins
resource "azurerm_role_assignment" "admin_eventhub_sender" {
  for_each = toset(var.fabric_admins)

  scope                = azurerm_eventhub_namespace.main.id
  role_definition_name = "Azure Event Hubs Data Sender"
  principal_id         = data.azuread_user.admins[each.value].object_id

  depends_on = [azurerm_eventhub_namespace.main]
}

# Assign Event Hub Data Receiver role to Fabric Admins
resource "azurerm_role_assignment" "admin_eventhub_receiver" {
  for_each = toset(var.fabric_admins)

  scope                = azurerm_eventhub_namespace.main.id
  role_definition_name = "Azure Event Hubs Data Receiver"
  principal_id         = data.azuread_user.admins[each.value].object_id

  depends_on = [azurerm_eventhub_namespace.main]
}

# Azure Data Lake Storage Gen2
resource "azurerm_storage_account" "datalake" {
  name                      = var.storage_account_name
  resource_group_name       = azurerm_resource_group.fabric_rg.name
  location                  = azurerm_resource_group.fabric_rg.location
  account_tier              = var.storage_account_tier
  account_replication_type  = var.storage_replication_type
  account_kind              = "StorageV2"
  is_hns_enabled            = true  # Hierarchical namespace for Data Lake Gen2
  min_tls_version           = "TLS1_2"
  shared_access_key_enabled = false # Required by Azure policy - use Azure AD auth instead
  public_network_access_enabled = true
  allow_nested_items_to_be_public = false
  blob_properties {
    delete_retention_policy {
      days = 7
    }
    container_delete_retention_policy {
      days = 7
    }
  }

  tags = var.tags
}

# Data Lake Storage Container (File System)
resource "azurerm_storage_data_lake_gen2_filesystem" "main" {
  name               = var.datalake_filesystem_name
  storage_account_id = azurerm_storage_account.datalake.id
}

# Assign Storage Blob Data Contributor role to Fabric Workspace Identity
resource "azurerm_role_assignment" "workspace_identity_storage" {
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = fabric_workspace.main.identity.service_principal_id

  depends_on = [
    fabric_workspace.main,
    azurerm_storage_account.datalake
  ]
}

# Microsoft Fabric Eventhouse (Real-Time Analytics)
resource "fabric_eventhouse" "main" {
  display_name = var.eventhouse_name
  description  = var.eventhouse_description
  workspace_id = fabric_workspace.main.id

  depends_on = [fabric_workspace.main]
}

# KQL Database inside the Eventhouse
resource "fabric_kql_database" "main" {
  display_name = var.kql_database_name
  workspace_id = fabric_workspace.main.id

  configuration = {
    database_type = "ReadWrite"
    eventhouse_id = fabric_eventhouse.main.id
  }

  depends_on = [fabric_eventhouse.main]
}

# Microsoft Fabric Eventstream with Custom App source and Eventhouse destination
resource "fabric_eventstream" "main" {
  display_name = var.eventstream_name
  description  = var.eventstream_description
  workspace_id = fabric_workspace.main.id
  format       = "Default"

  definition = {
    "eventstream.json" = {
      source = "${path.module}/eventstream.json.tmpl"
      tokens = {
        "WorkspaceID"     = fabric_workspace.main.id
        "EventhouseID"    = fabric_eventhouse.main.id
        "DatabaseID"      = fabric_kql_database.main.id
        "DatabaseName"    = var.kql_database_name
        "TableName"       = var.eventstream_table_name
        "EventstreamName" = var.eventstream_name
      }
    }
  }

  depends_on = [fabric_kql_database.main]
}

# Microsoft Fabric Eventstream with Custom App source and Eventhouse destination (Direct Ingestion)
resource "fabric_eventstream" "direct" {
  display_name = var.eventstream_direct_name
  description  = var.eventstream_direct_description
  workspace_id = fabric_workspace.main.id
  format       = "Default"

  definition = {
    "eventstream.json" = {
      source = "${path.module}/eventstream-direct.json.tmpl"
      tokens = {
        "WorkspaceID"     = fabric_workspace.main.id
        "EventhouseID"    = fabric_eventhouse.main.id
        "DatabaseID"      = fabric_kql_database.main.id
        "DatabaseName"    = var.kql_database_name
        "TableName"       = var.eventstream_direct_table_name
        "EventstreamName" = var.eventstream_direct_name
      }
    }
  }

  depends_on = [fabric_kql_database.main]
}

# Microsoft Fabric Notebook for Event Hub to Kusto Structured Streaming
resource "fabric_notebook" "eventhub_to_kusto" {
  display_name = var.notebook_eventhub_to_kusto_name
  description  = var.notebook_eventhub_to_kusto_description
  workspace_id = fabric_workspace.main.id
  format       = "py"

  definition = {
    "notebook-content.py" = {
      source = "${path.module}/../notebooks/eventhub_to_kusto_streaming.py"
      tokens = {
        "EventHubNamespace"         = "${azurerm_eventhub_namespace.main.name}.servicebus.windows.net"
        "EventHubName"              = azurerm_eventhub.main.name
        "EventHubConnectionString"  = azurerm_eventhub_authorization_rule.listen.primary_connection_string
        "KustoClusterUri"           = fabric_kql_database.main.properties.query_service_uri
        "KustoDatabaseName"         = var.kql_database_name
        "KustoTableName"            = var.notebook_kusto_table_name
      }
    }
  }

  depends_on = [
    fabric_kql_database.main,
    azurerm_eventhub.main,
    azurerm_eventhub_namespace.main
  ]
}
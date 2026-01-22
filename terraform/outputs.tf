# Outputs for Microsoft Fabric Terraform Configuration

output "resource_group_name" {
  value       = azurerm_resource_group.fabric_rg.name
  description = "Name of the created resource group"
}

output "resource_group_id" {
  value       = azurerm_resource_group.fabric_rg.id
  description = "ID of the created resource group"
}

output "fabric_capacity_name" {
  value       = azurerm_fabric_capacity.fabric_capacity.name
  description = "Name of the Fabric Capacity"
}

output "fabric_capacity_id" {
  value       = azurerm_fabric_capacity.fabric_capacity.id
  description = "ID of the Fabric Capacity"
}

output "workspace_id" {
  value       = fabric_workspace.main.id
  description = "ID of the Fabric Workspace"
}

output "workspace_name" {
  value       = fabric_workspace.main.display_name
  description = "Display name of the Fabric Workspace"
}

output "lakehouse_id" {
  value       = fabric_lakehouse.main.id
  description = "ID of the Lakehouse"
}

output "lakehouse_name" {
  value       = fabric_lakehouse.main.display_name
  description = "Display name of the Lakehouse"
}

# Data Lake Storage Outputs
output "datalake_storage_account_name" {
  value       = azurerm_storage_account.datalake.name
  description = "Name of the Data Lake Storage Gen2 account"
}

output "datalake_storage_account_id" {
  value       = azurerm_storage_account.datalake.id
  description = "ID of the Data Lake Storage Gen2 account"
}

output "datalake_primary_dfs_endpoint" {
  value       = azurerm_storage_account.datalake.primary_dfs_endpoint
  description = "Primary DFS endpoint for Data Lake Storage Gen2"
}

output "datalake_filesystem_name" {
  value       = azurerm_storage_data_lake_gen2_filesystem.main.name
  description = "Name of the Data Lake Gen2 filesystem"
}

# Eventhouse Outputs
output "eventhouse_id" {
  value       = fabric_eventhouse.main.id
  description = "ID of the Eventhouse"
}

output "eventhouse_name" {
  value       = fabric_eventhouse.main.display_name
  description = "Display name of the Eventhouse"
}

# Eventstream Outputs
output "eventstream_id" {
  value       = fabric_eventstream.main.id
  description = "ID of the Eventstream (Processed Ingestion)"
}

output "eventstream_name" {
  value       = fabric_eventstream.main.display_name
  description = "Display name of the Eventstream (Processed Ingestion)"
}

# Eventstream Direct Ingestion Outputs
output "eventstream_direct_id" {
  value       = fabric_eventstream.direct.id
  description = "ID of the Eventstream (Direct Ingestion)"
}

output "eventstream_direct_name" {
  value       = fabric_eventstream.direct.display_name
  description = "Display name of the Eventstream (Direct Ingestion)"
}

# Azure Event Hub Outputs
output "eventhub_namespace_name" {
  value       = azurerm_eventhub_namespace.main.name
  description = "Name of the Event Hub Namespace"
}

output "eventhub_namespace_id" {
  value       = azurerm_eventhub_namespace.main.id
  description = "ID of the Event Hub Namespace"
}

output "eventhub_name" {
  value       = azurerm_eventhub.main.name
  description = "Name of the Event Hub"
}

output "eventhub_id" {
  value       = azurerm_eventhub.main.id
  description = "ID of the Event Hub"
}

output "eventhub_send_connection_string" {
  value       = azurerm_eventhub_authorization_rule.send.primary_connection_string
  description = "Connection string for sending to Event Hub"
  sensitive   = true
}

output "eventhub_listen_connection_string" {
  value       = azurerm_eventhub_authorization_rule.listen.primary_connection_string
  description = "Connection string for listening to Event Hub"
  sensitive   = true
}

# Fabric Notebook Outputs
output "notebook_eventhub_to_kusto_id" {
  value       = fabric_notebook.eventhub_to_kusto.id
  description = "ID of the Event Hub to Kusto streaming notebook"
}

output "notebook_eventhub_to_kusto_name" {
  value       = fabric_notebook.eventhub_to_kusto.display_name
  description = "Display name of the Event Hub to Kusto streaming notebook"
}
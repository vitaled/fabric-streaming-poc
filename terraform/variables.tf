# Variables for Microsoft Fabric Terraform Configuration

# Azure Subscription
variable "subscription_id" {
  type        = string
  description = "Azure Subscription ID"
}

# Resource Group
variable "resource_group_name" {
  type        = string
  description = "Name of the resource group for Fabric Capacity"
  default     = "rg-fabric-contoso"
}

variable "location" {
  type        = string
  description = "Azure region for resources"
  default     = "eastus"
}

# Fabric Capacity
variable "fabric_capacity_name" {
  type        = string
  description = "Name of the Fabric Capacity"
  default     = "fabriccapcontoso"

  validation {
    condition     = can(regex("^[a-z][a-z0-9]{2,62}$", var.fabric_capacity_name))
    error_message = "Fabric capacity name must be 3-63 characters, start with a letter, and contain only lowercase letters and numbers."
  }
}

variable "fabric_sku" {
  type        = string
  description = "SKU for Fabric Capacity (F2, F4, F8, F16, F32, F64, F128, F256, F512, F1024, F2048)"
  default     = "F2"

  validation {
    condition     = contains(["F2", "F4", "F8", "F16", "F32", "F64", "F128", "F256", "F512", "F1024", "F2048"], var.fabric_sku)
    error_message = "Invalid Fabric SKU. Must be one of: F2, F4, F8, F16, F32, F64, F128, F256, F512, F1024, F2048."
  }
}

variable "fabric_admins" {
  type        = list(string)
  description = "List of admin user principal names (UPNs) or object IDs for Fabric Capacity"
}

# Fabric Workspace
variable "workspace_name" {
  type        = string
  description = "Display name for the Fabric Workspace"
  default     = "contoso Analytics Workspace"
}

variable "workspace_description" {
  type        = string
  description = "Description for the Fabric Workspace"
  default     = "Microsoft Fabric workspace for contoso analytics and data engineering"
}

# Lakehouse
variable "lakehouse_name" {
  type        = string
  description = "Display name for the Lakehouse"
  default     = "contoso_lakehouse"
}

variable "lakehouse_description" {
  type        = string
  description = "Description for the Lakehouse"
  default     = "Central lakehouse for contoso data storage and analytics"
}

# Eventhouse
variable "eventhouse_name" {
  type        = string
  description = "Display name for the Eventhouse (Real-Time Analytics)"
  default     = "contoso_eventhouse"
}

variable "eventhouse_description" {
  type        = string
  description = "Description for the Eventhouse"
  default     = "Real-time analytics eventhouse for contoso streaming data"
}

# KQL Database
variable "kql_database_name" {
  type        = string
  description = "Display name for the KQL Database inside the Eventhouse"
  default     = "contoso_db"
}

# Eventstream
variable "eventstream_name" {
  type        = string
  description = "Display name for the Eventstream"
  default     = "contoso_eventstream"
}

variable "eventstream_description" {
  type        = string
  description = "Description for the Eventstream"
  default     = "Eventstream for ingesting real-time log data"
}

variable "eventstream_table_name" {
  type        = string
  description = "Name of the destination table in the KQL Database"
  default     = "logs"
}

# Eventstream (Direct Ingestion)
variable "eventstream_direct_name" {
  type        = string
  description = "Display name for the Eventstream with Direct Ingestion"
  default     = "contoso_eventstream_direct"
}

variable "eventstream_direct_description" {
  type        = string
  description = "Description for the Eventstream with Direct Ingestion"
  default     = "Eventstream for ingesting real-time log data using direct ingestion"
}

variable "eventstream_direct_table_name" {
  type        = string
  description = "Name of the destination table in the KQL Database for direct ingestion"
  default     = "logs_direct"
}

# Azure Event Hub
variable "eventhub_namespace_name" {
  type        = string
  description = "Name of the Event Hub Namespace"
  default     = "ehns-contoso"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9-]{4,48}[a-zA-Z0-9]$", var.eventhub_namespace_name))
    error_message = "Event Hub Namespace name must be 6-50 characters, start with a letter, end with a letter or number, and contain only letters, numbers, and hyphens."
  }
}

variable "eventhub_name" {
  type        = string
  description = "Name of the Event Hub"
  default     = "contoso-logs"
}

variable "eventhub_sku" {
  type        = string
  description = "SKU for Event Hub Namespace (Basic, Standard, Premium)"
  default     = "Standard"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.eventhub_sku)
    error_message = "Event Hub SKU must be one of: Basic, Standard, Premium."
  }
}

variable "eventhub_capacity" {
  type        = number
  description = "Throughput units for the Event Hub Namespace (1-20 for Standard)"
  default     = 1
}

variable "eventhub_partition_count" {
  type        = number
  description = "Number of partitions for the Event Hub (2-32)"
  default     = 2

  validation {
    condition     = var.eventhub_partition_count >= 2 && var.eventhub_partition_count <= 32
    error_message = "Partition count must be between 2 and 32."
  }
}

variable "eventhub_message_retention" {
  type        = number
  description = "Message retention in days (1-7 for Standard, 1-90 for Premium)"
  default     = 1
}

# Fabric Notebook
variable "notebook_eventhub_to_kusto_name" {
  type        = string
  description = "Display name for the Event Hub to Kusto streaming notebook"
  default     = "EventHub_to_Kusto_Streaming"
}

variable "notebook_eventhub_to_kusto_description" {
  type        = string
  description = "Description for the Event Hub to Kusto streaming notebook"
  default     = "Spark Structured Streaming notebook that reads from Event Hub and writes to Kusto database"
}

variable "notebook_kusto_table_name" {
  type        = string
  description = "Name of the Kusto table to write streaming data to"
  default     = "logs_streaming"
}

# Tags
variable "tags" {
  type        = map(string)
  description = "Tags to apply to Azure resources"
  default = {
    Environment = "Development"
    Project     = "contoso"
    ManagedBy   = "Terraform"
  }
}

# Data Lake Storage
variable "storage_account_name" {
  type        = string
  description = "Name of the Azure Data Lake Storage Gen2 account"
  default     = "dlscontoso"

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Storage account name must be 3-24 characters, and contain only lowercase letters and numbers."
  }
}

variable "storage_account_tier" {
  type        = string
  description = "Performance tier for the storage account (Standard or Premium)"
  default     = "Standard"

  validation {
    condition     = contains(["Standard", "Premium"], var.storage_account_tier)
    error_message = "Storage account tier must be either Standard or Premium."
  }
}

variable "storage_replication_type" {
  type        = string
  description = "Replication type for the storage account (LRS, GRS, RAGRS, ZRS, GZRS, RAGZRS)"
  default     = "LRS"

  validation {
    condition     = contains(["LRS", "GRS", "RAGRS", "ZRS", "GZRS", "RAGZRS"], var.storage_replication_type)
    error_message = "Invalid replication type. Must be one of: LRS, GRS, RAGRS, ZRS, GZRS, RAGZRS."
  }
}

variable "datalake_filesystem_name" {
  type        = string
  description = "Name of the Data Lake Gen2 filesystem (container)"
  default     = "contoso-data"
}
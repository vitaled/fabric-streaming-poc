# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {}
# META   }
# META }

# MARKDOWN ********************

# # Event Hub to Kusto Structured Streaming
# 
# This notebook reads JSON data from Azure Event Hub using Spark Structured Streaming
# and writes the results to a Kusto (KQL) database table in real-time.
# 
# **Authentication:** 
# - Event Hub: SAS Token (via connection string)
# - Kusto: Fabric Workspace Managed Identity

# CELL ********************

# Configuration - These values are injected by Terraform
# Event Hub Configuration
EVENTHUB_NAMESPACE = "{{ .EventHubNamespace }}"
EVENTHUB_NAME = "{{ .EventHubName }}"
EVENTHUB_CONSUMER_GROUP = "$Default"

# Event Hub connection string with SAS token (injected by Terraform)
EVENTHUB_CONNECTION_STRING = "{{ .EventHubConnectionString }}"

# Kusto Configuration
KUSTO_CLUSTER_URI = "{{ .KustoClusterUri }}"
KUSTO_DATABASE = "{{ .KustoDatabaseName }}"
KUSTO_TABLE = "{{ .KustoTableName }}"

# Checkpoint Configuration - Use the attached lakehouse's Files folder
CHECKPOINT_PATH = f"Files/checkpoints/eventhub_to_kusto/{KUSTO_TABLE}"

# Set to True to clear checkpoint and start fresh from beginning
CLEAR_CHECKPOINT = True

print(f"Event Hub: {EVENTHUB_NAMESPACE}/{EVENTHUB_NAME}")
print(f"Connection String: [SAS token configured]")
print(f"Kusto: {KUSTO_CLUSTER_URI}/{KUSTO_DATABASE}/{KUSTO_TABLE}")
print(f"Checkpoint Path: {CHECKPOINT_PATH}")
print(f"Clear Checkpoint: {CLEAR_CHECKPOINT}")

# Clear checkpoint if requested
if CLEAR_CHECKPOINT:
    try:
        mssparkutils.fs.rm(CHECKPOINT_PATH, True)
        print(f"✓ Checkpoint cleared: {CHECKPOINT_PATH}")
    except Exception as e:
        print(f"No checkpoint to clear (this is OK for first run): {e}")

# MARKDOWN ********************

# ## Setup Event Hub Connection
# 
# Configure Event Hub connection using SAS token authentication.

# CELL ********************

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType, DoubleType
import json

# Build Event Hub configuration for Spark connector
# Starting position: Start from the beginning of the stream
starting_position = {
    "offset": "-1",
    "seqNo": -1,
    "enqueuedTime": None,
    "isInclusive": True
}
starting_position_json = json.dumps(starting_position)

# Get Kusto token using Fabric managed identity
kusto_token = mssparkutils.credentials.getToken(KUSTO_CLUSTER_URI)
print(f"✓ Obtained Kusto token (length: {len(kusto_token)} chars)")

# Encrypt the connection string for secure transmission
encrypted_conn_string = sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(EVENTHUB_CONNECTION_STRING)

# Event Hub Spark connector configuration with SAS token
eventhub_conf = {
    "eventhubs.connectionString": encrypted_conn_string,
    "eventhubs.consumerGroup": EVENTHUB_CONSUMER_GROUP,
    "eventhubs.startingPosition": starting_position_json
}

print("✓ Event Hub configuration set up with SAS token authentication")
print(f"Consumer Group: {EVENTHUB_CONSUMER_GROUP}")
print(f"Starting Position: {starting_position_json}")

# MARKDOWN ********************

# ## Test Event Hub Connection (Batch Read)
# 
# Verify connectivity and check if there's data in Event Hub before starting the stream.

# CELL ********************

# Test Event Hub connection with a batch read
# This helps verify connectivity before starting the stream
print("Testing Event Hub connection with batch read...")

try:
    df_test = (
        spark
        .read
        .format("eventhubs")
        .options(**eventhub_conf)
        .load()
    )
    
    count = df_test.count()
    print(f"✓ SUCCESS: Connected to Event Hub. Found {count} events.")
    
    if count > 0:
        print("\nSample events (first 3):")
        df_test.select(
            col("enqueuedTime"),
            col("offset"),
            col("sequenceNumber"),
            col("body").cast("string").alias("body")
        ).show(3, truncate=100)
    else:
        print("\n⚠ WARNING: No events found in Event Hub!")
        print("Either the Event Hub is empty or events have expired (check retention period).")
        print("Run send_logs_to_eventhub.py script to send test data.")
        
except Exception as e:
    print(f"✗ ERROR connecting to Event Hub: {e}")
    raise

# MARKDOWN ********************

# ## Define JSON Schema
# 
# Define the schema for the incoming JSON messages from Event Hub.

# CELL ********************

from pyspark.sql.functions import get_json_object

# Define the schema for incoming JSON data
# This matches the docCreator log format from Kubernetes pods
# The 'data' field is kept as a JSON string for flexibility

json_schema = StructType([
    StructField("category", StringType(), True),
    StructField("container", StringType(), True),
    StructField("containerId", StringType(), True),
    StructField("containerImage", StringType(), True),
    StructField("containerImageId", StringType(), True),
    StructField("file", StringType(), True),
    StructField("host", StringType(), True),
    StructField("namespace", StringType(), True),
    StructField("pod", StringType(), True),
    StructField("podIp", StringType(), True),
    StructField("podOwner", StringType(), True),
    StructField("resource", StringType(), True),
    StructField("resourceGroup", StringType(), True),
    StructField("severity", StringType(), True),
    StructField("source", StringType(), True),
    StructField("subscription", StringType(), True),
    StructField("type", StringType(), True),
    StructField("timestamp", StringType(), True)
    # Note: 'data' field is extracted separately as a JSON string
])

print("JSON schema defined for docCreator log format")
print(f"Top-level fields: {len(json_schema.fields)}")
print("'data' field will be stored as JSON string")

# MARKDOWN ********************

# ## Read from Event Hub with Structured Streaming

# CELL ********************

# Read streaming data from Event Hub
df_raw = (
    spark
    .readStream
    .format("eventhubs")
    .options(**eventhub_conf)
    .load()
)

# Parse the Event Hub message body (which is in binary format) as JSON
# Keep the 'data' field as a JSON string
df_parsed = (
    df_raw
    .select(
        col("enqueuedTime").alias("enqueued_time"),
        col("sequenceNumber").alias("sequence_number"),
        col("body").cast("string").alias("body_string"),
        from_json(col("body").cast("string"), json_schema).alias("json")
    )
    .select(
        "enqueued_time",
        "sequence_number",
        # Top-level fields
        col("json.container").alias("container"),
        col("json.containerId").alias("container_id"),
        col("json.containerImage").alias("container_image"),
        col("json.containerImageId").alias("container_image_id"),
        col("json.file").alias("file"),
        col("json.host").alias("host"),
        col("json.namespace").alias("namespace"),
        col("json.pod").alias("pod"),
        col("json.podIp").alias("pod_ip"),
        col("json.podOwner").alias("pod_owner"),
        col("json.resource").alias("resource"),
        col("json.resourceGroup").alias("resource_group"),
        col("json.severity").alias("severity"),
        col("json.source").alias("source"),
        col("json.subscription").alias("subscription"),
        col("json.type").alias("type"),
        col("json.timestamp").alias("log_timestamp"),
        # Extract 'data' field as JSON string using get_json_object
        get_json_object(col("body_string"), "$.data").alias("data")
    )
    .withColumn("ingestion_time", current_timestamp())
)

print("Streaming DataFrame created successfully")
print("Schema with 'data' stored as JSON string:")
df_parsed.printSchema()

# MARKDOWN ********************

# ## Configure Kusto Sink
# 
# Set up the connection to write data to Kusto using the Kusto Spark connector with managed identity.

# CELL ********************

# Kusto Spark connector options using access token (obtained in setup cell)
kusto_options = {
    "kustoCluster": KUSTO_CLUSTER_URI,
    "kustoDatabase": KUSTO_DATABASE,
    "kustoTable": KUSTO_TABLE,
    "accessToken": kusto_token,
    "tableCreateOptions": "CreateIfNotExist"
}

print(f"Kusto sink configured for table: {KUSTO_DATABASE}.{KUSTO_TABLE}")

# MARKDOWN ********************

# ## Start Streaming Query
# 
# Write the streaming data to Kusto using the Kusto Spark connector with structured streaming.

# CELL ********************

# Write streaming data to Kusto
query = (
    df_parsed
    .writeStream
    .format("com.microsoft.kusto.spark.datasink.KustoSinkProvider")
    .options(**kusto_options)
    .option("checkpointLocation", CHECKPOINT_PATH)
    .trigger(processingTime="30 seconds")
    .start()
)

print(f"Streaming query started. Query ID: {query.id}")
print(f"Query Name: {query.name}")
print(f"Query Status: {query.status}")

# MARKDOWN ********************

# ## Monitor Streaming Query
# 
# Use this cell to monitor the streaming query status.

# CELL ********************

# Monitor the streaming query
# Uncomment and run to check status
# query.status
# query.recentProgress
# query.lastProgress

# To stop the query, uncomment and run:
# query.stop()

# Display active streams
for stream in spark.streams.active:
    print(f"Stream: {stream.name}, ID: {stream.id}, Status: {stream.status}")

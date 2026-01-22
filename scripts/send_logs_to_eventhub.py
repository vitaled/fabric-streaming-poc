#!/usr/bin/env python3
"""
Send fake log events to Azure Event Hub.
This is a variant of generate_partitioned_logs.py that sends events to Event Hub
instead of writing to files.
"""

import json
import uuid
import random
import os
import time
from datetime import datetime, timedelta
from typing import Optional

import yaml
from azure.eventhub import EventHubProducerClient, EventData, TransportType
from azure.identity import (
    DefaultAzureCredential,
    ClientSecretCredential,
    InteractiveBrowserCredential,
    AzureCliCredential,
    ManagedIdentityCredential
)

# Default configuration values
DEFAULTS = {
    "mode": "batch",
    "connection_string": None,
    "eventhub_name": None,
    "namespace": None,
    "use_managed_identity": False,
    "auth_method": None,  # 'default', 'client_secret', 'interactive', 'cli', 'managed_identity'
    "tenant_id": None,
    "client_id": None,
    "client_secret": None,
    "start": None,
    "end": None,
    "duration_hours": 1,
    "total_events": None,
    "events_per_batch": 100,
    "delay_between_batches": 0.0,
    "events_per_second": 10,
    "duration_seconds": None
}

# Template data from example_json.json
TEMPLATE = {
    "category": {},
    "container": "doccreator-backend",
    "containerId": "containerd://7c4f4ab34671afb1975126e8c0fca8ce23b62b318c7435ff78d0f73116359d34",
    "containerImage": "crcontosoprdgwc.azurecr.io/infonds:4.3.3937",
    "containerImageId": "crcontosoprdgwc.azurecr.io/infonds@sha256:52f0be0aacfce5d345b5dab9efabe3e0ede9f97ce4eeb5831fc01cf4e14d84d7",
    "file": "/var/log/pods/int-doccreator_doccreator-backend-master-api-deployment-685948cb57-tpg4f_f0db2d83-0bb4-4f1d-9003-a6d806e8a749/doccreator-backend/0.log",
    "host": "aks-applications-18125824-vmss0000yt",
    "namespace": "int-doccreator",
    "pod": "doccreator-backend-master-api-deployment-685948cb57-tpg4f",
    "podIp": "10.3.132.14",
    "podOwner": "ReplicaSet/doccreator-backend-master-api-deployment-685948cb57",
    "resource": "aks-nucleus-npe-ne",
    "resourceGroup": "rg-nucleus-npe-ne",
    "severity": "info",
    "source": "kubernetes",
    "subscription": "86873dce-75a0-4ed5-ada5-7dc31e90cc91",
    "type": "pod"
}

# Fake data options for generating variety
CLIENTS = [
    "contoso Standard PIB",
    "contoso Premium Client",
    "Enterprise Solutions GmbH",
    "Financial Services AG",
    "Insurance Corp"
]

DOCUMENT_DEFINITIONS = [
    "contoso_standard_pib",
    "annual_report",
    "quarterly_statement",
    "fund_factsheet",
    "portfolio_summary"
]

TEMPLATE_CODES = [
    "aktie_stammaktie",
    "bond_certificate",
    "fund_report",
    "etf_factsheet",
    "derivative_notice"
]

TEMPLATE_NAMES = [
    "Aktie - Stammaktie",
    "Bond Certificate",
    "Fund Report",
    "ETF Factsheet",
    "Derivative Notice"
]

LOCALES = ["de_DE", "en_US", "fr_FR", "it_IT", "es_ES"]

NAMESPACES = ["int-doccreator", "prd-doccreator", "dev-doccreator", "stg-doccreator"]

PODS = [
    "doccreator-backend-master-api-deployment-685948cb57-tpg4f",
    "doccreator-backend-master-api-deployment-685948cb57-abc12",
    "doccreator-backend-worker-deployment-7f8d9c-xyz99",
    "doccreator-backend-scheduler-deployment-3e4f5g-def45"
]

LOG_TYPES = ["DocGeneration", "TemplateLoad", "DataFetch", "PDFRender", "CacheHit"]

SEVERITIES = ["info", "warning", "debug", "error"]

IDENTIFIERS = [
    "DE0007100000",
    "DE0008404005", 
    "DE0005140008",
    "DE0007164600",
    "DE0005552004",
    "LU0378449770",
    "IE00B4L5Y983"
]


def generate_fake_data(timestamp: datetime) -> dict:
    """Generate fake data block with realistic values."""
    time_total = random.randint(200, 5000)
    time_doc_creator = int(time_total * random.uniform(0.7, 0.95))
    time_calculation = int(time_total * random.uniform(0.02, 0.1))
    time_gc = int(time_total * random.uniform(0.01, 0.05))
    
    template_idx = random.randint(0, len(TEMPLATE_CODES) - 1)
    
    return {
        "apiType": random.choice(["REST", "SOAP", "GraphQL"]),
        "authorizationMode": random.choice(["AuthorizedOnly", "Anonymous", "Token"]),
        "backendGui": random.choice([True, False]),
        "client": random.choice(CLIENTS),
        "contentClient": random.choice(CLIENTS),
        "dataClassification": random.choice(["Public", "Internal", "Confidential"]),
        "documentContentLength": random.randint(10000, 500000),
        "documentDefinition": random.choice(DOCUMENT_DEFINITIONS),
        "documentName": f"document-{uuid.uuid4().hex[:8]}.pdf",
        "externalSource": random.choice(["", "bloomberg", "refinitiv", "internal"]),
        "generationEngine": "docCreator",
        "infondsVersion": f"4.{random.randint(1, 5)}.{random.randint(1000, 4000)}",
        "locale": random.choice(LOCALES),
        "logType": random.choice(LOG_TYPES),
        "mediaType": random.choice(["PDF", "HTML", "DOCX"]),
        "pageConfigurationCode": "contoso",
        "serialNumber": str(uuid.uuid4()),
        "sourceAction": random.choice(["DocumentGeneration", "TemplatePreview", "BatchProcess"]),
        "sourceCategory": random.choice(["API", "Scheduler", "Manual"]),
        "templateAuthorizationDate": (timestamp - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%dT%H:%M:%S.0000000Z"),
        "templateCode": TEMPLATE_CODES[template_idx],
        "templateName": TEMPLATE_NAMES[template_idx],
        "templateVersion": random.randint(1, 50),
        "templateVersionDate": (timestamp - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%dT%H:%M:%S.0000000Z"),
        "timeTotal": time_total,
        "traceId": uuid.uuid4().hex,
        "traceParentId": uuid.uuid4().hex[:16],
        "uploadToDocRepository": random.choice([True, False]),
        "timeDocCreator": time_doc_creator,
        "identifier": random.choice(IDENTIFIERS),
        "timeCalculation": time_calculation,
        "timeGC": time_gc
    }


def generate_log_record(timestamp: datetime) -> dict:
    """Generate a complete log record for the given timestamp."""
    record = TEMPLATE.copy()
    record["timestamp"] = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f0Z")
    record["namespace"] = random.choice(NAMESPACES)
    record["pod"] = random.choice(PODS)
    record["severity"] = random.choice(SEVERITIES)
    record["podIp"] = f"10.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    record["host"] = f"aks-applications-{random.randint(10000000, 99999999)}-vmss{random.randint(1000, 9999)}"
    record["data"] = generate_fake_data(timestamp)
    return record


def create_producer_client(
    connection_string: Optional[str] = None,
    eventhub_name: Optional[str] = None,
    fully_qualified_namespace: Optional[str] = None,
    use_managed_identity: bool = False,
    auth_method: Optional[str] = None,
    tenant_id: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    use_websockets: bool = True
) -> EventHubProducerClient:
    """
    Create an Event Hub producer client.
    
    Args:
        connection_string: Event Hub connection string (includes EntityPath or use eventhub_name)
        eventhub_name: Event Hub name (if not included in connection string)
        fully_qualified_namespace: Fully qualified namespace (e.g., 'mynamespace.servicebus.windows.net')
        use_managed_identity: Use Azure DefaultAzureCredential for authentication (legacy, use auth_method instead)
        auth_method: Authentication method - 'default', 'client_secret', 'interactive', 'cli', 'managed_identity'
        tenant_id: Azure AD tenant ID (required for client_secret auth)
        client_id: Azure AD application/client ID (required for client_secret auth)
        client_secret: Azure AD client secret (required for client_secret auth)
        use_websockets: Use AMQP over WebSockets (port 443) instead of raw AMQP (port 5671)
    
    Returns:
        EventHubProducerClient
    """
    # Use WebSockets transport to work through firewalls (port 443 instead of 5671)
    transport_type = TransportType.AmqpOverWebsocket if use_websockets else TransportType.Amqp
    
    # Determine authentication method
    # Support legacy use_managed_identity flag
    if use_managed_identity and not auth_method:
        auth_method = "default"
    
    # If auth_method is specified, use Entra ID authentication
    if auth_method and fully_qualified_namespace:
        credential = _get_credential(auth_method, tenant_id, client_id, client_secret)
        print(f"Using Entra ID authentication method: {auth_method}")
        return EventHubProducerClient(
            fully_qualified_namespace=fully_qualified_namespace,
            eventhub_name=eventhub_name,
            credential=credential,
            transport_type=transport_type
        )
    elif connection_string:
        print("Using connection string authentication")
        return EventHubProducerClient.from_connection_string(
            conn_str=connection_string,
            eventhub_name=eventhub_name,
            transport_type=transport_type
        )
    else:
        raise ValueError(
            "Either connection_string or (fully_qualified_namespace + auth_method) must be provided.\n"
            "Supported auth_method values: 'default', 'client_secret', 'interactive', 'cli', 'managed_identity'"
        )


def _get_credential(auth_method: str, tenant_id: Optional[str], client_id: Optional[str], client_secret: Optional[str]):
    """
    Get the appropriate Azure credential based on the auth method.
    
    Args:
        auth_method: Authentication method
        tenant_id: Azure AD tenant ID
        client_id: Azure AD application/client ID  
        client_secret: Azure AD client secret
    
    Returns:
        Azure credential object
    """
    auth_method = auth_method.lower()
    
    if auth_method == "client_secret":
        if not all([tenant_id, client_id, client_secret]):
            raise ValueError("client_secret auth requires tenant_id, client_id, and client_secret")
        return ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
    elif auth_method == "interactive":
        return InteractiveBrowserCredential(
            tenant_id=tenant_id,
            client_id=client_id
        ) if tenant_id else InteractiveBrowserCredential()
    elif auth_method == "cli":
        return AzureCliCredential()
    elif auth_method == "managed_identity":
        return ManagedIdentityCredential(client_id=client_id) if client_id else ManagedIdentityCredential()
    elif auth_method == "default":
        return DefaultAzureCredential()
    else:
        raise ValueError(
            f"Unknown auth_method: {auth_method}. "
            "Supported values: 'default', 'client_secret', 'interactive', 'cli', 'managed_identity'"
        )


def send_events_to_eventhub(
    producer: EventHubProducerClient,
    start_time: datetime,
    end_time: datetime,
    events_per_batch: int = 100,
    total_events: Optional[int] = None,
    delay_between_batches: float = 0.0,
    realtime_mode: bool = False
):
    """
    Send generated log events to Event Hub.
    
    Args:
        producer: EventHubProducerClient instance
        start_time: Start datetime for generated timestamps
        end_time: End datetime for generated timestamps
        events_per_batch: Number of events per batch (default: 100)
        total_events: Total number of events to send (default: None = calculate from time range)
        delay_between_batches: Delay in seconds between batches (default: 0)
        realtime_mode: If True, send events with current timestamps in real-time
    """
    if total_events is None:
        # Calculate based on time range (roughly 2 events per second)
        duration_seconds = (end_time - start_time).total_seconds()
        total_events = int(duration_seconds * 2)
    
    print(f"Sending {total_events} events to Event Hub")
    print(f"Timestamp range: {start_time} to {end_time}")
    print(f"Events per batch: {events_per_batch}")
    print(f"Realtime mode: {realtime_mode}")
    print("-" * 60)
    
    sent_count = 0
    batch_count = 0
    start_process_time = time.time()
    
    while sent_count < total_events:
        # Create a batch
        event_data_batch = producer.create_batch()
        batch_events = 0
        
        while batch_events < events_per_batch and sent_count < total_events:
            # Generate timestamp
            if realtime_mode:
                timestamp = datetime.now()
            else:
                # Distribute timestamps evenly across the time range
                progress = sent_count / total_events
                timestamp = start_time + (end_time - start_time) * progress
            
            # Generate the log record
            record = generate_log_record(timestamp)
            event_json = json.dumps(record, separators=(',', ':'))
            
            try:
                event_data_batch.add(EventData(event_json))
                batch_events += 1
                sent_count += 1
            except ValueError:
                # Batch is full, send what we have
                break
        
        # Send the batch
        if batch_events > 0:
            producer.send_batch(event_data_batch)
            batch_count += 1
            
            if batch_count % 10 == 0:
                elapsed = time.time() - start_process_time
                rate = sent_count / elapsed if elapsed > 0 else 0
                print(f"Sent {sent_count}/{total_events} events ({batch_count} batches, {rate:.1f} events/sec)")
        
        # Optional delay between batches
        if delay_between_batches > 0:
            time.sleep(delay_between_batches)
    
    elapsed = time.time() - start_process_time
    rate = sent_count / elapsed if elapsed > 0 else 0
    
    print("-" * 60)
    print(f"Complete! Sent {sent_count} events in {batch_count} batches")
    print(f"Total time: {elapsed:.2f} seconds ({rate:.1f} events/sec)")
    
    return sent_count, batch_count


def send_continuous_stream(
    producer: EventHubProducerClient,
    events_per_second: float = 10,
    duration_seconds: Optional[int] = None,
    events_per_batch: int = 10
):
    """
    Send a continuous stream of events with current timestamps.
    
    Args:
        producer: EventHubProducerClient instance
        events_per_second: Target rate of events per second
        duration_seconds: How long to run (None = run forever)
        events_per_batch: Number of events per batch
    """
    print(f"Starting continuous stream at ~{events_per_second} events/second")
    if duration_seconds:
        print(f"Duration: {duration_seconds} seconds")
    else:
        print("Duration: indefinite (Ctrl+C to stop)")
    print("-" * 60)
    
    sent_count = 0
    batch_count = 0
    start_time = time.time()
    
    try:
        while True:
            batch_start = time.time()
            
            # Create and send a batch
            event_data_batch = producer.create_batch()
            for _ in range(events_per_batch):
                record = generate_log_record(datetime.now())
                event_json = json.dumps(record, separators=(',', ':'))
                try:
                    event_data_batch.add(EventData(event_json))
                except ValueError:
                    break
            
            producer.send_batch(event_data_batch)
            sent_count += events_per_batch
            batch_count += 1
            
            # Calculate delay to maintain target rate
            batch_duration = time.time() - batch_start
            target_batch_duration = events_per_batch / events_per_second
            sleep_time = max(0, target_batch_duration - batch_duration)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            
            # Progress update
            if batch_count % 100 == 0:
                elapsed = time.time() - start_time
                actual_rate = sent_count / elapsed if elapsed > 0 else 0
                print(f"Sent {sent_count} events ({actual_rate:.1f} events/sec)")
            
            # Check duration limit
            if duration_seconds and (time.time() - start_time) >= duration_seconds:
                break
                
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    elapsed = time.time() - start_time
    rate = sent_count / elapsed if elapsed > 0 else 0
    print("-" * 60)
    print(f"Complete! Sent {sent_count} events in {elapsed:.2f} seconds ({rate:.1f} events/sec)")
    
    return sent_count


def load_config(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config if config else {}


def get_config(args) -> dict:
    """
    Build final configuration by merging (in order of priority):
    1. Default values (lowest priority)
    2. Environment variables
    3. Config file values
    4. CLI arguments (highest priority)
    """
    config = DEFAULTS.copy()
    
    # Apply environment variables
    env_mapping = {
        "EVENTHUB_CONNECTION_STRING": "connection_string",
        "EVENTHUB_NAME": "eventhub_name",
        "EVENTHUB_NAMESPACE": "namespace",
        "AZURE_TENANT_ID": "tenant_id",
        "AZURE_CLIENT_ID": "client_id",
        "AZURE_CLIENT_SECRET": "client_secret",
    }
    for env_key, config_key in env_mapping.items():
        env_value = os.environ.get(env_key)
        if env_value:
            config[config_key] = env_value
    
    # Load config file if provided
    if args.config:
        file_config = load_config(args.config)
        # Map YAML keys to config keys (support multiple naming conventions)
        key_mapping = {
            # Connection settings
            "connection_string": "connection_string",
            "connectionString": "connection_string",
            "eventhub_name": "eventhub_name",
            "eventhubName": "eventhub_name",
            "namespace": "namespace",
            "use_managed_identity": "use_managed_identity",
            "useManagedIdentity": "use_managed_identity",
            # Entra ID authentication settings
            "auth_method": "auth_method",
            "authMethod": "auth_method",
            "tenant_id": "tenant_id",
            "tenantId": "tenant_id",
            "client_id": "client_id",
            "clientId": "client_id",
            "client_secret": "client_secret",
            "clientSecret": "client_secret",
            # Mode settings
            "mode": "mode",
            # Batch settings
            "start": "start",
            "end": "end",
            "duration_hours": "duration_hours",
            "durationHours": "duration_hours",
            "total_events": "total_events",
            "totalEvents": "total_events",
            "events_per_batch": "events_per_batch",
            "eventsPerBatch": "events_per_batch",
            "delay_between_batches": "delay_between_batches",
            "delayBetweenBatches": "delay_between_batches",
            # Continuous settings
            "events_per_second": "events_per_second",
            "eventsPerSecond": "events_per_second",
            "duration_seconds": "duration_seconds",
            "durationSeconds": "duration_seconds",
        }
        for yaml_key, config_key in key_mapping.items():
            if yaml_key in file_config:
                config[config_key] = file_config[yaml_key]
    
    # Override with CLI arguments if provided (non-None values)
    cli_mapping = {
        "connection_string": "connection_string",
        "eventhub_name": "eventhub_name",
        "namespace": "namespace",
        "use_managed_identity": "use_managed_identity",
        "auth_method": "auth_method",
        "tenant_id": "tenant_id",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "mode": "mode",
        "start": "start",
        "end": "end",
        "duration_hours": "duration_hours",
        "total_events": "total_events",
        "events_per_batch": "events_per_batch",
        "delay_between_batches": "delay_between_batches",
        "events_per_second": "events_per_second",
        "duration_seconds": "duration_seconds",
    }
    for arg_name, config_key in cli_mapping.items():
        arg_value = getattr(args, arg_name, None)
        if arg_value is not None:
            config[config_key] = arg_value
    
    return config


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Send fake log events to Azure Event Hub"
    )
    
    # Config file option
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=None,
        help="Path to YAML configuration file (overrides defaults, CLI args override config)"
    )
    
    # Connection options
    conn_group = parser.add_argument_group('Connection')
    conn_group.add_argument(
        "--connection-string",
        default=None,
        help="Event Hub connection string (or set EVENTHUB_CONNECTION_STRING env var)"
    )
    conn_group.add_argument(
        "--eventhub-name",
        default=None,
        help="Event Hub name (or set EVENTHUB_NAME env var)"
    )
    conn_group.add_argument(
        "--namespace",
        default=None,
        help="Fully qualified namespace for managed identity auth (e.g., 'mynamespace.servicebus.windows.net')"
    )
    conn_group.add_argument(
        "--use-managed-identity",
        action="store_true",
        default=None,
        help="Use Azure DefaultAzureCredential for authentication (legacy, use --auth-method instead)"
    )
    
    # Entra ID Authentication options
    auth_group = parser.add_argument_group('Entra ID Authentication')
    auth_group.add_argument(
        "--auth-method",
        choices=["default", "client_secret", "interactive", "cli", "managed_identity"],
        default=None,
        help="Entra ID auth method: 'default' (DefaultAzureCredential), 'client_secret' (service principal), "
             "'interactive' (browser), 'cli' (Azure CLI), 'managed_identity'"
    )
    auth_group.add_argument(
        "--tenant-id",
        default=None,
        help="Azure AD tenant ID (or set AZURE_TENANT_ID env var)"
    )
    auth_group.add_argument(
        "--client-id",
        default=None,
        help="Azure AD application/client ID (or set AZURE_CLIENT_ID env var)"
    )
    auth_group.add_argument(
        "--client-secret",
        default=None,
        help="Azure AD client secret (or set AZURE_CLIENT_SECRET env var)"
    )
    
    # Mode selection
    mode_group = parser.add_argument_group('Mode')
    mode_group.add_argument(
        "--mode",
        choices=["batch", "continuous"],
        default=None,
        help="Sending mode: 'batch' for historical data, 'continuous' for real-time stream (default: batch)"
    )
    
    # Batch mode options
    batch_group = parser.add_argument_group('Batch Mode Options')
    batch_group.add_argument(
        "--start",
        default=None,
        help="Start datetime in ISO format (default: 1 hour ago)"
    )
    batch_group.add_argument(
        "--end",
        default=None,
        help="End datetime in ISO format (default: now)"
    )
    batch_group.add_argument(
        "--duration-hours",
        type=int,
        default=None,
        help="Duration in hours if start/end not specified (default: 1)"
    )
    batch_group.add_argument(
        "--total-events",
        type=int,
        default=None,
        help="Total number of events to send (default: auto-calculate)"
    )
    batch_group.add_argument(
        "--events-per-batch",
        type=int,
        default=None,
        help="Number of events per batch (default: 100)"
    )
    batch_group.add_argument(
        "--delay-between-batches",
        type=float,
        default=None,
        help="Delay in seconds between batches (default: 0)"
    )
    
    # Continuous mode options
    cont_group = parser.add_argument_group('Continuous Mode Options')
    cont_group.add_argument(
        "--events-per-second",
        type=float,
        default=None,
        help="Target events per second in continuous mode (default: 10)"
    )
    cont_group.add_argument(
        "--duration-seconds",
        type=int,
        default=None,
        help="Duration in seconds for continuous mode (default: indefinite)"
    )
    
    args = parser.parse_args()
    
    # Build merged configuration
    config = get_config(args)
    
    # Validate connection parameters
    if not config["connection_string"] and not (config["namespace"] and (config["use_managed_identity"] or config["auth_method"])):
        parser.error("Either --connection-string or (--namespace + --auth-method/--use-managed-identity) is required")
    
    # Print configuration summary
    print("Configuration:")
    if args.config:
        print(f"  Config file: {args.config}")
    print(f"  Mode: {config['mode']}")
    print(f"  Event Hub: {config['eventhub_name'] or '(from connection string)'}")
    if config['auth_method']:
        print(f"  Auth: Entra ID ({config['auth_method']}) - {config['namespace']}")
    elif config['use_managed_identity']:
        print(f"  Auth: Managed Identity ({config['namespace']})")
    else:
        print("  Auth: Connection String")
    print("-" * 60)
    
    # Create producer client
    print("Connecting to Event Hub...")
    producer = create_producer_client(
        connection_string=config["connection_string"],
        eventhub_name=config["eventhub_name"],
        fully_qualified_namespace=config["namespace"],
        use_managed_identity=config["use_managed_identity"],
        auth_method=config["auth_method"],
        tenant_id=config["tenant_id"],
        client_id=config["client_id"],
        client_secret=config["client_secret"]
    )
    
    try:
        if config["mode"] == "batch":
            # Parse or default timestamps
            if config["end"]:
                end_time = datetime.fromisoformat(config["end"].replace('Z', '+00:00').replace('+00:00', ''))
            else:
                end_time = datetime.now()
            
            if config["start"]:
                start_time = datetime.fromisoformat(config["start"].replace('Z', '+00:00').replace('+00:00', ''))
            else:
                start_time = end_time - timedelta(hours=config["duration_hours"])
            
            send_events_to_eventhub(
                producer=producer,
                start_time=start_time,
                end_time=end_time,
                events_per_batch=config["events_per_batch"],
                total_events=config["total_events"],
                delay_between_batches=config["delay_between_batches"]
            )
        else:  # continuous mode
            send_continuous_stream(
                producer=producer,
                events_per_second=config["events_per_second"],
                duration_seconds=config["duration_seconds"],
                events_per_batch=min(config["events_per_batch"], 10)  # Smaller batches for real-time
            )
    finally:
        producer.close()


if __name__ == "__main__":
    main()

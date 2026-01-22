#!/usr/bin/env python3
"""
Generate partitioned JSONL files based on the example_json.json template.
Files are partitioned by timestamp: year=YYYY/month=MM/day=DD/hour=HH/minute=mm/UUID.json.gz
"""

import json
import gzip
import uuid
import random
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Template data from example_json.json

TEMPLATE = {
    "category": {},
    "container": "fabrikam-orders",
    "containerId": "containerd://a9f1c3b2d7e84c0aa4b2f9f8b1a4d3e29f0c1b2a3c4d5e6f708192a3b4c5d6e7",
    "containerImage": "crfabrikamprod.azurecr.io/ordersvc:5.1.7421",
    "containerImageId": "crfabrikamprod.azurecr.io/ordersvc@sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "file": "/var/log/pods/prod-fabrikam_fabrikam-orders-api-7d8c9fbbcc-9k2lm_b1a2c3d4-e5f6-47a8-b9c0-1d2e3f4a5b6c/fabrikam-orders/0.log",
    "host": "aks-apps-92c1d2ab-vmss0001ab",
    "namespace": "prod-fabrikam",
    "pod": "fabrikam-orders-api-7d8c9fbbcc-9k2lm",
    "podIp": "10.7.24.36",
    "podOwner": "ReplicaSet/fabrikam-orders-api-7d8c9fbbcc",
    "resource": "aks-fabrikam-eus",
    "resourceGroup": "rg-fabrikam-prod-eus",
    "severity": "info",
    "source": "kubernetes",
    "subscription": "9f1c3b2d-7e84-4c0a-a4b2-f9f8b1a4d3e2",
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

NAMESPACES = ["int", "prd", "dev", "stg"]

PODS = [
    
    "fabrikam-orders-api-7d8c9fbbcc-9k2lm",
    "fabrikam-orders-api-7d8c9fbbcc-abc12",
    "fabrikam-orders-worker-7f8d9c-xyz99",
    "fabrikam-orders-scheduler-3e4f5g-def45"
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


def generate_partitioned_files(
    output_dir: str,
    start_time: datetime,
    end_time: datetime,
    records_per_file: int = 10,
    files_per_minute: int = 1
):
    """
    Generate partitioned JSONL.gz files between start_time and end_time.
    
    Args:
        output_dir: Base output directory
        start_time: Start datetime for data generation
        end_time: End datetime for data generation
        records_per_file: Number of JSON records per file
        files_per_minute: Number of files to generate per minute
    """
    output_path = Path(output_dir)
    current_time = start_time
    total_files = 0
    total_records = 0
    
    print(f"Generating partitioned files from {start_time} to {end_time}")
    print(f"Output directory: {output_path.absolute()}")
    print(f"Records per file: {records_per_file}")
    print(f"Files per minute: {files_per_minute}")
    print("-" * 60)
    
    while current_time < end_time:
        # Create partition path
        partition_path = output_path / (
            f"year={current_time.year}/"
            f"month={current_time.month:02d}/"
            f"day={current_time.day:02d}/"
            f"hour={current_time.hour:02d}/"
            f"minute={current_time.minute:02d}"
        )
        partition_path.mkdir(parents=True, exist_ok=True)
        
        # Generate files for this minute
        for _ in range(files_per_minute):
            file_id = uuid.uuid4()
            file_path = partition_path / f"{file_id}.json.gz"
            
            # Generate records for this file
            records = []
            for i in range(records_per_file):
                # Add some variation to timestamp within the minute
                record_time = current_time + timedelta(seconds=random.uniform(0, 59))
                records.append(generate_log_record(record_time))
            
            # Write JSONL.gz file
            with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                for record in records:
                    f.write(json.dumps(record, separators=(',', ':')) + '\n')
            
            total_files += 1
            total_records += records_per_file
        
        # Move to next minute
        current_time += timedelta(minutes=1)
        
        # Progress indicator
        if total_files % 100 == 0:
            print(f"Generated {total_files} files, {total_records} records...")
    
    print("-" * 60)
    print(f"Complete! Generated {total_files} files with {total_records} total records.")
    return total_files, total_records


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate partitioned JSONL.gz log files for testing"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="./output",
        help="Output directory for partitioned files (default: ./output)"
    )
    parser.add_argument(
        "--start",
        default=None,
        help="Start datetime in ISO format (default: 1 hour ago)"
    )
    parser.add_argument(
        "--end",
        default=None,
        help="End datetime in ISO format (default: now)"
    )
    parser.add_argument(
        "--duration-hours",
        type=int,
        default=1,
        help="Duration in hours if start/end not specified (default: 1)"
    )
    parser.add_argument(
        "--records-per-file",
        type=int,
        default=10,
        help="Number of JSON records per file (default: 10)"
    )
    parser.add_argument(
        "--files-per-minute",
        type=int,
        default=2,
        help="Number of files to generate per minute (default: 2)"
    )
    
    args = parser.parse_args()
    
    # Parse or default timestamps
    if args.end:
        end_time = datetime.fromisoformat(args.end.replace('Z', '+00:00').replace('+00:00', ''))
    else:
        end_time = datetime.now()
    
    if args.start:
        start_time = datetime.fromisoformat(args.start.replace('Z', '+00:00').replace('+00:00', ''))
    else:
        start_time = end_time - timedelta(hours=args.duration_hours)
    
    generate_partitioned_files(
        output_dir=args.output_dir,
        start_time=start_time,
        end_time=end_time,
        records_per_file=args.records_per_file,
        files_per_minute=args.files_per_minute
    )


if __name__ == "__main__":
    main()

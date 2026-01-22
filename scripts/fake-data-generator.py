import argparse
import json
import os
import random
import uuid
from datetime import datetime, timedelta

import yaml

# Default configuration values
DEFAULTS = {
    "days": 3,
    "entries": 100,
    "start_date": "2026-01-01",
    "output_dir": "."
}

# Define optional fields (beyond the base schema) 
OPTIONAL_FIELDS = ['userId', 'errorCode', 'requestId', 'sessionId', 'region']

# Sample values for certain fields
LEVELS = ['INFO', 'DEBUG', 'WARN', 'ERROR']
SERVICES = ['auth', 'billing', 'data-engine', 'frontend', 'integration']
REGIONS = ['EU', 'US', 'APAC', 'CH']


def load_config(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config if config else {}


def generate_field_value(field_name: str) -> str | None:
    """Generate a random value for a given optional field."""
    if field_name == 'userId':
        return f"user_{random.randint(1000, 9999)}"
    elif field_name == 'errorCode':
        return f"ERR{random.randint(1, 5):03d}"      # e.g., ERR001 to ERR005
    elif field_name == 'requestId':
        return str(uuid.uuid4())                    # UUID for request ID
    elif field_name == 'sessionId':
        return uuid.uuid4().hex[:16]                # shorter unique session ID
    elif field_name == 'region':
        return random.choice(REGIONS)
    else:
        return None


def generate_logs(num_days: int, entries_per_day: int, base_date: datetime, output_dir: str) -> None:
    """Generate fake log files for the specified number of days."""
    os.makedirs(output_dir, exist_ok=True)
    
    for day_offset in range(num_days):
        day_date = base_date + timedelta(days=day_offset)
        file_name = os.path.join(output_dir, f"sample_logs_{day_date.strftime('%Y%m%d')}.jsonl")
        
        # Create sorted timestamps for entries within the day
        timestamps = []
        for _ in range(entries_per_day):
            sec_offset = random.randint(0, 24*3600 - 1)  # random second of the day
            ts = day_date + timedelta(seconds=sec_offset)
            timestamps.append(ts)
        timestamps.sort()
        
        # Write JSON Lines for the day
        with open(file_name, 'w') as f:
            for ts in timestamps:
                log_entry = {
                    "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                    "level": random.choice(LEVELS),
                    "message": "Sample log message",
                    "service": random.choice(SERVICES)
                }
                # Add a random subset of optional fields
                num_opts = random.randint(0, len(OPTIONAL_FIELDS))
                for field in random.sample(OPTIONAL_FIELDS, num_opts):
                    log_entry[field] = generate_field_value(field)
                # Write the log entry as a JSON object per line
                f.write(json.dumps(log_entry) + "\n")
        print(f"Wrote {entries_per_day} log entries to {file_name}")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate fake log data in JSON Lines format."
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=None,
        help="Path to YAML configuration file (overrides defaults, CLI args override config)"
    )
    parser.add_argument(
        "-d", "--days",
        type=int,
        default=None,
        help=f"Number of days to simulate (default: {DEFAULTS['days']})"
    )
    parser.add_argument(
        "-e", "--entries",
        type=int,
        default=None,
        help=f"Number of log entries per day (default: {DEFAULTS['entries']})"
    )
    parser.add_argument(
        "-s", "--start-date",
        type=str,
        default=None,
        help=f"Start date in YYYY-MM-DD format (default: {DEFAULTS['start_date']})"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=None,
        help=f"Output directory for generated log files (default: {DEFAULTS['output_dir']})"
    )
    return parser.parse_args()


def get_config(args: argparse.Namespace) -> dict:
    """
    Build final configuration by merging (in order of priority):
    1. Default values (lowest priority)
    2. Config file values
    3. CLI arguments (highest priority)
    """
    config = DEFAULTS.copy()
    
    # Load config file if provided
    if args.config:
        file_config = load_config(args.config)
        # Map YAML keys to config keys (support both formats)
        key_mapping = {
            "days": "days",
            "entries": "entries", 
            "entries_per_day": "entries",
            "start_date": "start_date",
            "startDate": "start_date",
            "output_dir": "output_dir",
            "outputDir": "output_dir",
        }
        for yaml_key, config_key in key_mapping.items():
            if yaml_key in file_config:
                config[config_key] = file_config[yaml_key]
    
    # Override with CLI arguments if provided
    if args.days is not None:
        config["days"] = args.days
    if args.entries is not None:
        config["entries"] = args.entries
    if args.start_date is not None:
        config["start_date"] = args.start_date
    if args.output_dir is not None:
        config["output_dir"] = args.output_dir
    
    return config


def main() -> None:
    """Main entry point for the fake data generator."""
    args = parse_args()
    config = get_config(args)
    
    # Parse the start date
    try:
        base_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format '{config['start_date']}'. Use YYYY-MM-DD format.")
        return
    
    print(f"Generating {config['days']} days of logs with {config['entries']} entries per day...")
    print(f"Start date: {base_date.strftime('%Y-%m-%d')}")
    print(f"Output directory: {os.path.abspath(config['output_dir'])}")
    if args.config:
        print(f"Config file: {args.config}")
    print("-" * 50)
    
    generate_logs(
        num_days=config["days"],
        entries_per_day=config["entries"],
        base_date=base_date,
        output_dir=config["output_dir"]
    )
    
    print("-" * 50)
    print("Done!")


if __name__ == "__main__":
    main()

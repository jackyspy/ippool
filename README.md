[English](README.md) | [中文](https://github.com/jackyspy/ippool/blob/main/README_zh.md)

# ipools

Efficient IP address pool management and operations for IPv4/IPv6 networks.

[![PyPI version](https://badge.fury.io/py/ipools.svg)](https://pypi.org/project/ipools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- Fast add/remove/merge of IP ranges and networks
- Support for both IPv4 and IPv6
- Flexible input: CIDR, range string, tuple, object, etc.
- Efficient intersection, subtraction, and membership operations
- Output as summarized networks or raw ranges
- Pythonic API, well-tested, and production-ready
- Command-line tool for batch operations

## Installation

```bash
pip install ipools
```

## Quick Start (Python API)

```python
from ippool import IPv4Pool, IPv6Pool

# Create a pool from CIDR and range strings
pool = IPv4Pool(["192.168.1.0/24", "10.0.0.1-10.0.0.10"])

# Add more networks
pool.add("172.16.0.0/16")

# Remove a subnet
pool.remove("192.168.1.128/25")

# Check if an IP is in the pool
print("192.168.1.5" in pool)  # True
print("192.168.2.1" in pool)  # False

# Get summarized networks
print(pool.networks)  # (IPv4Network('10.0.0.1/32'), ..., IPv4Network('172.16.0.0/16'))

# Intersection
other = IPv4Pool("10.0.0.0/8")
print(pool & other)

# Set operations examples
pool1 = IPv4Pool("192.168.1.0/24")
pool2 = IPv4Pool("192.168.1.128/25")
pool3 = IPv4Pool("192.168.2.0/24")

# Union
union = pool1 + pool2 + pool3
print(f"Union contains {union.num_addresses} IP addresses")

# Subtraction
diff = pool1 - pool2
print(f"Difference contains {diff.num_addresses} IP addresses")

# Intersection
intersection = pool1 & pool2
print(f"Intersection contains {intersection.num_addresses} IP addresses")

# IPv6 support
ipv6_pool = IPv6Pool(["2001:db8::/48", "2001:db8:1::/48"])
print(f"IPv6 pool contains {ipv6_pool.num_addresses} addresses")

# Complex operations example
# Exclude multiple small networks from a large network
large_network = IPv4Pool("10.0.0.0/8")
excluded_networks = [
    "10.0.1.0/24",
    "10.0.2.0/24", 
    "10.1.0.0/16"
]
result = large_network - excluded_networks
print(f"Remaining IP addresses after exclusion: {result.num_addresses}")

# Check if IP ranges overlap
range1 = IPv4Pool("192.168.1.0/24")
range2 = IPv4Pool("192.168.1.128/25")
if range1 & range2:
    print("IP ranges overlap")

# Get pool statistics
print(f"Pool contains {len(pool.networks)} networks")
print(f"Pool contains {len(pool.ip_ranges)} IP ranges")
print(f"Total IP count: {pool.num_addresses}")

# Create from string in batch
networks_str = """
192.168.1.0/24
10.0.0.0/8
172.16.0.0/16
"""
pool_from_str = IPv4Pool(networks_str)
print(f"Created pool with {pool_from_str.num_addresses} IPs from string")

# Copy and modify
pool_copy = pool.copy()
pool_copy.add("192.168.3.0/24")
print(f"Original pool: {pool.num_addresses} IPs, Copy: {pool_copy.num_addresses} IPs")
```

## Command Line Usage

Install via pip, then use the `ippool` command:

### Basic Operations

```bash
# Default merge operation (no command needed)
ippool "192.168.1.0/24,10.0.0.0/8"
ippool "192.168.1.0/24;192.168.2.0/24"
ippool "192.168.1.0/24 192.168.2.0/24"

# Subtract one pool from another (note: global options must come before subcommands)
ippool --format cidr diff "192.168.0.0/16" "192.168.1.0/24"
# Subtract multiple small networks from a large network
ippool --format cidr diff 192.168.0.0/16 "192.168.1.0/24;192.168.2.0-192.168.100.255,192.168.254.0-255"
# Load address pools from files
ippool --ipv6 diff @ippool1.txt @ippool2.txt

# Intersection of multiple pools
ippool --format json intersect "192.168.1.0/24" "192.168.1.128/25" "192.168.1.192/26"
```

### Input Formats

```bash
# Direct input with separators (comma, semicolon, space)
ippool "192.168.1.0/24,10.0.0.0/8,172.16.0.0/16"

# Read from file
ippool @ranges.txt
ippool @"path with spaces/ranges.txt"

# Read from stdin
cat ranges.txt | ippool -
echo "192.168.1.0/24,10.0.0.0/8" | ippool -

# Mix different input sources
ippool @vpc1.txt "192.168.1.0/24" @vpc2.txt
```

### Output Formats

```bash
# Range format (default)
ippool "192.168.1.0/24;192.168.2.0/24"
# Output: 192.168.1.0-192.168.2.255

# CIDR format
ippool --format=cidr 192.168.1.0/24,192.168.2.0/24
# Output: 192.168.1.0/24
#         192.168.2.0/24

# Statistics
ippool --format=stat "192.168.1.0/24"
# Output: Networks: 1
#         Total IPs: 256
#         Largest: 192.168.1.0/24 (256 IPs)
#         Smallest: 192.168.1.0/24 (256 IPs)

# JSON format
ippool --format=json "192.168.1.0/24"
# Output: {
#   "ranges": ["192.168.1.0-192.168.1.255"],
#   "cidr": ["192.168.1.0/24"],
#   "total_ips": 256
# }
```

### Advanced Usage

```bash
# IPv6 support
ippool --ipv6 "2001:db8::/48" "2001:db8:1::/48"

# Output to file
ippool --format=json --output=result.json "192.168.1.0/24"

# Complex operations
ippool --format=stat "192.168.1.0/24,10.0.0.0/8,172.16.0.0/16"

# Batch processing multiple files
ippool --format=cidr -o merged.txt @file1.txt @file2.txt @file3.txt

# Process from standard input
echo "192.168.1.0/24\n10.0.0.0/8" | ippool --format=json -
```

### overlap: Find all overlapping IP ranges and their sources

Finds all overlapping IP ranges from input (supports IPv4/IPv6, file/stdin, any format).

**Usage:**

```
ippool overlap [--ipv6] [--format plain|json] <inputs...>
```

- `--format`: Output format. `plain` (default) prints readable text, `json` prints machine-readable JSON.

**Example:**

```
ippool overlap 192.168.0.0/24 192.168.0.128/25 10.0.0.0/8
```

**Plain output:**
```
[192.168.0.128/25]:
    192.168.0.0/24
    192.168.0.128/25
```

**JSON output:**
```
ippool overlap --format json 192.168.0.0/24 192.168.0.128/25 10.0.0.0/8
[
  {
    "overlap": "192.168.0.128-192.168.0.255",
    "sources": [
      "192.168.0.0-192.168.0.255",
      "192.168.0.128-192.168.0.255"
    ]
  }
]
```


## CLI Help

```bash
ippool --help
ippool diff --help
ippool intersect --help
```

## Python API Detailed Examples

### Network Management Scenarios

```python
from ippool import IPv4Pool

# Scenario 1: Managing company network allocation
company_networks = IPv4Pool([
    "10.0.0.0/8",      # Headquarters network
    "172.16.0.0/12",   # Branch offices
    "192.168.0.0/16"   # Office network
])

# Department network allocation
dept_allocations = {
    "IT Department": IPv4Pool("10.0.1.0/24"),
    "Finance": IPv4Pool("10.0.2.0/24"),
    "HR": IPv4Pool("10.0.3.0/24")
}

# Check for conflicts
for dept, network in dept_allocations.items():
    if company_networks & network:
        print(f"{dept} network allocation is valid")
    else:
        print(f"{dept} network allocation is invalid")

# Scenario 2: Security policy configuration
allowed_networks = IPv4Pool("192.168.1.0/24")
blocked_ranges = IPv4Pool([
    "192.168.1.100-192.168.1.110",  # Server maintenance window
    "192.168.1.200-192.168.1.255"   # Test environment
])

# Calculate actually allowed networks
effective_allowed = allowed_networks - blocked_ranges
print(f"Actually allowed IPs: {effective_allowed.num_addresses}")
```

### Cloud Platform Resource Management

```python
from ippool import IPv4Pool, IPv6Pool

# Scenario 3: Cloud platform VPC management
vpc_pools = {
    "vpc-1": IPv4Pool("10.1.0.0/16"),
    "vpc-2": IPv4Pool("10.2.0.0/16"),
    "vpc-3": IPv4Pool("10.3.0.0/16")
}

# Check for IP conflicts between VPCs
def check_vpc_conflicts(vpc_pools):
    vpc_list = list(vpc_pools.values())
    for i, pool1 in enumerate(vpc_list):
        for j, pool2 in enumerate(vpc_list[i+1:], i+1):
            if pool1 & pool2:
                print(f"VPC {i+1} and VPC {j+1} have IP conflicts")
                return True
    return False

# Scenario 4: Container network planning
kubernetes_pods = IPv4Pool("10.244.0.0/16")
kubernetes_services = IPv4Pool("10.96.0.0/12")

# Ensure Pod and Service networks don't overlap
if kubernetes_pods & kubernetes_services:
    print("Warning: Pod and Service networks overlap")
else:
    print("Pod and Service network configuration is correct")
```

### Data Analysis and Statistics

```python
from ippool import IPv4Pool

# Scenario 5: Network traffic analysis
def analyze_network_coverage(access_logs, network_pools):
    """
    Analyze IP address coverage in access logs
    """
    # Assume access_logs is a list containing IP addresses
    accessed_ips = IPv4Pool(access_logs)
    
    results = {}
    for name, pool in network_pools.items():
        overlap = accessed_ips & pool
        coverage_rate = overlap.num_addresses / pool.num_addresses
        results[name] = {
            "total_ips": pool.num_addresses,
            "accessed_ips": overlap.num_addresses,
            "coverage_rate": coverage_rate
        }
    
    return results

# Scenario 6: Network utilization statistics
def calculate_network_utilization(allocated_pools, total_network):
    """
    Calculate network utilization
    """
    total_allocated = IPv4Pool()
    for pool in allocated_pools:
        total_allocated += pool
    
    utilization = total_allocated & total_network
    utilization_rate = utilization.num_addresses / total_network.num_addresses
    
    return {
        "total_ips": total_network.num_addresses,
        "allocated_ips": utilization.num_addresses,
        "utilization_rate": utilization_rate,
        "available_ips": total_network.num_addresses - utilization.num_addresses
    }
```

### Automation Script Examples

```python
from ippool import IPv4Pool
import json

# Scenario 7: Batch network configuration generation
def generate_network_configs(base_network, subnet_count, subnet_size):
    """
    Generate multiple subnet configurations from base network
    """
    base_pool = IPv4Pool(base_network)
    configs = []
    
    # Simplified processing, actual implementation needs more complex subnet division logic
    for i in range(subnet_count):
        # Example: Create subnet configuration
        config = {
            "name": f"subnet-{i+1}",
            "network": f"10.0.{i}.0/24",
            "gateway": f"10.0.{i}.1",
            "dhcp_range": f"10.0.{i}.10-10.0.{i}.254"
        }
        configs.append(config)
    
    return configs

# Scenario 8: Configuration file validation
def validate_network_config(config_file):
    """
    Validate IP address settings in network configuration file
    """
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    networks = IPv4Pool()
    errors = []
    
    for item in config.get('networks', []):
        try:
            network = IPv4Pool(item['cidr'])
            # Check for overlaps
            if networks & network:
                errors.append(f"Network {item['name']} overlaps with other networks")
            networks += network
        except Exception as e:
            errors.append(f"Network {item['name']} configuration error: {e}")
    
    return errors

# Usage example
if __name__ == "__main__":
    # Validate configuration file
    errors = validate_network_config('network_config.json')
    if errors:
        print("Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration validation passed")
```

## License

MIT License. See [LICENSE](LICENSE).

## Links

- [PyPI](https://pypi.org/project/ipools/)
- [GitHub](https://github.com/jackyspy/ippool)

## Authors

- [jackyspy](https://github.com/jackyspy)
- [Theunsafe](https://github.com/Theunsafe)
- [tutu](https://github.com/tutu) 
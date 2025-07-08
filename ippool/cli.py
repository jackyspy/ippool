import argparse
import sys
import re
import json
from ippool.ippool import IPv4Pool, IPv6Pool
from ippool.utils import find_overlapping_ranges


def _print_help():
    """Print help message"""
    print("Usage: ippool [options] <inputs...>")
    print("       ippool [options] diff <pool1> <pool2>")
    print("       ippool [options] intersect <pools...>")
    print("       ippool [options] overlap <inputs...>")
    print("\nGlobal Options:")
    print("  --ipv6                    Use IPv6 mode (default: IPv4)")
    print("  --format {range,cidr,stat,json}  Output format (default: range)")
    print("  -o, --output FILE         Output to file")
    print("\nInput formats:")
    print("  <ip/cidr>                 Direct IP or CIDR")
    print("  @<file>                   Read from file")
    print("  -                         Read from stdin")
    print("\nExamples:")
    print("  ippool 192.168.1.0/24 192.168.2.0/24")
    print("  ippool --format json --output result.json 192.168.1.0/24")
    print("  ippool --format cidr diff 192.168.0.0/16 192.168.1.0/24")
    print("  ippool --ipv6 intersect 2001:db8::/48 2001:db8:1::/48")
    print("  ippool overlap 192.168.1.0/24 192.168.1.128/25")
    print("  ippool overlap --ipv6 2001:db8::/48 2001:db8:0:8000::/49")


def parse_input_string(input_str):
    """
    Parse input string with comma and semicolon separators
    """
    # Split by comma or semicolon
    parts = re.split(r'[,;]+', input_str.strip())
    return [part.strip() for part in parts if part.strip()]


def parse_file_content(file_obj):
    """Parse file content where each line is a separate entry"""
    return [line.strip() for line in file_obj if line.strip()]


def parse_inputs(inputs, ipv6=False):
    """
    Parse inputs from command line arguments, files, or stdin
    """
    all_networks = []
    stdin_used = False

    for input_item in inputs:
        if input_item == '-':
            if stdin_used:
                print("Error: stdin can only be used once", file=sys.stderr)
                sys.exit(1)

            stdin_used = True
            # Read from stdin
            networks = parse_file_content(sys.stdin)
            all_networks.extend(networks)
        elif input_item.startswith('@'):
            # Read from file
            file_path = input_item[1:]
            # Handle quoted paths
            if file_path.startswith('"') and file_path.endswith('"'):
                file_path = file_path[1:-1]
            elif file_path.startswith("'") and file_path.endswith("'"):
                file_path = file_path[1:-1]

            try:
                with open(file_path, 'r') as f:
                    networks = parse_file_content(f)
                    all_networks.extend(networks)
            except FileNotFoundError:
                print(f"Error: File not found: {file_path}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error reading file {file_path}: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # Direct input
            networks = parse_input_string(input_item)
            all_networks.extend(networks)

    return all_networks


def format_stat(pool):
    """Format pool statistics"""
    total_ips = pool.num_addresses
    ranges_count = len(pool.ip_ranges)

    if ranges_count == 0:
        return "Networks: 0\nTotal IPs: 0\nRanges: 0"

    networks = list(pool.networks)

    # Find largest and smallest networks
    largest = max(networks, key=lambda n: n.num_addresses)
    smallest = min(networks, key=lambda n: n.num_addresses)

    return (f"Total IPs: {total_ips}\n"
            f"Ranges: {ranges_count}\n"
            f"Networks: {len(networks)}\n"
            f"Largest: {largest} ({largest.num_addresses} IPs)\n"
            f"Smallest: {smallest} ({smallest.num_addresses} IPs)")


def format_json(pool):
    """Format pool as JSON with ranges, cidr, and total_ips"""
    return {
        "ranges": [f"{start}-{end}" for start, end in pool.ip_ranges],
        "cidr": [str(network) for network in pool.networks],
        "total_ips": pool.num_addresses
    }


def output_result(pool, output_format, output_file=None):
    """Output result in specified format"""
    format_functions = {
        "json":
        lambda p: json.dumps(format_json(p), indent=2),
        "cidr":
        lambda p: "\n".join(str(network) for network in p.networks),
        "stat":
        format_stat,
        "range":
        lambda p: "\n".join(f"{start}-{end}" for start, end in p.ip_ranges)
    }

    output = format_functions.get(output_format,
                                  format_functions["range"])(pool)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(output)
    else:
        print(output)


def _create_parser():
    """Create argument parser for subcommands"""
    parser = argparse.ArgumentParser(
        description=
        "Efficient IP address pool management and operations (IPv4/IPv6).")

    # Global options that apply to all commands
    parser.add_argument("--ipv6",
                        action="store_true",
                        help="Use IPv6 mode (default: IPv4)")

    parser.add_argument("--format",
                        choices=["range", "cidr", "stat", "json"],
                        default="range",
                        help="Output format (default: range)")

    parser.add_argument("-o", "--output", help="Output file")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command")

    # diff command
    diff_p = subparsers.add_parser("diff",
                                   help="Subtract one pool from another")
    diff_p.add_argument("pool1",
                        help="First pool (IP ranges/networks, @file, or -)")
    diff_p.add_argument("pool2",
                        help="Second pool (IP ranges/networks, @file, or -)")

    # intersect command
    inter_p = subparsers.add_parser("intersect",
                                    help="Intersection of multiple pools")
    inter_p.add_argument("pools",
                         nargs="+",
                         help="Pools (IP ranges/networks, @file, or -)")

    # overlap command
    overlap_p = subparsers.add_parser(
        "overlap", help="Find all overlapping IP ranges and their sources")
    overlap_p.add_argument("inputs",
                           nargs="+",
                           help="IP ranges/networks, @file, or -")
    overlap_p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        help="Output format for overlap (plain or json, default: plain)")

    return parser


def _handle_diff_command(args, PoolClass):
    """Handle diff subcommand"""
    pool1_networks = parse_inputs([args.pool1], args.ipv6)
    pool2_networks = parse_inputs([args.pool2], args.ipv6)

    if not pool1_networks:
        print("Error: First pool is empty", file=sys.stderr)
        sys.exit(1)

    return PoolClass(pool1_networks) - PoolClass(pool2_networks)


def _handle_intersect_command(args, PoolClass):
    """Handle intersect subcommand"""
    all_networks = []
    for pool_arg in args.pools:
        networks = parse_inputs([pool_arg], args.ipv6)
        all_networks.append(networks)

    if not all_networks[0]:
        print("Error: First pool is empty", file=sys.stderr)
        sys.exit(1)

    result = PoolClass(all_networks[0])
    for networks in all_networks[1:]:
        if networks:
            result &= PoolClass(networks)
        else:
            return PoolClass([])

    return result


def _handle_overlap_command(args):
    ipv6 = args.ipv6
    all_networks = parse_inputs(args.inputs, ipv6)
    if not all_networks:
        print("Error: No input provided", file=sys.stderr)
        sys.exit(1)

    overlaps = find_overlapping_ranges(all_networks, ipv6=ipv6)
    if args.format == "json":
        out = [{
            "overlap": str(overlap),
            "sources": [str(s) for s in sources]
        } for overlap, sources in overlaps]
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for overlap, sources in overlaps:
            print(f"[{overlap}]:")
            for s in sources:
                print(f"    {s}")


def _parse_manual_args():
    """Parse arguments manually for default merge operation"""
    args = {
        "ipv6": False,
        "format_type": "range",
        "output_file": None,
        "inputs": []
    }

    argv = sys.argv
    argc = len(argv)

    def _get_next_arg():
        """Get next argument value"""
        nonlocal i
        if i + 1 < argc:
            i += 1
            return argv[i]

        print(f"Error: {arg} requires a value", file=sys.stderr)
        sys.exit(1)

    i = 1
    while i < argc:
        arg = argv[i]

        if arg == "--ipv6":
            args["ipv6"] = True
        elif arg == "--format":
            args["format_type"] = _get_next_arg()
        elif arg.startswith("--format="):
            args["format_type"] = arg.split("=", 1)[1]
        elif arg in ["-o", "--output"]:
            args["output_file"] = _get_next_arg()
        elif arg.startswith("-o=") or arg.startswith("--output="):
            args["output_file"] = arg.split("=", 1)[1]
        else:
            args["inputs"].append(arg)

        i += 1

    return args


def main():
    # Check if help is requested
    argv = sys.argv
    if "--help" in argv[1:] or "-h" in argv[1:]:
        _print_help()
        sys.exit(0)

    # Check if any argument is a subcommand
    has_subcommand = any(arg in ["diff", "intersect", "overlap"]
                         for arg in argv[1:])

    if has_subcommand:
        # Use subcommand parsing
        parser = _create_parser()
        args = parser.parse_args()

        # Determine pool class based on ipv6 flag
        PoolClass = IPv6Pool if args.ipv6 else IPv4Pool

        # Handle subcommands
        if args.command == "diff":
            result = _handle_diff_command(args, PoolClass)
        elif args.command == "intersect":
            result = _handle_intersect_command(args, PoolClass)
        elif args.command == "overlap":
            _handle_overlap_command(args)
            return

        # Output result
        output_result(result, args.format, args.output)

    else:
        # Default merge operation
        args = _parse_manual_args()

        if not args["inputs"]:
            print("Error: No input provided", file=sys.stderr)
            sys.exit(1)

        networks = parse_inputs(args["inputs"], args["ipv6"])
        if not networks:
            print("Error: No valid networks found", file=sys.stderr)
            sys.exit(1)

        # Determine pool class based on ipv6 flag
        PoolClass = IPv6Pool if args["ipv6"] else IPv4Pool
        result = PoolClass(networks)
        output_result(result, args["format_type"], args["output_file"])


if __name__ == "__main__":
    main()

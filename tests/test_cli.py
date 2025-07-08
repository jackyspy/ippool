import subprocess
import sys
import os
import tempfile
import pytest
import json
from ipaddress import IPv4Address

CLI = [sys.executable, "-m", "ippool"]


def run_cli(args, input_text=None):
    result = subprocess.run(
        CLI + args,
        input=input_text,
        capture_output=True,
        text=True,
    )
    return result


def test_not_enough_arguments():
    """Test insufficient arguments"""
    result = run_cli([])
    assert result.returncode == 1
    assert "Error: No input provided" in result.stderr


def test_default_merge():
    """Test default merge operation (no command specified)"""
    result = run_cli(["192.168.1.0/24", "192.168.2.0/25"])
    assert result.returncode == 0
    # Should output merged ranges
    assert "192.168.1.0-192.168.2.127" in result.stdout


def test_merge_with_separators():
    """Test merge with different separators"""
    # Test with JSON format
    result = run_cli(
        ["--format=json", "192.168.1.0/24,10.0.0.0/8;172.16.0.0/16"])
    assert result.returncode == 0
    json_output = json.loads(result.stdout)
    assert "ranges" in json_output
    assert "cidr" in json_output
    assert "total_ips" in json_output
    assert len(json_output["ranges"]) > 0
    assert len(json_output["cidr"]) > 0
    assert json_output["total_ips"] > 0


def test_diff_basic():
    """Test diff operation"""
    result = run_cli(["diff", "192.168.1.0/24", "192.168.1.0/25"])
    assert result.returncode == 0
    assert "192.168.1.128-192.168.1.255" in result.stdout


def test_output_to_file():
    """Test -o output to file"""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        output_file = f.name

    try:
        result = run_cli(["192.168.1.0/24", "-o", output_file])
        assert result.returncode == 0
        assert result.stdout == ""

        # Check file content
        with open(output_file, 'r') as f:
            content = f.read()
            assert "192.168.1.0-192.168.1.255" in content
    finally:
        os.unlink(output_file)


def test_intersect_basic():
    """Test intersect operation"""
    result = run_cli(["intersect", "192.168.1.0/24", "192.168.1.128/25"])
    assert result.returncode == 0
    assert "192.168.1.128-192.168.1.255" in result.stdout


def test_intersect_multiple():
    """Test intersect with multiple pools"""
    result = run_cli([
        "intersect", "192.168.1.0/24", "192.168.1.128/25", "192.168.1.100-200"
    ])
    assert result.returncode == 0
    assert "192.168.1.128-192.168.1.200" in result.stdout


def test_output_formats():
    """Test different output formats"""
    # Range format (default)
    result = run_cli(["192.168.1.0/24"])
    assert result.returncode == 0
    assert "192.168.1.0-192.168.1.255" in result.stdout

    # CIDR format
    result = run_cli(["--format=cidr", "192.168.1.0/24"])
    assert result.returncode == 0
    assert "192.168.1.0/24" in result.stdout

    # Stat format
    result = run_cli(["--format", "stat", "192.168.1.0/24"])
    assert result.returncode == 0
    assert "Networks: 1" in result.stdout
    assert "Total IPs: 256" in result.stdout

    # JSON format
    result = run_cli(["--format=json", "192.168.1.0/24"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "ranges" in data and data['ranges'] == ['192.168.1.0-192.168.1.255']
    assert "cidr" in data and data['cidr'] == ['192.168.1.0/24']
    assert "total_ips" in data and data["total_ips"] == 256


def test_file_input():
    """Test @file input"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                     delete=False) as f:
        f.write("192.168.1.0/25\n\n\n192.168.1.128/25\n\n  ")
        f.close()

        result = run_cli([f"@{f.name}"])
        assert result.returncode == 0
        assert "192.168.1.0-192.168.1.255" in result.stdout

        os.unlink(f.name)


def test_file_input_quoted():
    """Test @file input with quoted path"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                     delete=False) as f:
        f.write("192.168.1.0/24\n")
        f.close()

        # Test with double quotes
        result = run_cli([f'@"{f.name}"'])
        assert result.returncode == 0
        assert "192.168.1.0-192.168.1.255" in result.stdout

        os.unlink(f.name)


def test_stdin_input():
    """Test stdin input with -"""
    input_text = "192.168.1.0/24\n10.0.0.0/8"
    result = run_cli(["-"], input_text=input_text)
    assert result.returncode == 0
    assert "192.168.1.0-192.168.1.255" in result.stdout
    assert "10.0.0.0-10.255.255.255" in result.stdout


def test_multiple_input_sources():
    """Test mixing different input sources"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                     delete=False) as f:
        f.write("192.168.1.0/25\n")
        f.close()

        result = run_cli([f"@'{f.name}'", "192.168.1.128/25"])
        assert result.returncode == 0
        assert "192.168.1.0-192.168.1.255" in result.stdout

        os.unlink(f.name)


def test_output_to_file():
    """Test output to file"""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        f.close()

        result = run_cli(
            ["--format=json", f"--output={f.name}", "192.168.1.0/24"])
        assert result.returncode == 0
        assert result.stdout == ""  # No output to stdout

        # Check file content
        with open(f.name, 'r') as f_read:
            data = json.load(f_read)
            assert data["total_ips"] == 256

        os.unlink(f.name)

    result = run_cli(["192.168.1.0/24", "--output"])
    assert result.returncode == 1


def test_ipv6_support():
    """Test IPv6 support"""
    result = run_cli(["--ipv6", "2001:db8::/48", "2001:db8:1::/48"])
    assert result.returncode == 0
    assert "2001:db8::-2001:db8:1:ffff:ffff:ffff:ffff:ffff" in result.stdout


def test_error_handling():
    """Test error handling"""
    # Invalid IP format
    result = run_cli(["invalid-ip"])
    assert result.returncode != 0
    assert "Error" in result.stderr

    # File not found
    result = run_cli(["@nonexistent.txt"])
    assert result.returncode != 0
    assert "File not found" in result.stderr

    # Multiple stdin usage
    result = run_cli(["-", "-"])
    assert result.returncode != 0
    assert "stdin can only be used once" in result.stderr


def test_empty_input():
    """Test empty input handling"""
    result = run_cli([])
    assert result.returncode != 0
    assert "No input provided" in result.stderr


def test_help():
    """Test help output"""
    result = run_cli(["--help"])
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()
    assert "diff" in result.stdout.lower()
    assert "intersect" in result.stdout.lower()


def test_complex_operations():
    """Test complex operations with multiple formats"""
    # Test merge with multiple networks and different formats
    networks = "192.168.1.0/24,10.0.0.0/8,172.16.0.0/16"

    # Range format
    result = run_cli([networks])
    assert result.returncode == 0
    assert "192.168.1.0-192.168.1.255" in result.stdout
    assert "10.0.0.0-10.255.255.255" in result.stdout
    assert "172.16.0.0-172.16.255.255" in result.stdout

    # JSON format with stats
    result = run_cli([networks, "--format=json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["ranges"]) == 3
    assert data["total_ips"] == (1 << 8) + (1 << 24) + (1 << 16)


def test_diff_with_format_options():
    """Test diff command with format and output options"""
    # Test diff with different formats (options before command)
    result = run_cli(
        ["--format=cidr", "diff", "192.168.1.0/24", "192.168.1.0/25"])
    assert result.returncode == 0
    assert "192.168.1.128/25" in result.stdout

    result = run_cli(
        ["--format=stat", "diff", "192.168.1.0/24", "192.168.1.0/25"])
    assert result.returncode == 0
    assert "Networks: 1" in result.stdout
    assert "Total IPs: 128" in result.stdout

    result = run_cli(
        ["--format=json", "diff", "192.168.1.0/24", "192.168.1.0/25"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "ranges" in data
    assert "cidr" in data
    assert data["total_ips"] == 128

    # Test diff with output to file (options before command)
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        f.close()

        result = run_cli([
            "--format=json", f"--output={f.name}", "diff", "192.168.1.0/24",
            "192.168.1.0/25"
        ])
        assert result.returncode == 0
        assert result.stdout == ""  # No output to stdout

        # Check file content
        with open(f.name, 'r') as f_read:
            data = json.load(f_read)
            assert data["total_ips"] == 128
            assert "192.168.1.128-192.168.1.255" in data["ranges"][0]

        os.unlink(f.name)


def test_intersect_with_format_options():
    """Test intersect command with format and output options"""
    # Test intersect with different formats (options before command)
    result = run_cli([
        "--format=cidr", "intersect", "192.168.1.0/24", "192.168.1.128/25",
        "192.168.1.100-200"
    ])
    assert result.returncode == 0
    assert "192.168.1.128/26" in result.stdout
    assert '192.168.1.192/29' in result.stdout
    assert '192.168.1.200/32' in result.stdout

    # Test intersect with output to file (options before command)
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.close()

        result = run_cli([
            "--format=cidr", f"--output={f.name}", "intersect",
            "192.168.1.0/24", "192.168.1.128/25"
        ])
        assert result.returncode == 0
        assert result.stdout == ""  # No output to stdout

        # Check file content
        with open(f.name, 'r') as f_read:
            content = f_read.read().strip()
            assert "192.168.1.128/25" in content

        os.unlink(f.name)


def test_subcommand_with_options_before():
    """Test subcommands with options before the command"""
    # Test with --ipv6 before diff
    result = run_cli(["--ipv6", "diff", "2001:db8::/48", "2001:db8::/49"])
    assert result.returncode == 0

    # Test with --format before intersect
    result = run_cli(
        ["--format=json", "intersect", "192.168.1.0/24", "192.168.1.128/25"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "ranges" in data


def test_help_variations():
    """Test help options"""
    # Test -h
    result = run_cli(["-h"])
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()
    assert "diff" in result.stdout.lower()
    assert "intersect" in result.stdout.lower()


def test_empty_string_parameters():
    """Test empty string parameters"""
    # Empty string as direct input
    result = run_cli([""])
    assert result.returncode != 0
    assert "Error" in result.stderr

    # Empty string with separators
    result = run_cli([",,,"])
    assert result.returncode != 0
    assert "Error" in result.stderr

    # Empty string with semicolons
    result = run_cli([";;;"])
    assert result.returncode != 0
    assert "Error" in result.stderr


def test_empty_stdin():
    """Test empty stdin input"""
    # Empty stdin
    result = run_cli(["-"], input_text="")
    assert result.returncode != 0
    assert "Error" in result.stderr


def test_directory_as_file_parameter():
    """Test @ with directory parameter"""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        result = run_cli([f"@{temp_dir}"])
        assert result.returncode != 0
        assert "Error" in result.stderr


def test_diff_empty_result():
    """Test diff operation that results in empty pool"""
    # Test diff with stat format for empty result
    result = run_cli(
        ["--format=stat", "diff", "192.168.1.0/24", "192.168.1.0/24"])
    assert result.returncode == 0
    assert "Networks: 0" in result.stdout
    assert "Total IPs: 0" in result.stdout
    assert "Ranges: 0" in result.stdout


def test_diff_first_pool_empty():
    """Test diff command with empty first pool"""
    # Empty first pool
    result = run_cli(["diff", "", "192.168.1.0/24"])
    assert result.returncode != 0
    assert "First pool is empty" in result.stderr


def test_intersect_pool_empty():
    """Test intersect command with empty pool"""
    # pool empty
    result = run_cli(["intersect", "", "192.168.1.0/24"])
    assert result.returncode == 1
    assert result.stderr.strip() == "Error: First pool is empty"

    result = run_cli(["intersect", "192.168.1.0/24", ""])
    assert result.returncode == 0
    # Should return empty result
    assert result.stdout.strip() == ""


def test_empty_file_input():
    """Test empty file input"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                     delete=False) as f:
        f.write("")  # Empty file
        f.close()

        result = run_cli([f"@{f.name}"])
        assert result.returncode != 0
        assert "Error" in result.stderr

        os.unlink(f.name)


def test_whitespace_only_parameters():
    """Test parameters with only whitespace"""
    # Whitespace-only direct input
    result = run_cli(["   "])
    assert result.returncode != 0
    assert "Error" in result.stderr


def test_overlap_basic():
    result = run_cli(["overlap", "192.168.1.0/24", "192.168.1.128/25"])
    assert result.returncode == 0
    assert "[192.168.1.128-192.168.1.255]:\n" in result.stdout
    assert "192.168.1.0-192.168.1.255\n    192.168.1.128-192.168.1.255" in result.stdout


def test_overlap_multiple():
    result = run_cli([
        "overlap",
        "192.168.1.0/24",
        "192.168.1.50-150",
        "192.168.1.100-200",
        "192.168.1.75-125",
    ])
    assert result.returncode == 0
    # 检查多个重叠区间
    assert "192.168.1.100-192.168.1.125" in result.stdout or "192.168.1.75-192.168.1.100" in result.stdout


def test_overlap_mixed_formats():
    result = run_cli([
        "overlap", "192.168.1.0/24", "192.168.1.128/25", "192.168.1.100-200",
        "192.168.1.50-192.168.1.150",
        str(int(IPv4Address("192.168.1.60")))
    ])
    assert result.returncode == 0
    assert "[192.168.1.50-192.168.1.59]:" in result.stdout
    assert "[192.168.1.60]:" in result.stdout
    assert "[192.168.1.61-192.168.1.99]:" in result.stdout
    assert "[192.168.1.100-192.168.1.127]:" in result.stdout
    assert "[192.168.1.128-192.168.1.150]:" in result.stdout
    assert "[192.168.1.151-192.168.1.200]:" in result.stdout
    assert "[192.168.1.201-192.168.1.255]:" in result.stdout


def test_overlap_ipv6():
    result = run_cli([
        "--ipv6", "overlap", "2001:db8::/48", "2001:db8:0:8000::/49",
        "2001:db8::1-2001:db8::10"
    ])
    assert result.returncode == 0
    assert "[2001:db8:0:8000::-2001:db8:0:ffff:ffff:ffff:ffff:ffff]:" in result.stdout


def test_overlap_file_input():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                     delete=False) as f:
        f.write("192.168.1.0/24\n192.168.1.128/25\n")
        f.close()
        result = run_cli(["overlap", f"@{f.name}"])
        assert result.returncode == 0
        assert "[192.168.1.128-192.168.1.255]:" in result.stdout
        os.unlink(f.name)


def test_overlap_stdin_input():
    input_text = "192.168.1.0/24\n192.168.1.128/25\n"
    result = run_cli(["overlap", "-"], input_text=input_text)
    assert result.returncode == 0
    assert "[192.168.1.128-192.168.1.255]:" in result.stdout


def test_overlap_invalid_input():
    result = run_cli(["overlap", "invalid-ip", "192.168.1.0/24"])
    assert result.returncode != 0
    assert "Error" in result.stderr or "error" in result.stderr


def test_overlap_empty_input():
    result = run_cli(["overlap", " "])
    assert result.returncode != 0
    assert "Error: No input provided" in result.stderr or "Error" in result.stderr


def test_overlap_json():
    result = run_cli(
        ["overlap", "--format", "json", "192.168.1.0/24", "192.168.1.128/25"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert any(d["overlap"].startswith("192.168.1.128")
               and "192.168.1.0-192.168.1.255" in d["sources"] for d in data)

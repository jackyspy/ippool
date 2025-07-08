import pytest
import random
from ippool.ippool import IPv4Pool, IPv6Pool
from ippool.ipv4 import IPv4Network, IPv4Address
from ippool.ipv6 import IPv6Network, IPv6Address


@pytest.fixture
def small_ipv4_pool():
    """小型IPv4池，用于基础性能测试"""
    return IPv4Pool(["192.168.1.0/24", "10.0.0.0/8", "172.16.0.0/12"])


@pytest.fixture
def medium_ipv4_pool():
    """中型IPv4池，用于中等规模性能测试"""
    networks = []
    # 生成100个不同的/24网段
    for i in range(100):
        networks.append(f"192.168.{i}.0/24")
    return IPv4Pool(networks)


@pytest.fixture
def large_ipv4_pool():
    """大型IPv4池，用于大规模性能测试"""
    networks = []
    # 生成1000个不同的网段，确保IP地址格式正确
    for i in range(1000):
        if i % 3 == 0:
            # 10.x.y.0/24 格式，确保 x 和 y 都在 0-255 范围内
            x = (i // 256) % 256
            y = i % 256
            networks.append(f"10.{x}.{y}.0/24")
        elif i % 3 == 1:
            # 172.x.y.0/24 格式，确保 x 在 16-31 范围内
            x = 16 + ((i // 256) % 16)
            y = i % 256
            networks.append(f"172.{x}.{y}.0/24")
        else:
            # 192.168.x.0/24 格式，确保 x 在 0-255 范围内
            x = i % 256
            networks.append(f"192.168.{x}.0/24")
    return IPv4Pool(networks)


@pytest.fixture
def small_ipv6_pool():
    """小型IPv6池，用于基础性能测试"""
    return IPv6Pool(["2001:db8::/32", "2001:db8:1::/48", "2001:db8:2::/48"])


@pytest.fixture
def medium_ipv6_pool():
    """中型IPv6池，用于中等规模性能测试"""
    networks = []
    # 生成50个不同的IPv6网段
    for i in range(50):
        networks.append(f"2001:db8:{i:04x}::/48")
    return IPv6Pool(networks)


class TestIPv4PoolBenchmarks:
    """IPv4Pool性能测试"""

    def test_add_single_network(self, benchmark):
        """测试添加单个网络"""
        pool = IPv4Pool()
        benchmark(pool.add, "192.168.1.0/24")

    def test_add_multiple_networks(self, benchmark):
        """测试添加多个网络"""
        pool = IPv4Pool()
        networks = [f"192.168.{i}.0/24" for i in range(100)]
        benchmark(pool.add, networks)

    def test_add_overlapping_networks(self, benchmark):
        """测试添加重叠网络（需要合并）"""
        pool = IPv4Pool()
        networks = [
            "192.168.1.0/24", "192.168.1.0/25", "192.168.1.128/25",
            "192.168.2.0/24"
        ]
        benchmark(pool.add, networks)

    def test_remove_single_network(self, benchmark, medium_ipv4_pool):
        """测试移除单个网络"""
        benchmark(medium_ipv4_pool.remove, "192.168.50.0/24")

    def test_remove_multiple_networks(self, benchmark, medium_ipv4_pool):
        """测试移除多个网络"""
        networks = [f"192.168.{i}.0/24" for i in range(10, 20)]
        benchmark(medium_ipv4_pool.remove, networks)

    def test_remove_overlapping_networks(self, benchmark, medium_ipv4_pool):
        """测试移除重叠网络"""
        networks = ["192.168.50.0/25", "192.168.50.128/25", "192.168.51.0/24"]
        benchmark(medium_ipv4_pool.remove, networks)

    def test_intersection_small(self, benchmark, small_ipv4_pool):
        """测试小型池的交集操作"""
        other = IPv4Pool(["192.168.1.0/24", "10.0.0.0/16"])
        benchmark(small_ipv4_pool.intersection, other)

    def test_intersection_medium(self, benchmark, medium_ipv4_pool):
        """测试中型池的交集操作"""
        other = IPv4Pool([f"192.168.{i}.0/24" for i in range(50, 70)])
        benchmark(medium_ipv4_pool.intersection, other)

    def test_intersection_large(self, benchmark, large_ipv4_pool):
        """测试大型池的交集操作"""
        other = IPv4Pool([f"10.{i}.0.0/24" for i in range(100, 200)])
        benchmark(large_ipv4_pool.intersection, other)

    def test_contains_single_ip(self, benchmark, medium_ipv4_pool):
        """测试包含单个IP地址"""
        ip = "192.168.50.100"
        benchmark(lambda: ip in medium_ipv4_pool)

    def test_contains_network(self, benchmark, medium_ipv4_pool):
        """测试包含网络"""
        network = "192.168.50.0/24"
        benchmark(lambda: network in medium_ipv4_pool)

    def test_contains_multiple_ips(self, benchmark, medium_ipv4_pool):
        """测试包含多个IP地址"""
        ips = [f"192.168.{i}.100" for i in range(10)]
        benchmark(lambda: all(ip in medium_ipv4_pool for ip in ips))

    def test_ip_ranges_small(self, benchmark, small_ipv4_pool):
        """测试获取IP范围（小型池）"""
        benchmark(lambda: small_ipv4_pool.ip_ranges)

    def test_ip_ranges_medium(self, benchmark, medium_ipv4_pool):
        """测试获取IP范围（中型池）"""
        benchmark(lambda: medium_ipv4_pool.ip_ranges)

    def test_ip_ranges_large(self, benchmark, large_ipv4_pool):
        """测试获取IP范围（大型池）"""
        benchmark(lambda: large_ipv4_pool.ip_ranges)

    def test_networks_property_small(self, benchmark, small_ipv4_pool):
        """测试networks属性（小型池）"""
        benchmark(lambda: small_ipv4_pool.networks)

    def test_networks_property_medium(self, benchmark, medium_ipv4_pool):
        """测试networks属性（中型池）"""
        benchmark(lambda: medium_ipv4_pool.networks)

    def test_networks_property_large(self, benchmark, large_ipv4_pool):
        """测试networks属性（大型池）"""
        benchmark(lambda: large_ipv4_pool.networks)

    def test_copy_small(self, benchmark, small_ipv4_pool):
        """测试复制操作（小型池）"""
        benchmark(small_ipv4_pool.copy)

    def test_copy_medium(self, benchmark, medium_ipv4_pool):
        """测试复制操作（中型池）"""
        benchmark(medium_ipv4_pool.copy)

    def test_copy_large(self, benchmark, large_ipv4_pool):
        """测试复制操作（大型池）"""
        benchmark(large_ipv4_pool.copy)

    def test_add_with_range_strings(self, benchmark):
        """测试添加IP范围字符串"""
        pool = IPv4Pool()
        ranges = [
            "192.168.1.1-192.168.1.100", "10.0.0.1-10.0.0.50",
            "172.16.1.1-172.16.1.200"
        ]
        benchmark(pool.add, ranges)

    def test_add_with_mixed_types(self, benchmark):
        """测试添加混合类型输入"""
        pool = IPv4Pool()
        mixed_input = [
            "192.168.1.0/24",
            IPv4Network("10.0.0.0/8"), "172.16.1.1-172.16.1.100",
            (int(IPv4Address("192.168.2.1")), int(IPv4Address("192.168.2.50")))
        ]
        benchmark(pool.add, mixed_input)


class TestIPv6PoolBenchmarks:
    """IPv6Pool性能测试"""

    def test_add_single_network(self, benchmark):
        """测试添加单个IPv6网络"""
        pool = IPv6Pool()
        benchmark(pool.add, "2001:db8::/32")

    def test_add_multiple_networks(self, benchmark):
        """测试添加多个IPv6网络"""
        pool = IPv6Pool()
        networks = [f"2001:db8:{i:04x}::/48" for i in range(50)]
        benchmark(pool.add, networks)

    def test_intersection_medium(self, benchmark, medium_ipv6_pool):
        """测试IPv6池的交集操作"""
        other = IPv6Pool([f"2001:db8:{i:04x}::/48" for i in range(20, 40)])
        benchmark(medium_ipv6_pool.intersection, other)

    def test_contains_ipv6(self, benchmark, medium_ipv6_pool):
        """测试包含IPv6地址"""
        ip = "2001:db8:0010::1"
        benchmark(lambda: ip in medium_ipv6_pool)

    def test_ip_ranges_ipv6(self, benchmark, medium_ipv6_pool):
        """测试获取IPv6范围"""
        benchmark(lambda: medium_ipv6_pool.ip_ranges)


class TestEdgeCaseBenchmarks:
    """边界情况性能测试"""

    def test_empty_pool_operations(self, benchmark):
        """测试空池操作"""
        pool = IPv4Pool()
        benchmark(lambda: len(pool.networks))

    def test_single_ip_pool(self, benchmark):
        """测试单个IP池"""
        pool = IPv4Pool("192.168.1.1/32")
        benchmark(lambda: pool.num_addresses)

    def test_large_network_pool(self, benchmark):
        """测试大型网络池"""
        pool = IPv4Pool("0.0.0.0/0")
        benchmark(lambda: pool.num_addresses)

    def test_highly_fragmented_pool(self, benchmark):
        """测试高度碎片化的池"""
        # 创建大量小的、不连续的网络
        networks = []
        for j in range(168, 180):
            for i in range(0, 255, 2):
                networks.append(f"192.{j}.{i}.0/30")
        pool = IPv4Pool(networks)
        benchmark(lambda: len(pool.networks))

    def test_merge_adjacent_networks(self, benchmark):
        """测试合并相邻网络"""
        # 创建相邻的网络，测试合并性能
        networks = []
        for i in range(100):
            networks.append(f"192.168.{i}.0/24")
        pool = IPv4Pool()
        benchmark(pool.add, networks)


class TestMemoryBenchmarks:
    """内存使用相关性能测试"""

    def test_large_pool_memory_usage(self, benchmark):
        """测试大型池的内存使用"""

        def create_large_pool():
            networks = [f"10.{i//256}.{i%256}.0/24" for i in range(10000)]
            return IPv4Pool(networks)

        benchmark(create_large_pool)

    def test_pool_serialization(self, benchmark, medium_ipv4_pool):
        """测试池的序列化性能"""
        benchmark(lambda: str(medium_ipv4_pool))

    def test_pool_repr(self, benchmark, medium_ipv4_pool):
        """测试池的repr性能"""
        benchmark(lambda: repr(medium_ipv4_pool))


# 配置基准测试参数
def pytest_benchmark_generate_json(config, benchmarks, include_data,
                                   machine_info, commit_info):
    """生成基准测试JSON报告"""
    return {
        "machine_info":
        machine_info,
        "commit_info":
        commit_info,
        "benchmarks": [{
            "name": benchmark.name,
            "stats": {
                "min": benchmark.stats.min,
                "max": benchmark.stats.max,
                "mean": benchmark.stats.mean,
                "stddev": benchmark.stats.stddev,
                "rounds": benchmark.stats.rounds,
            },
            "extra_info": benchmark.extra_info,
        } for benchmark in benchmarks],
    }

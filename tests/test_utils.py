import pytest
from ippool.utils import (merge_ip_ranges, summarize_range, collapse_networks,
                          find_overlapping_ranges)
from ippool.ipv4 import IPv4Network, IPv4Address
from ippool.ipv6 import IPv6Network, IPv6Address
from ippool.ippool import IPv4Pool
from ippool.iprange import IPv4Range, IPv6Range


# merge_ip_ranges 测试
def test_merge_ip_ranges_empty():
    """测试空列表"""
    result = merge_ip_ranges([])
    assert result == []


def test_merge_ip_ranges_single():
    """测试单个范围"""
    result = merge_ip_ranges([(1, 10)])
    assert result == [(1, 10)]


def test_merge_ip_ranges_overlapping():
    """测试重叠范围"""
    result = merge_ip_ranges([(1, 10), (5, 15), (20, 30)])
    assert result == [(1, 15), (20, 30)]


def test_merge_ip_ranges_adjacent():
    """测试相邻范围"""
    result = merge_ip_ranges([(1, 10), (11, 20), (25, 30)])
    assert result == [(1, 20), (25, 30)]


def test_merge_ip_ranges_unsorted():
    """测试未排序的范围"""
    result = merge_ip_ranges([(20, 30), (1, 10), (5, 15)])
    assert result == [(1, 15), (20, 30)]


def test_merge_ip_ranges_generator_equivalent():
    """测试 merge_ip_ranges 的生成器输出与列表输出一致"""
    ranges = [(1, 10), (5, 15), (20, 30)]
    result_list = merge_ip_ranges(ranges)
    result_gen = list(merge_ip_ranges(ranges, as_generator=True))
    assert result_list == result_gen

    # 测试空输入
    assert list(merge_ip_ranges([], as_generator=True)) == []

    # 测试未排序输入
    unsorted = [(20, 30), (1, 10), (5, 15)]
    assert list(merge_ip_ranges(
        unsorted, as_generator=True)) == merge_ip_ranges(unsorted)


# summarize_range IPv4 测试
def test_summarize_range_ipv4_single_ip():
    """单个IPv4地址"""
    result = summarize_range(3232235777, 3232235777,
                             ip_version=4)  # 192.168.1.1
    assert len(result) == 1
    assert result[0] == IPv4Network("192.168.1.1/32")


def test_summarize_range_ipv4_cidr():
    """完整的IPv4 /24网段"""
    start = int(IPv4Network("192.168.1.0/24").network_address)
    end = int(IPv4Network("192.168.1.0/24").broadcast_address)
    result = summarize_range(start, end, ip_version=4)
    assert len(result) == 1
    assert result[0] == IPv4Network("192.168.1.0/24")


def test_summarize_range_ipv4_partial():
    """非对齐的IPv4区间"""
    start = int(IPv4Network("192.168.1.10/32").network_address)
    end = int(IPv4Network("192.168.1.20/32").network_address)
    result = summarize_range(start, end, ip_version=4)
    # 检查覆盖范围
    covered = set()
    for net in result:
        covered.update(
            range(int(net.network_address),
                  int(net.broadcast_address) + 1))
    assert covered == set(range(start, end + 1))


def test_summarize_range_ipv4_large():
    """大IPv4区间（跨多个网段）"""
    start = int(IPv4Network("10.0.0.0/8").network_address)
    end = int(IPv4Network("10.0.3.255/24").broadcast_address)
    result = summarize_range(start, end, ip_version=4)
    # 检查覆盖范围
    covered = set()
    for net in result:
        covered.update(
            range(int(net.network_address),
                  int(net.broadcast_address) + 1))
    assert covered == set(range(start, end + 1))


def test_summarize_range_ipv4_edge():
    """IPv4边界情况：全0和全1"""
    start = 0
    end = 0xFFFFFFFF
    result = summarize_range(start, end, ip_version=4)
    # 应该只返回一个/0网段
    assert len(result) == 1
    assert result[0] == IPv4Network("0.0.0.0/0")


def test_summarize_range_ipv4_default():
    """测试IPv4默认参数"""
    result = summarize_range(3232235777, 3232235777)  # 默认ip_version=4
    assert len(result) == 1
    assert result[0] == IPv4Network("192.168.1.1/32")


def test_summarize_range_invalid_version():
    """测试无效的IP版本"""
    with pytest.raises(ValueError, match="ip_version must be 4 or 6"):
        summarize_range(1, 10, ip_version=5)


# summarize_range IPv6 测试
def test_summarize_range_ipv6_single_ip():
    """单个IPv6地址"""
    start = int(IPv6Network("2001:db8::1/128").network_address)
    end = int(IPv6Network("2001:db8::1/128").broadcast_address)
    result = summarize_range(start, end, ip_version=6)
    assert len(result) == 1
    assert result[0] == IPv6Network("2001:db8::1/128")


def test_summarize_range_ipv6_cidr():
    """完整的IPv6 /64网段"""
    start = int(IPv6Network("2001:db8::/64").network_address)
    end = int(IPv6Network("2001:db8::/64").broadcast_address)
    result = summarize_range(start, end, ip_version=6)
    assert len(result) == 1
    assert result[0] == IPv6Network("2001:db8::/64")


def test_summarize_range_ipv6_partial():
    """非对齐的IPv6区间"""
    start = int(IPv6Network("2001:db8::10/128").network_address)
    end = int(IPv6Network("2001:db8::20/128").network_address)
    result = summarize_range(start, end, ip_version=6)
    # 检查覆盖范围
    covered = set()
    for net in result:
        covered.update(
            range(int(net.network_address),
                  int(net.broadcast_address) + 1))
    assert covered == set(range(start, end + 1))


# collapse_networks IPv4 测试
def test_collapse_networks_ipv4_empty():
    """空IPv4网络列表"""
    result = collapse_networks([])
    assert result == ()


def test_collapse_networks_ipv4_single():
    """单个IPv4网络"""
    networks = [IPv4Network("192.168.1.0/24")]
    result = collapse_networks(networks)
    assert result == (IPv4Network("192.168.1.0/24"), )


def test_collapse_networks_ipv4_adjacent():
    """相邻的IPv4网络"""
    networks = [IPv4Network("192.168.1.0/24"), IPv4Network("192.168.0.0/24")]
    result = collapse_networks(networks)
    assert len(result) == 1
    assert result[0] == IPv4Network("192.168.0.0/23")


def test_collapse_networks_ipv4_overlapping():
    """重叠的IPv4网络"""
    networks = [IPv4Network("192.168.1.0/24"), IPv4Network("192.168.1.128/25")]
    result = collapse_networks(networks)
    assert len(result) == 1
    assert result[0] == IPv4Network("192.168.1.0/24")


def test_collapse_networks_ipv4_disjoint():
    """不相连的IPv4网络"""
    networks = [IPv4Network("192.168.1.0/24"), IPv4Network("192.168.3.0/24")]
    result = collapse_networks(networks)
    assert len(result) == 2
    assert IPv4Network("192.168.1.0/24") in result
    assert IPv4Network("192.168.3.0/24") in result


def test_collapse_networks_ipv4_complex():
    """复杂的IPv4网络合并"""
    networks = [
        IPv4Network("192.168.1.0/24"),
        IPv4Network("192.168.2.0/24"),
        IPv4Network("192.168.3.0/24"),
        IPv4Network("192.168.5.0/24")
    ]
    result = collapse_networks(networks)
    assert result == (IPv4Network("192.168.1.0/24"),
                      IPv4Network("192.168.2.0/23"),
                      IPv4Network("192.168.5.0/24"))


# collapse_networks IPv6 测试
def test_collapse_networks_ipv6_empty():
    """空IPv6网络列表"""
    result = collapse_networks([])
    assert result == ()


def test_collapse_networks_ipv6_single():
    """单个IPv6网络"""
    networks = [IPv6Network("2001:db8::/64")]
    result = collapse_networks(networks)
    assert result == (IPv6Network("2001:db8::/64"), )


def test_collapse_networks_ipv6_adjacent():
    """相邻的IPv6网络"""
    networks = [IPv6Network("2001:db8::/64"), IPv6Network("2001:db8:0:1::/64")]
    result = collapse_networks(networks)
    assert len(result) == 1
    assert result[0] == IPv6Network("2001:db8::/63")


def test_collapse_networks_ipv6_overlapping():
    """重叠的IPv6网络"""
    networks = [IPv6Network("2001:db8::/64"), IPv6Network("2001:db8::/80")]
    result = collapse_networks(networks)
    assert len(result) == 1
    assert result[0] == IPv6Network("2001:db8::/64")


def test_collapse_networks_ipv6_disjoint():
    """不相连的IPv6网络"""
    networks = [IPv6Network("2001:db8::/64"), IPv6Network("2001:db8:0:2::/64")]
    result = collapse_networks(networks)
    assert len(result) == 2
    assert IPv6Network("2001:db8::/64") in result
    assert IPv6Network("2001:db8:0:2::/64") in result


# 错误处理测试
def test_collapse_networks_invalid_type():
    """测试无效的网络对象类型"""
    with pytest.raises(
            ValueError,
            match="networks must contain IPv4Network or IPv6Network objects"):
        collapse_networks([None])


def test_merge_ip_ranges_with_set_and_generator():
    s = {(1, 2), (3, 4)}
    result = merge_ip_ranges(s, True)
    assert isinstance(result, list)
    g = ((i, i + 1) for i in range(0, 10, 2))
    result2 = merge_ip_ranges(g, True)
    assert isinstance(result2, list)


def test_find_overlapping_ranges_empty():
    result = find_overlapping_ranges([])
    assert result == []


def test_find_overlapping_ranges_simple_overlap():
    ranges = ['192.168.1.0/24', '192.168.1.128/25']
    result = find_overlapping_ranges(ranges)
    assert len(result) == 1
    overlap_range, involved_sources = result[0]
    expected = IPv4Range('192.168.1.128', '192.168.1.255')
    assert overlap_range == expected
    assert len(involved_sources) == 2
    assert all(isinstance(r, IPv4Range) for r in involved_sources)
    for src in involved_sources:
        assert src.start <= overlap_range.start and src.end >= overlap_range.end


def test_find_overlapping_ranges_complex_example():
    ranges = [
        '192.168.1.0/24',
        '192.168.1.100-200',
        '192.168.1.20-192.168.1.30',
        ('192.168.1.60', '192.168.2.200'),
        (3232235996, 3232236132),
        IPv4Range(3232236042, 3232236082),
    ]
    result = find_overlapping_ranges(ranges)
    assert len(result) > 0
    for overlap_range, involved_sources in result:
        assert len(involved_sources) >= 2
        assert overlap_range.start <= overlap_range.end
        for src in involved_sources:
            assert src.start <= overlap_range.start and src.end >= overlap_range.end
            assert src.start <= overlap_range.end and src.end >= overlap_range.start
            assert isinstance(src, IPv4Range)
        assert isinstance(overlap_range, IPv4Range)


def test_find_overlapping_ranges_mixed_formats():
    ranges = [
        '192.168.1.0/24',
        IPv4Network('192.168.1.128/25'),
        IPv4Range('192.168.1.100', '192.168.1.200'),
        (int(IPv4Address('192.168.1.50')), int(IPv4Address('192.168.1.150'))),
        3232235777,  # 192.168.1.1
    ]
    result = find_overlapping_ranges(ranges)
    assert len(result) > 0
    for overlap_range, involved_sources in result:
        for src in involved_sources:
            assert src.start <= overlap_range.start and src.end >= overlap_range.end


def test_find_overlapping_ranges_ipv6():
    ranges = [
        '2001:db8::/48',
        '2001:db8:1::/64',
        IPv6Range('2001:db8::1', '2001:db8::100'),
        (int(IPv6Address('2001:db8::10')), int(IPv6Address('2001:db8::50'))),
    ]
    result = find_overlapping_ranges(ranges, ipv6=True)
    assert len(result) > 0
    for overlap_range, involved_sources in result:
        for src in involved_sources:
            assert src.start <= overlap_range.start and src.end >= overlap_range.end


def test_find_overlapping_ranges_multiple_overlaps():
    ranges = [
        '192.168.1.0/24',
        '192.168.1.50-150',
        '192.168.1.100-200',
        '192.168.1.75-125',
    ]
    result = find_overlapping_ranges(ranges)
    assert len(result) > 0
    overlap_starts = [overlap[0][0] for overlap in result]
    assert overlap_starts == sorted(overlap_starts)
    for overlap_range, involved_sources in result:
        for src in involved_sources:
            assert src.start <= overlap_range.start and src.end >= overlap_range.end


def test_find_overlapping_ranges_edge_cases():
    # 完全重叠
    ranges = ['192.168.1.0/24', '192.168.1.0-255']
    result = find_overlapping_ranges(ranges)
    assert len(result) == 1
    overlap_range, involved_sources = result[0]
    expected = IPv4Range('192.168.1.0', '192.168.1.255')
    assert overlap_range == expected
    assert involved_sources == [expected]
    for src in involved_sources:
        assert src.start <= overlap_range.start and src.end >= overlap_range.end
    # 相邻但不重叠
    ranges = ['192.168.1.0/24', '192.168.2.0/24']
    result = find_overlapping_ranges(ranges)
    assert result == []


def test_find_overlapping_ranges_invalid_input():
    with pytest.raises(TypeError):
        find_overlapping_ranges([(1, 2, 3)])
    with pytest.raises(ValueError):
        find_overlapping_ranges(['invalid-ip'])
    with pytest.raises(TypeError):
        find_overlapping_ranges([object()])


def test_find_overlapping_ranges_comprehensive():
    ranges = [
        '192.168.1.0/24',
        '192.168.1.100-192.168.1.200',
        IPv4Network('192.168.1.128/25'),
        IPv4Range('192.168.1.50', '192.168.1.150'),
        (int(IPv4Address('192.168.1.75')), int(IPv4Address('192.168.1.125'))),
        ('192.168.1.80', '192.168.1.120'),
        3232236042,  # 192.168.2.10
    ]
    result = find_overlapping_ranges(ranges)
    assert len(result) > 0
    for overlap_range, involved_sources in result:
        assert len(involved_sources) >= 2
        for src_start, src_end in involved_sources:
            assert src_start <= overlap_range[1] and src_end >= overlap_range[0]
    for overlap_range, involved_sources in result:
        for src in involved_sources:
            assert src.start <= overlap_range.start and src.end >= overlap_range.end


def test_find_overlapping_ranges_ipv6_mode():
    ranges = [
        '2001:db8::/48',
        '2001:db8:1::/64',
        IPv6Range('2001:db8::1', '2001:db8::100'),
    ]
    result = find_overlapping_ranges(ranges, ipv6=True)
    assert len(result) == 1
    for overlap_range, involved_sources in result:
        assert isinstance(overlap_range, IPv6Range)
        assert overlap_range.start <= overlap_range.end
        for src in involved_sources:
            assert isinstance(src, IPv6Range)
            assert src.start <= overlap_range.start and src.end >= overlap_range.end


def test_find_overlapping_ranges_ipv6_single_ip():
    ranges = [
        int(IPv6Address('2001:db8::1')),
        '2001:db8::1/128',
        IPv6Address('2001:db8::1'),
    ]
    result = find_overlapping_ranges(ranges, ipv6=True)
    assert len(result) == 1
    for overlap_range, involved_sources in result:
        assert overlap_range[0] == overlap_range[1] == IPv6Address(
            '2001:db8::1')
        for src in involved_sources:
            assert src.start <= overlap_range[0] and src.end >= overlap_range[1]

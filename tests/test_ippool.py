import pytest
from ippool.iprange import IPv4Range, IPv6Range
from ippool.ippool import IPv4Pool, IPv6Pool
from ippool.ipv4 import IPv4Network, IPv4Address
from ippool.ipv6 import IPv6Network, IPv6Address


# Test cases for IPv4Pool
def test_ipv4_pool_init():
    pool = IPv4Pool()
    assert len(pool.networks) == 0

    pool2 = IPv4Pool(["192.168.1.0/24", "10.0.0.0/8"])
    assert len(pool2.networks) == 2
    assert IPv4Network("192.168.1.0/24") in pool2.networks
    assert IPv4Network("10.0.0.0/8") in pool2.networks


def test_ipv4_pool_add():
    # 测试字符串参数
    pool = IPv4Pool()
    pool.add("192.168.1.0/24")
    assert len(pool.networks) == 1
    assert IPv4Network("192.168.1.0/24") in pool.networks
    assert len(pool._ranges) == 1
    expected_start = int(IPv4Network("192.168.1.0/24").network_address)
    expected_end = int(IPv4Network("192.168.1.0/24").broadcast_address)
    assert pool._ranges[0] == (expected_start, expected_end)

    # 测试列表参数
    pool.add(["10.0.0.0/8", "192.168.2.0/24"])
    assert len(pool.networks) == 3
    assert IPv4Network("10.0.0.0/8") == pool.networks[0]
    assert IPv4Network("192.168.1.0/24") == pool.networks[1]
    assert IPv4Network("192.168.2.0/24") == pool.networks[2]

    # 测试+=操作符
    pool += "192.168.0.0/23"  # 应该与192.168.1.0/24
    assert pool.networks == (IPv4Network("10.0.0.0/8"),
                             IPv4Network("192.168.0.0/23"),
                             IPv4Network("192.168.2.0/24"))
    # 192.168.0.0-192.168.2.255 连续
    expected_ranges = (
        (int(IPv4Network("10.0.0.0/8").network_address),
         int(IPv4Network("10.0.0.0/8").broadcast_address)),
        (int(IPv4Network("192.168.0.0/23").network_address),
         int(IPv4Network("192.168.2.0/24").broadcast_address)),
    )
    assert pool._ranges == expected_ranges


def test_ipv4_pool_add_various_types():
    # 1. 添加本类对象
    pool1 = IPv4Pool("192.168.1.0/24")
    pool2 = IPv4Pool("10.0.0.0/8")
    pool3 = IPv4Pool("192.168.0.0/24")
    pool1.add(pool2)
    pool1 += pool3
    assert IPv4Network("10.0.0.0/8") in pool1.networks
    assert IPv4Network("192.168.0.0/23") in pool1.networks

    # 2. 添加单个网络对象
    pool = IPv4Pool()
    net = IPv4Network("172.16.0.0/16")
    pool.add(net)
    assert net in pool.networks

    # 3. 添加多行字符串
    pool = IPv4Pool()
    pool.add("192.168.10.0/24\n192.168.20.0/24")
    assert IPv4Network("192.168.10.0/24") in pool.networks
    assert IPv4Network("192.168.20.0/24") in pool.networks

    # 4. 添加IP区间字符串（完整IP-完整IP）
    pool = IPv4Pool()
    pool.add("192.168.100.1-192.168.100.10")
    # 检查_ranges数量
    assert len(pool._ranges) == 1
    # 检查start/end ip值
    assert pool._ranges[0][0] == int(IPv4Address("192.168.100.1"))
    assert pool._ranges[0][1] == int(IPv4Address("192.168.100.10"))

    # 5. 添加IP区间字符串（完整IP-结尾数字）
    assert IPv4Pool("192.168.100.1-192.168.100.10") == IPv4Pool(
        "192.168.100.1-10")

    # 6. 添加混合类型（网络对象、区间、字符串）
    pool = IPv4Pool()
    pool.add([
        IPv4Network("10.10.0.0/24"), "10.10.1.0-10.10.1.10", "10.10.2.0/30",
        (int(IPv4Address("10.10.3.1")), int(IPv4Address("10.10.3.5")))
    ])
    # 检查所有IP都被包含
    for ip in ["10.10.0.1", "10.10.1.5", "10.10.2.2", "10.10.3.3"]:
        assert IPv4Address(ip) in pool
    # 检查_ranges内容
    expected_ranges = (
        (int(IPv4Address("10.10.0.0")), int(IPv4Address("10.10.1.10"))),
        (int(IPv4Address("10.10.2.0")), int(IPv4Address("10.10.2.3"))),
        (int(IPv4Address("10.10.3.1")), int(IPv4Address("10.10.3.5"))),
    )
    assert pool._ranges == expected_ranges

    # 7. 添加元组区间
    pool = IPv4Pool()
    pool.add([(int(IPv4Address("192.168.50.1")),
               int(IPv4Address("192.168.50.5")))])
    for i in range(1, 6):
        assert IPv4Address(f"192.168.50.{i}") in pool
    # 检查_ranges内容
    expected_ranges = ((int(IPv4Address("192.168.50.1")),
                        int(IPv4Address("192.168.50.5"))), )
    assert pool._ranges == expected_ranges

    pool = IPv4Pool([['192.168.1.1', '192.168.1.10']])
    expected_ranges = ((int(IPv4Address("192.168.1.1")),
                        int(IPv4Address("192.168.1.10"))), )
    assert pool._ranges == expected_ranges


def test_ipv4_pool_remove():
    # 基础移除
    pool = IPv4Pool(["192.168.0.0/23", "10.0.0.0/8"])
    pool.remove("192.168.1.0/24")
    assert len(pool.networks) == 2
    assert IPv4Network("192.168.0.0/24") in pool.networks
    assert "192.168.1.0" not in pool
    assert IPv4Network("10.0.0.0/8") in pool.networks

    pool -= "10.0.0.0/8"
    assert len(pool.networks) == 1
    assert IPv4Network("10.0.0.0/8") not in pool.networks
    assert IPv4Network("192.168.0.0/24") in pool.networks

    pool = IPv4Pool(["192.168.1.0/24"])
    pool.remove("192.168.2.128/25")
    assert IPv4Network("192.168.1.0/24") in pool.networks

    # 移除部分重叠区间
    pool = IPv4Pool(["192.168.1.0/24"])
    pool.remove("192.168.1.128/25")
    assert IPv4Network("192.168.1.0/25") in pool.networks
    assert IPv4Network("192.168.1.128/25") not in pool.networks

    # 移除完全覆盖区间
    pool = IPv4Pool(["192.168.2.0/24"])
    pool.remove("192.168.2.0/24")
    assert len(pool.networks) == 0

    # 移除相邻但不重叠区间
    pool = IPv4Pool(["192.168.3.0/24"])
    pool.remove("192.168.4.0/24")
    assert IPv4Network("192.168.3.0/24") in pool.networks

    # 移除多段区间
    pool = IPv4Pool(["10.0.0.0/8", "192.168.0.0/16"])
    pool.remove(["10.0.0.0/9", "192.168.128.0/17"])
    assert IPv4Network("10.128.0.0/9") in pool.networks
    assert IPv4Network("192.168.0.0/17") in pool.networks
    assert IPv4Network("10.0.0.0/9") not in pool.networks
    assert IPv4Network("192.168.128.0/17") not in pool.networks

    # 严格模式下的异常
    pool = IPv4Pool(["192.168.5.0/24"])
    with pytest.raises(ValueError):
        pool.remove("192.168.5.0/23", strict=True)
    # 严格模式下正常
    pool = IPv4Pool(["192.168.6.0/24"])
    pool.remove("192.168.6.0/24", strict=True)
    assert len(pool.networks) == 0

    # 移除不存在区间
    pool = IPv4Pool(["192.168.7.0/24"])
    pool.remove("10.0.0.0/8")
    assert IPv4Network("192.168.7.0/24") in pool.networks

    # 移除区间后池为空
    pool = IPv4Pool(["192.168.8.0/24"])
    pool.remove("192.168.8.0-192.168.8.255")
    assert len(pool.networks) == 0

    # 支持多种输入类型
    pool = IPv4Pool(["192.168.9.0/24"])
    pool.remove(IPv4Network("192.168.9.0/25"))
    assert IPv4Network("192.168.9.128/25") in pool.networks
    pool.remove([IPv4Network("192.168.9.128/25")])
    assert len(pool.networks) == 0


def test_ipv4_pool_intersection():
    # 完全重叠
    pool1 = IPv4Pool(["192.168.1.0/24", "10.0.0.0/8"])
    pool2 = IPv4Pool(["192.168.1.0/24", "10.0.0.0/8"])
    intersection_pool = pool1 & pool2
    assert intersection_pool.networks == (IPv4Network("10.0.0.0/8"),
                                          IPv4Network("192.168.1.0/24"))

    # 部分重叠
    pool1 = IPv4Pool(["192.168.1.0/24", "10.0.0.0/8"])
    pool2 = IPv4Pool(["192.168.1.128/25", "10.0.0.0/16"])
    intersection_pool = pool1 & pool2
    assert intersection_pool.networks == (IPv4Network("10.0.0.0/16"),
                                          IPv4Network("192.168.1.128/25"))

    # 无重叠
    pool1 = IPv4Pool(["192.168.1.0/24"])
    pool2 = IPv4Pool(["10.0.0.0/8"])
    intersection_pool = pool1 & pool2
    assert len(intersection_pool._ranges) == 0

    # 相邻但不重叠
    pool1 = IPv4Pool(["192.168.1.0/24"])
    pool2 = IPv4Pool(["192.168.2.0/24"])
    intersection_pool = pool1 & pool2
    assert len(intersection_pool._ranges) == 0

    # 多区间交集
    pool1 = IPv4Pool(["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"])
    pool2 = IPv4Pool(["10.0.0.0/16", "172.16.1.0/24", "192.168.1.0/24"])
    intersection_pool = pool1 & pool2
    assert intersection_pool.networks == (
        IPv4Network("10.0.0.0/16"),
        IPv4Network("172.16.1.0/24"),
        IPv4Network("192.168.1.0/24"),
    )

    # 字符串、区间混合输入
    pool1 = IPv4Pool(["192.168.1.0/24", "10.0.0.0/8"])
    intersection_pool = pool1 & IPv4Pool([
        IPv4Network("192.168.1.128/25"),
        (int(IPv4Address("10.0.0.0")), int(IPv4Address("10.0.0.255")))
    ])
    assert intersection_pool.networks == (
        IPv4Network("10.0.0.0/24"),
        IPv4Network("192.168.1.128/25"),
    )

    assert len(pool1 & IPv4Pool()) == 0
    assert len(pool1 & "\n") == 0


def test_ipv4_pool_contains():
    pool = IPv4Pool(["192.168.1.0/24", "10.0.0.0/8"])
    assert IPv4Address("192.168.1.10") in pool
    assert IPv4Network("192.168.1.0/24") in pool
    assert IPv4Address("10.0.0.1") in pool
    assert "10.0.0.0/16" in pool
    assert IPv4Address("192.168.2.1") not in pool
    assert IPv4Network("192.168.2.0/24") not in pool
    assert '1.1.1.1' not in pool
    assert '1.1.1.1' not in IPv4Pool()

    pool = IPv4Pool(["192.168.1.0/24", "192.168.2.10-20"])
    assert "192.168.2.15" in pool
    assert IPv4Pool("192.168.2.15") in pool
    assert IPv4Pool(["192.168.1.0/25", "192.168.2.15-20"]) in pool
    assert IPv4Pool("192.168.2.15-21") not in pool

    with pytest.raises(ValueError):
        _ = 'abc' in pool


def test_ipv4_pool_num_addresses():
    # 单个网段
    pool = IPv4Pool(["192.168.1.0/24"])
    assert pool.num_addresses == 256

    # 多个不连续网段
    pool = IPv4Pool(["192.168.1.0/24", "10.0.0.0/8"])
    assert pool.num_addresses == 256 + 2**24

    # 连续网段合并
    pool = IPv4Pool(["192.168.0.0/24", "192.168.1.0/24"])
    assert pool.num_addresses == 512

    # 地址范围
    pool = IPv4Pool(["192.168.1.100-192.168.2.200"])
    assert pool.num_addresses == 256 - 100 + 201
    pool = IPv4Pool(["192.168.1.100-192.168.1.200"])
    assert pool.num_addresses == 200 - 100 + 1

    # 空池
    pool = IPv4Pool()
    assert pool.num_addresses == 0

    # 大区间
    pool = IPv4Pool(["0.0.0.0/0"])
    assert pool.num_addresses == 2**32


def test_ipv4_pool_ip_ranges():
    pool = IPv4Pool(["192.168.1.0/24", "192.168.2.0/24"])
    ip_ranges = pool.ip_ranges
    assert len(ip_ranges) == 1
    assert str(ip_ranges[0]) == "192.168.1.0-192.168.2.255"

    pool2 = IPv4Pool(["192.168.1.0/24", "192.168.1.255"])
    ip_ranges2 = pool2.ip_ranges
    assert len(ip_ranges2) == 1
    assert str(ip_ranges2[0]) == "192.168.1.0-192.168.1.255"

    pool3 = IPv4Pool(["192.168.1.0/24", "192.168.1.50-192.168.2.50"])
    ip_ranges3 = pool3.ip_ranges
    assert len(ip_ranges3) == 1
    assert str(ip_ranges3[0]) == "192.168.1.0-192.168.2.50"

    pool4 = IPv4Pool(["192.168.1.0/24", "192.168.3.0/24"])
    ip_ranges4 = pool4.ip_ranges
    assert len(ip_ranges4) == 2
    assert str(ip_ranges4[0]) == "192.168.1.0-192.168.1.255"
    assert str(ip_ranges4[1]) == "192.168.3.0-192.168.3.255"

    pool5 = IPv4Pool(["192.168.0.0/16"]) - IPv4Pool(["192.168.1.0/24"])
    ip_ranges5 = pool5.ip_ranges
    assert len(ip_ranges5) == 2
    assert str(ip_ranges5[0]) == "192.168.0.0-192.168.0.255"
    assert str(ip_ranges5[1]) == "192.168.2.0-192.168.255.255"


# Test cases for IPv6Pool (basic)
def test_ipv6_pool_add():
    pool = IPv6Pool()
    pool.add("2001:db8::/32")
    assert len(pool.networks) == 1
    assert IPv6Network("2001:db8::/32") in pool.networks

    # 添加多个不连续网段
    pool = IPv6Pool()
    pool.add(["2001:db8:1::/48", "2001:db8:2::/48"])
    assert pool._ranges == ((
        int(IPv6Network("2001:db8:1::/48").network_address),
        int(IPv6Network("2001:db8:2::/48").broadcast_address)), )

    # 合并相邻网段
    pool = IPv6Pool(["2001:db8::/48", "2001:db8:1::/48"])
    assert pool.networks == (IPv6Network("2001:db8::/47"), )

    # 添加区间字符串
    pool = IPv6Pool()
    pool.add("2001:db8::1-2001:db8::10")
    assert any(
        int(net.network_address) <= int(IPv6Address("2001:db8::5")) <= int(
            net.broadcast_address) for net in pool.networks)

    # 添加单个IPv6地址
    pool = IPv6Pool()
    pool.add("2001:db8::1/128")
    assert IPv6Network("2001:db8::1/128") in pool.networks

    # 添加本类对象
    pool1 = IPv6Pool("2001:db8::/32")
    pool2 = IPv6Pool("2001:db8:1::/48")
    pool1.add(pool2)
    assert IPv6Network("2001:db8::/32") in pool1.networks
    assert IPv6Network("2001:db8:1::/48") not in pool1.networks


def test_format_ip_ranges_with_pool():
    pool = IPv4Pool()
    pool._ranges = ((int(IPv4Network("192.168.1.0/24").network_address),
                     int(IPv4Network("192.168.1.0/24").broadcast_address)),
                    (int(IPv4Network("10.0.0.0/8").network_address),
                     int(IPv4Network("10.0.0.0/8").broadcast_address)))
    result = pool._format_ip_ranges(pool)
    assert result == pool._ranges


def test_format_ip_ranges_with_single_network():
    pool = IPv4Pool()
    net = IPv4Network("192.168.1.0/24")
    result = pool._format_ip_ranges(net)
    assert result == ((int(net.network_address), int(net.broadcast_address)), )


def test_format_ip_ranges_with_str():
    pool = IPv4Pool()
    result = pool._format_ip_ranges("192.168.1.0/24\n10.0.0.1-10.0.0.10")
    assert (int(IPv4Network("192.168.1.0/24").network_address),
            int(IPv4Network("192.168.1.0/24").broadcast_address)) in result
    assert any(start <= int(IPv4Network("10.0.0.1/32").network_address) <= end
               for start, end in result)


def test_format_ip_ranges_with_tuple():
    pool = IPv4Pool()
    result = pool._format_ip_ranges([(3232235777, 3232235780)])
    assert result == ((3232235777, 3232235780), )


def test_format_ip_ranges_with_mixed():
    pool = IPv4Pool()
    net = IPv4Network("192.168.1.0/24")
    result = pool._format_ip_ranges(
        [net, (3232235777, 3232235780), "10.0.0.1-10.0.0.10"])
    # 检查所有区间都被包含
    assert any(start <= 3232235777 <= end for start, end in result)
    assert any(start <= int(net.network_address) <= end
               for start, end in result)
    assert any(start <= int(IPv4Network("10.0.0.1/32").network_address) <= end
               for start, end in result)


def test_networks_property_ipv4():
    # 单个网段
    pool = IPv4Pool("192.168.1.0/24")
    assert isinstance(pool.networks, tuple)
    assert pool.networks == (IPv4Network("192.168.1.0/24"), )

    # 多个不连续网段
    pool = IPv4Pool(["192.168.1.0/24", "10.0.0.0/8"])
    expected = [IPv4Network("10.0.0.0/8"), IPv4Network("192.168.1.0/24")]
    assert sorted(pool.networks,
                  key=lambda n: int(n.network_address)) == sorted(
                      expected, key=lambda n: int(n.network_address))

    # 连续网段合并
    pool = IPv4Pool(["192.168.0.0/24", "192.168.1.0/24"])
    assert pool.networks == (IPv4Network("192.168.0.0/23"), )

    # 添加后合并
    pool = IPv4Pool("192.168.1.0/24")
    pool.add("192.168.0.0/24")
    assert pool.networks == (IPv4Network("192.168.0.0/23"), )

    # 多种类型输入
    pool = IPv4Pool()
    pool.add([
        IPv4Network("10.0.0.0/24"), "10.0.1.0-10.0.1.10",
        (int(IPv4Address("10.0.2.1")), int(IPv4Address("10.0.2.5")))
    ])
    assert any(IPv4Network("10.0.0.0/24") == net for net in pool.networks)
    assert any(
        int(IPv4Address("10.0.1.5")) >= int(net.network_address)
        and int(IPv4Address("10.0.1.5")) <= int(net.broadcast_address)
        for net in pool.networks)
    assert any(
        int(IPv4Address("10.0.2.3")) >= int(net.network_address)
        and int(IPv4Address("10.0.2.3")) <= int(net.broadcast_address)
        for net in pool.networks)

    # 空池
    pool = IPv4Pool()
    assert pool.networks == ()


def test_add_empty_input():
    pool = IPv4Pool()
    original_ranges = pool._ranges
    pool.add("")
    assert pool._ranges == original_ranges


def test_add_none_input():
    pool = IPv4Pool()
    original_ranges = pool._ranges
    pool.add(None)
    assert pool._ranges == original_ranges


def test_add_empty_list():
    pool = IPv4Pool()
    original_ranges = pool._ranges
    pool.add([])
    assert pool._ranges == original_ranges


def test_format_ip_ranges_empty():
    pool = IPv4Pool()
    assert pool._format_ip_ranges([]) == ()
    assert pool._format_ip_ranges(None) == ()


def test_format_ip_ranges_invalid_type():
    pool = IPv4Pool()
    with pytest.raises(TypeError):
        pool._format_ip_ranges(object())


def test_format_ip_ranges_invalid_str():
    pool = IPv4Pool()
    with pytest.raises(ValueError):
        pool._format_ip_ranges("invalid-ip")

    with pytest.raises(ValueError):
        pool._format_ip_ranges("192.168.1.1-300")

    with pytest.raises(ValueError):
        pool._format_ip_ranges("192.168.1.1-192.168.1.300")

    with pytest.raises(ValueError):
        pool._format_ip_ranges("192.168.1.1-ip")


def test_format_ip_ranges_tuple():
    pool = IPv4Pool()
    result = pool._format_ip_ranges([(IPv4Address("192.168.1.1"),
                                      IPv4Address("192.168.1.10"))])
    assert result == ((IPv4Address("192.168.1.1"),
                       IPv4Address("192.168.1.10")), )


def test_format_ip_ranges_with_iprange():
    pool = IPv4Pool()
    r = IPv4Range("192.168.1.1", "192.168.1.10")
    result = pool._format_ip_ranges([r])
    # result 是 ((IPv4Address('192.168.1.1'), IPv4Address('192.168.1.10')),)
    assert (r.start, r.end) in result


def test_intersection_empty():
    pool = IPv4Pool()
    result = pool.intersection(None)
    assert isinstance(result, IPv4Pool)
    assert len(result.networks) == 0
    pool2 = IPv4Pool()
    result2 = pool.intersection(pool2)
    assert isinstance(result2, IPv4Pool)
    assert len(result2.networks) == 0


def test_remove_empty():
    pool = IPv4Pool()
    result = pool.remove(None)
    assert result is pool
    pool2 = IPv4Pool()
    result2 = pool.remove(pool2)
    assert result2 is pool


def test_remove_strict_not_contained():
    pool = IPv4Pool("192.168.1.0/24")
    with pytest.raises(ValueError):
        pool.remove("192.168.2.0/24", strict=True)


def test_contains_tuple_iprange():
    pool = IPv4Pool("192.168.1.0/24")
    t = (IPv4Address("192.168.1.1"), IPv4Address("192.168.1.10"))
    r = IPv4Range("192.168.1.1", "192.168.1.10")
    assert t in pool
    assert r in pool


def test_contains_list():
    pool = IPv4Pool("192.168.1.0/24")
    assert [IPv4Address("192.168.1.1"), IPv4Address("192.168.1.2")] in pool


def test_contains_wrong_type():
    pool = IPv4Pool("192.168.1.0/24")
    with pytest.raises(TypeError):
        pool.__contains__(object())


def test_copy_and_eq():
    pool = IPv4Pool("192.168.1.0/24")
    pool2 = pool.copy()
    assert pool == pool2
    pool3 = IPv4Pool("192.168.2.0/24")
    assert pool != pool3


def test_iter():
    pool = IPv4Pool("192.168.1.0/24")
    nets = list(iter(pool))
    assert IPv4Network("192.168.1.0/24") in nets


def test_ip_ranges_property():
    pool = IPv4Pool("192.168.1.0/24")
    ip_ranges = pool.ip_ranges
    assert isinstance(ip_ranges[0], IPv4Range)


def test_push_pop_alias():
    pool = IPv4Pool("192.168.1.0/24")
    pool.push("192.168.2.0/24")
    assert IPv4Network("192.168.2.0/24") in pool.networks
    pool.pop("192.168.2.0/24")
    assert IPv4Network("192.168.2.0/24") not in pool.networks


def test_len_repr_str_bool():
    pool = IPv4Pool("192.168.1.0/24")
    assert len(pool) == pool.num_addresses
    assert isinstance(repr(pool), str)
    assert isinstance(str(pool), str)
    assert bool(pool) is True
    pool2 = IPv4Pool()
    assert bool(pool2) is False


def test_ipv6pool_basic():
    pool = IPv6Pool()
    pool.add("2001:db8::/32")
    assert IPv6Network("2001:db8::/32") in pool.networks
    pool2 = pool.copy()
    assert pool == pool2
    pool3 = IPv6Pool("2001:db8:1::/48")
    assert pool != pool3
    pool.push("2001:db8:2::/48")
    # 由于会合并为更大的网段，断言新地址在池中
    assert IPv6Address("2001:db8:2::1") in pool
    pool.pop("2001:db8:2::/48")
    # pop后，2001:db8:2::/48 相关地址不在池中
    assert IPv6Address("2001:db8:2::1") not in pool
    assert isinstance(pool.ip_ranges[0], IPv6Range)


def test_pool_init_various_empty():
    assert isinstance(IPv4Pool(None), IPv4Pool)
    assert isinstance(IPv4Pool([]), IPv4Pool)
    assert isinstance(IPv4Pool(()), IPv4Pool)
    assert isinstance(IPv4Pool(""), IPv4Pool)


def test_format_ip_ranges_invalid_tuple_length():
    pool = IPv4Pool()
    with pytest.raises(TypeError):
        pool._format_ip_ranges([(1, 2, 3)])


def test_format_ip_ranges_invalid_set_dict():
    pool = IPv4Pool()
    # dict 的 key 被当作字符串，最终抛 ValueError
    with pytest.raises(ValueError):
        pool._format_ip_ranges({"a": 1})
    # set 直接抛 TypeError
    with pytest.raises(TypeError):
        pool._format_ip_ranges({IPv4Address("192.168.1.1")})


def test_format_ip_ranges_ipv6range():
    pool = IPv6Pool()
    r = IPv6Range("2001:db8::1", "2001:db8::10")
    result = pool._format_ip_ranges([r])
    assert (r.start, r.end) in result

    with pytest.raises(ValueError):
        pool._format_ip_ranges(["2001:db8::1-xxx"])


def test_intersection_no_overlap():
    pool1 = IPv4Pool("192.168.1.0/24")
    pool2 = IPv4Pool("10.0.0.0/8")
    result = pool1.intersection(pool2)
    assert isinstance(result, IPv4Pool)
    assert len(result.networks) == 0


def test_remove_full_cover():
    pool = IPv4Pool("192.168.1.0/24")
    pool.remove("192.168.1.0/24")
    assert len(pool.networks) == 0


def test_remove_partial():
    pool = IPv4Pool(["192.168.1.0/24", "192.168.2.0/24"])
    pool.remove("192.168.1.0/25")
    assert IPv4Network("192.168.1.128/25") in pool.networks


def test_contains_ipv6():
    pool = IPv6Pool("2001:db8::/48")
    assert IPv6Address("2001:db8::1") in pool
    assert IPv6Network("2001:db8::/48") in pool
    assert (int(IPv6Address("2001:db8::1")),
            int(IPv6Address("2001:db8::10"))) in pool
    assert IPv6Range("2001:db8::1", "2001:db8::10") in pool
    assert [IPv6Address("2001:db8::1")] in pool
    assert IPv6Pool("2001:db8::/48") in pool


def test_contains_invalid_type():
    pool = IPv4Pool("192.168.1.0/24")
    with pytest.raises(TypeError):
        pool.__contains__(set())


def test_eq_with_other_type():
    pool = IPv4Pool("192.168.1.0/24")
    assert pool != "not a pool"


def test_iter_and_len():
    pool = IPv4Pool("192.168.1.0/24")
    nets = list(iter(pool))
    assert len(nets) == 1
    assert len(pool) == pool.num_addresses


def test_repr_str():
    pool = IPv4Pool("192.168.1.0/24")
    assert isinstance(repr(pool), str)
    assert isinstance(str(pool), str)


def test_bool_empty_and_nonempty():
    pool = IPv4Pool()
    assert not bool(pool)
    pool2 = IPv4Pool("192.168.1.0/24")
    assert bool(pool2)


def test_push_pop_alias_methods():
    pool = IPv4Pool("192.168.1.0/24")
    pool.push("192.168.2.0/24")
    assert IPv4Network("192.168.2.0/24") in pool.networks
    pool.pop("192.168.2.0/24")
    assert IPv4Network("192.168.2.0/24") not in pool.networks


def test_ip_ranges_property_empty():
    pool = IPv4Pool()
    assert pool.ip_ranges == []


def test_ipv6pool_properties():
    pool = IPv6Pool("2001:db8::/48")
    assert pool._network_class is IPv6Network
    assert pool._address_class is IPv6Address
    assert pool._iprange_class is IPv6Range
    assert pool._ip_version == 6


def test_ipv4pool_add_operator():
    pool1 = IPv4Pool("192.168.1.0/24")
    pool2 = IPv4Pool("192.168.2.0/24")
    pool3 = pool1 + pool2
    assert isinstance(pool3, IPv4Pool)
    assert IPv4Network("192.168.1.0/24") in pool3.networks
    assert IPv4Network("192.168.2.0/24") in pool3.networks
    # 加法操作不影响原对象
    assert IPv4Network("192.168.2.0/24") not in pool1.networks


def test_ipv6pool_add_operator():
    pool1 = IPv6Pool("2001:db8::/48")
    pool2 = IPv6Pool("2001:db8:1::/48")
    pool3 = pool1 + pool2
    assert isinstance(pool3, IPv6Pool)
    assert IPv6Network("2001:db8::/47") in pool3.networks
    # 加法操作不影响原对象
    assert all(net != IPv6Network("2001:db8:1::/48") for net in pool1.networks)


def test_ipv4pool_from_inputs():
    pool = IPv4Pool.from_inputs(["192.168.1.0/24", "10.0.0.0/8"])
    assert isinstance(pool, IPv4Pool)
    assert IPv4Network("192.168.1.0/24") in pool.networks
    assert IPv4Network("10.0.0.0/8") in pool.networks
    with pytest.raises(ValueError):
        IPv4Pool.from_inputs(["not an ip"])


def test_ipv6pool_from_inputs():
    pool = IPv6Pool.from_inputs(["2001:db8::/48", "2001:db8:1::/48"])
    assert isinstance(pool, IPv6Pool)
    assert IPv6Network("2001:db8::/47") in pool.networks
    with pytest.raises(ValueError):
        IPv6Pool.from_inputs(["not an ipv6"])

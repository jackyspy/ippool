import pytest
from ippool.ipv6 import IPv6Address, IPv6Network


class TestIPv6Address:
    """IPv6地址类的测试用例"""

    def test_ipv6_address_init_with_string(self):
        """测试用字符串初始化IPv6地址"""
        addr1 = IPv6Address("::1")
        assert str(addr1) == "::1"
        assert addr1 == IPv6Address(addr1)

        addr2 = IPv6Address("2001:db8::1")
        assert str(addr2) == "2001:db8::1"

        addr3 = IPv6Address("2001:db8:0:0:0:0:0:1")
        assert str(addr3) == "2001:db8::1"

        addr4 = IPv6Address("::")
        assert str(addr4) == "::"

        addr5 = IPv6Address("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")
        assert str(addr5) == "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"

    def test_ipv6_address_init_with_int(self):
        """测试用整数初始化IPv6地址"""
        addr1 = IPv6Address(1)
        assert str(addr1) == "::1"

        addr2 = IPv6Address(0)
        assert str(addr2) == "::"

        # 测试一个较大的IPv6地址
        large_int = 0x20010db8000000000000000000000001
        addr3 = IPv6Address(large_int)
        assert str(addr3) == "2001:db8::1"

    def test_ipv6_address_init_with_ipv6address(self):
        """测试用IPv6Address对象初始化"""
        addr1 = IPv6Address("::1")
        addr2 = IPv6Address(addr1)
        assert addr1 == addr2
        assert str(addr1) == str(addr2)

    def test_ipv6_address_invalid_inputs(self):
        """测试无效输入"""
        # 无效的字符串格式
        with pytest.raises(ValueError):
            IPv6Address("invalid")

        with pytest.raises(ValueError):
            IPv6Address("2001:db8:invalid")

        # 超出范围的整数值
        with pytest.raises(ValueError):
            IPv6Address(-1)

        with pytest.raises(ValueError):
            IPv6Address(1 << 128)

        # 无效的类型
        with pytest.raises(TypeError):
            IPv6Address([1, 2, 3, 4])

    def test_ipv6_address_equality(self):
        """测试IPv6地址相等性比较"""
        addr1 = IPv6Address("::1")
        addr2 = IPv6Address("::1")
        addr3 = IPv6Address("::2")

        assert addr1 == addr2
        assert addr1 != addr3
        assert addr1 == "::1"
        assert addr1 != "::2"
        assert addr1 == 1
        assert addr1 != 2

    def test_ipv6_address_ordering(self):
        """测试IPv6地址排序"""
        addr1 = IPv6Address("::1")
        addr2 = IPv6Address("::2")
        addr3 = IPv6Address("2001:db8::1")

        assert addr1 < addr2
        assert addr2 > addr1
        assert addr1 <= addr2
        assert addr2 >= addr1
        assert addr1 < addr3
        assert addr3 > addr1

        # 与字符串比较（只测试 < 操作，因为 > 操作会尝试反向比较）
        assert addr1 < "::2"
        assert addr1 < "2001:db8::1"

        # 与整数比较
        assert addr1 < 2
        assert addr1 < 0x20010db8000000000000000000000001
        assert addr2 > 1

    def test_ipv6_address_repr(self):
        """测试IPv6地址的字符串表示"""
        addr = IPv6Address("::1")
        assert repr(addr) == "IPv6Address('::1')"

    def test_ipv6_address_compression(self):
        """测试IPv6地址压缩格式"""
        # 测试不同的压缩格式
        addr1 = IPv6Address("2001:0db8:0000:0000:0000:0000:0000:0001")
        assert str(addr1) == "2001:db8::1"

        addr2 = IPv6Address("2001:db8:0:0:0:0:0:1")
        assert str(addr2) == "2001:db8::1"

        addr3 = IPv6Address("2001:db8::1")
        assert str(addr3) == "2001:db8::1"

        # 测试中间有零的情况
        addr4 = IPv6Address("2001:db8:1:0:0:0:0:1")
        assert str(addr4) == "2001:db8:1::1"

        # 测试末尾有零的情况
        addr5 = IPv6Address("2001:db8:1:0:0:0:0:0")
        assert str(addr5) == "2001:db8:1::"

        # 测试开头有零的情况
        addr6 = IPv6Address("0:0:0:0:0:0:0:1")
        assert str(addr6) == "::1"


class TestIPv6Network:
    """IPv6网络类的测试用例"""

    def test_ipv6_network_init_with_cidr(self):
        """测试用CIDR格式初始化IPv6网络"""
        net1 = IPv6Network("2001:db8::/32")
        assert str(net1.network_address) == "2001:db8::"
        assert str(
            net1.broadcast_address) == "2001:db8:ffff:ffff:ffff:ffff:ffff:ffff"
        assert net1.num_addresses == 2**96

        net2 = IPv6Network("2001:db8::/64")
        assert str(net2.network_address) == "2001:db8::"
        assert str(net2.broadcast_address) == "2001:db8::ffff:ffff:ffff:ffff"
        assert net2.num_addresses == 2**64

        net3 = IPv6Network("2001:db8::/128")
        assert str(net3.network_address) == "2001:db8::"
        assert str(net3.broadcast_address) == "2001:db8::"
        assert net3.num_addresses == 1

    def test_ipv6_network_init_with_single_ip(self):
        """测试用单个IP初始化IPv6网络（/128）"""
        net = IPv6Network("::1")
        assert str(net.network_address) == "::1"
        assert str(net.broadcast_address) == "::1"
        assert net.num_addresses == 1

    def test_ipv6_network_init_with_tuple(self):
        """测试用元组初始化IPv6网络"""
        addr = IPv6Address("2001:db8::")
        net = IPv6Network((addr, 64))
        assert str(net.network_address) == "2001:db8::"
        assert str(net.broadcast_address) == "2001:db8::ffff:ffff:ffff:ffff"
        assert net.num_addresses == 2**64

    def test_ipv6_network_init_with_ipv6network(self):
        """测试用IPv6Network对象初始化"""
        net1 = IPv6Network("2001:db8::/64")
        net2 = IPv6Network(net1)
        assert net1 == net2
        assert str(net1) == str(net2)

    def test_ipv6_network_invalid_inputs(self):
        """测试无效输入"""
        # 无效的掩码位数
        with pytest.raises(ValueError):
            IPv6Network("2001:db8::/129")

        with pytest.raises(ValueError):
            IPv6Network("2001:db8::/-1")

        # 无效的网络格式
        with pytest.raises(TypeError):
            IPv6Network(123)

        with pytest.raises(TypeError):
            IPv6Network([1, 2, 3, 4])

    def test_ipv6_network_network_normalization(self):
        """测试网络地址标准化"""
        # 即使输入的不是网络地址，也应该被标准化为网络地址
        net1 = IPv6Network("2001:db8::1234/64")
        assert str(net1.network_address) == "2001:db8::"
        assert str(net1.broadcast_address) == "2001:db8::ffff:ffff:ffff:ffff"

        net2 = IPv6Network("2001:db8:1:2:3:4:5:6/32")
        assert str(net2.network_address) == "2001:db8::"
        assert str(
            net2.broadcast_address) == "2001:db8:ffff:ffff:ffff:ffff:ffff:ffff"

    def test_ipv6_network_properties(self):
        """测试IPv6网络属性"""
        net = IPv6Network("2001:db8::/64")

        # 网络地址
        assert isinstance(net.network_address, IPv6Address)
        assert str(net.network_address) == "2001:db8::"

        # 广播地址
        assert isinstance(net.broadcast_address, IPv6Address)
        assert str(net.broadcast_address) == "2001:db8::ffff:ffff:ffff:ffff"

        # 地址数量
        assert net.num_addresses == 2**64

    def test_ipv6_network_equality(self):
        """测试IPv6网络相等性"""
        net1 = IPv6Network("2001:db8::/64")
        net2 = IPv6Network("2001:db8::/64")
        net3 = IPv6Network("2001:db8::/65")
        net4 = IPv6Network("2001:db9::/64")

        assert net1 == net2
        assert net1 != net3
        assert net1 != net4

    def test_ipv6_network_ordering(self):
        """测试IPv6网络排序"""
        net1 = IPv6Network("2001:db8::/64")
        net2 = IPv6Network("2001:db8::/65")
        net3 = IPv6Network("2001:db9::/64")

        # 相同网络地址，不同掩码
        assert net1 > net2
        assert net2 < net1

        # 不同网络地址
        assert net1 < net3
        assert net3 > net1

    def test_ipv6_network_subnet_of(self):
        """测试子网关系检查"""
        parent = IPv6Network("2001:db8::/32")
        child1 = IPv6Network("2001:db8::/64")
        child2 = IPv6Network("2001:db8::/96")
        sibling = IPv6Network("2001:db8:1::/64")
        unrelated = IPv6Network("2001:db9::/64")

        # 子网关系
        assert child1.subnet_of(parent)
        assert child2.subnet_of(parent)
        assert child2.subnet_of(child1)

        # 非子网关系
        assert not parent.subnet_of(child1)
        assert not sibling.subnet_of(child1)
        assert not unrelated.subnet_of(parent)

        # 错误类型
        with pytest.raises(TypeError):
            child1.subnet_of("2001:db8::/32")

    def test_ipv6_network_str_repr(self):
        """测试IPv6网络的字符串表示"""
        net = IPv6Network("2001:db8::/64")
        assert str(net) == "2001:db8::/64"
        assert repr(net) == "IPv6Network('2001:db8::/64')'"

    def test_ipv6_network_edge_cases(self):
        """测试边界情况"""
        # /0 网络
        net1 = IPv6Network("::/0")
        assert str(net1.network_address) == "::"
        assert str(net1.broadcast_address
                   ) == "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"
        assert net1.num_addresses == 2**128

        # /128 网络
        net2 = IPv6Network("::1/128")
        assert str(net2.network_address) == "::1"
        assert str(net2.broadcast_address) == "::1"
        assert net2.num_addresses == 1

        # /127 网络（只有两个地址）
        net3 = IPv6Network("2001:db8::/127")
        assert str(net3.network_address) == "2001:db8::"
        assert str(net3.broadcast_address) == "2001:db8::1"
        assert net3.num_addresses == 2

    def test_ipv6_network_common_prefixes(self):
        """测试常见的IPv6网络前缀"""
        # 链路本地地址
        net1 = IPv6Network("fe80::/10")
        assert str(net1.network_address) == "fe80::"
        assert str(net1.broadcast_address
                   ) == "febf:ffff:ffff:ffff:ffff:ffff:ffff:ffff"

        # 唯一本地地址
        net2 = IPv6Network("fc00::/7")
        assert str(net2.network_address) == "fc00::"
        assert str(net2.broadcast_address
                   ) == "fdff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"

        # 多播地址
        net3 = IPv6Network("ff00::/8")
        assert str(net3.network_address) == "ff00::"
        assert str(net3.broadcast_address
                   ) == "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"

    def test_ipv6_network_large_numbers(self):
        """测试大数值的IPv6网络"""
        # 测试非常大的网络
        net1 = IPv6Network("2001:db8::/16")
        assert net1.num_addresses == 2**112

        net2 = IPv6Network("2001:db8::/8")
        assert net2.num_addresses == 2**120

        # 测试非常小的网络
        net3 = IPv6Network("2001:db8::/126")
        assert net3.num_addresses == 4

        net4 = IPv6Network("2001:db8::/125")
        assert net4.num_addresses == 8


def test_ipv6address_invalid_type():
    with pytest.raises(TypeError):
        IPv6Address([1, 2, 3])
    with pytest.raises(TypeError):
        IPv6Address({'a': 1})


def test_ipv6network_eq_invalid_type():
    net = IPv6Network('2001:db8::/64')
    with pytest.raises(TypeError):
        net == 'not a network'


def test_ipv6network_lt_invalid_type():
    net = IPv6Network('2001:db8::/64')
    with pytest.raises(TypeError):
        net < 'not a network'


def test_ipv6network_le_and_ge():
    net1 = IPv6Network('2001:db8::/64')
    net2 = IPv6Network('2001:db8::/65')
    assert (net2 <= net1) is True
    assert (net1 >= net2) is True
    assert (net1 <= net1) is True
    assert (net1 >= net1) is True


def test_hash_ipv6address():
    v1 = IPv6Address('2001:db8::1')
    v2 = IPv6Address('2001:db8::1')
    v3 = IPv6Address('2001:db8::2')
    assert hash(v1) == hash(v2)
    assert hash(v1) != hash(v3)
    s = set([v1, v2, v3])
    assert len(s) == 2

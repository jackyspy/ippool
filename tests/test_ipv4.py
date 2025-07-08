import pytest
from ippool.ipv4 import IPv4Address, IPv4Network


class TestIPv4Address:
    """IPv4地址类的测试用例"""

    def test_ipv4_address_init_with_string(self):
        """测试用字符串初始化IPv4地址"""
        addr1 = IPv4Address("192.168.1.1")
        assert int(addr1) == 3232235777
        assert str(addr1) == "192.168.1.1"
        assert addr1 == IPv4Address(addr1)

        addr2 = IPv4Address("0.0.0.0")
        assert int(addr2) == 0
        assert str(addr2) == "0.0.0.0"

        addr3 = IPv4Address("255.255.255.255")
        assert int(addr3) == 4294967295
        assert str(addr3) == "255.255.255.255"

    def test_ipv4_address_init_with_int(self):
        """测试用整数初始化IPv4地址"""
        addr1 = IPv4Address(3232235777)
        assert str(addr1) == "192.168.1.1"

        addr2 = IPv4Address(0)
        assert str(addr2) == "0.0.0.0"

        addr3 = IPv4Address(4294967295)
        assert str(addr3) == "255.255.255.255"

    def test_ipv4_address_init_with_ipv4address(self):
        """测试用IPv4Address对象初始化"""
        addr1 = IPv4Address("192.168.1.1")
        addr2 = IPv4Address(addr1)
        assert addr1 == addr2
        assert str(addr1) == str(addr2)

    def test_ipv4_address_invalid_inputs(self):
        """测试无效输入"""
        # 无效的字符串格式
        with pytest.raises(ValueError):
            IPv4Address("invalid")

        with pytest.raises(ValueError):
            IPv4Address("256.256.256.256")

        # 超出范围的整数值
        with pytest.raises(ValueError):
            IPv4Address(-1)

        with pytest.raises(ValueError):
            IPv4Address(4294967296)

        # 无效的类型
        with pytest.raises(TypeError):
            IPv4Address([1, 2, 3, 4])

    def test_ipv4_address_equality(self):
        """测试IPv4地址相等性比较"""
        addr1 = IPv4Address("192.168.1.1")
        addr2 = IPv4Address("192.168.1.1")
        addr3 = IPv4Address("192.168.1.2")

        assert addr1 == addr2
        assert addr1 != addr3
        assert addr1 == "192.168.1.1"
        assert addr1 != "192.168.1.2"
        assert addr1 == 3232235777
        assert addr1 != 3232235778

    def test_ipv4_address_ordering(self):
        """测试IPv4地址排序"""
        addr1 = IPv4Address("192.168.1.1")
        addr2 = IPv4Address("192.168.1.2")
        addr3 = IPv4Address("192.168.2.1")

        assert addr1 < addr2
        assert addr2 > addr1
        assert addr1 <= addr2
        assert addr2 >= addr1
        assert addr1 < addr3
        assert addr3 > addr1

        # 与字符串比较（只测试 < 操作，因为 > 操作会尝试反向比较）
        assert addr1 < "192.168.1.2"
        assert addr1 < "192.168.2.1"

        # 与整数比较
        assert addr1 < 3232235778
        assert addr1 < 3232236033
        assert addr2 > 3232235777

    def test_ipv4_address_repr(self):
        """测试IPv4地址的字符串表示"""
        addr = IPv4Address("192.168.1.1")
        assert repr(addr) == "IPv4Address('192.168.1.1')"


class TestIPv4Network:
    """IPv4网络类的测试用例"""

    def test_ipv4_network_init_with_cidr(self):
        """测试用CIDR格式初始化IPv4网络"""
        net1 = IPv4Network("192.168.1.0/24")
        assert str(net1.network_address) == "192.168.1.0"
        assert str(net1.broadcast_address) == "192.168.1.255"
        assert net1.num_addresses == 256

        net2 = IPv4Network("10.0.0.0/8")
        assert str(net2.network_address) == "10.0.0.0"
        assert str(net2.broadcast_address) == "10.255.255.255"
        assert net2.num_addresses == 16777216

        net3 = IPv4Network("172.16.0.0/16")
        assert str(net3.network_address) == "172.16.0.0"
        assert str(net3.broadcast_address) == "172.16.255.255"
        assert net3.num_addresses == 65536

    def test_ipv4_network_init_with_single_ip(self):
        """测试用单个IP初始化IPv4网络（/32）"""
        net = IPv4Network("192.168.1.1")
        assert str(net.network_address) == "192.168.1.1"
        assert str(net.broadcast_address) == "192.168.1.1"
        assert net.num_addresses == 1

    def test_ipv4_network_init_with_tuple(self):
        """测试用元组初始化IPv4网络"""
        addr = IPv4Address("192.168.1.0")
        net = IPv4Network((addr, 24))
        assert str(net.network_address) == "192.168.1.0"
        assert str(net.broadcast_address) == "192.168.1.255"
        assert net.num_addresses == 256

    def test_ipv4_network_init_with_ipv4network(self):
        """测试用IPv4Network对象初始化"""
        net1 = IPv4Network("192.168.1.0/24")
        net2 = IPv4Network(net1)
        assert net1 == net2
        assert str(net1) == str(net2)

    def test_ipv4_network_invalid_inputs(self):
        """测试无效输入"""
        # 无效的掩码位数
        with pytest.raises(ValueError):
            IPv4Network("192.168.1.0/33")

        with pytest.raises(ValueError):
            IPv4Network("192.168.1.0/-1")

        # 无效的网络格式
        with pytest.raises(TypeError):
            IPv4Network(123)

        with pytest.raises(TypeError):
            IPv4Network([1, 2, 3, 4])

    def test_ipv4_network_network_normalization(self):
        """测试网络地址标准化"""
        # 即使输入的不是网络地址，也应该被标准化为网络地址
        net1 = IPv4Network("192.168.1.15/24")
        assert str(net1.network_address) == "192.168.1.0"
        assert str(net1.broadcast_address) == "192.168.1.255"

        net2 = IPv4Network("10.0.0.100/8")
        assert str(net2.network_address) == "10.0.0.0"
        assert str(net2.broadcast_address) == "10.255.255.255"

    def test_ipv4_network_properties(self):
        """测试IPv4网络属性"""
        net = IPv4Network("192.168.1.0/24")

        # 网络地址
        assert isinstance(net.network_address, IPv4Address)
        assert str(net.network_address) == "192.168.1.0"

        # 广播地址
        assert isinstance(net.broadcast_address, IPv4Address)
        assert str(net.broadcast_address) == "192.168.1.255"

        # 地址数量
        assert net.num_addresses == 256

    def test_ipv4_network_equality(self):
        """测试IPv4网络相等性"""
        net1 = IPv4Network("192.168.1.0/24")
        net2 = IPv4Network("192.168.1.0/24")
        net3 = IPv4Network("192.168.1.0/25")
        net4 = IPv4Network("192.168.2.0/24")

        assert net1 == net2
        assert net1 != net3
        assert net1 != net4

    def test_ipv4_network_ordering(self):
        """测试IPv4网络排序"""
        net1 = IPv4Network("192.168.1.0/24")
        net2 = IPv4Network("192.168.1.0/25")
        net3 = IPv4Network("192.168.2.0/24")

        # 相同网络地址，不同掩码
        assert net1 > net2
        assert net2 < net1

        # 不同网络地址
        assert net1 < net3
        assert net3 > net1

    def test_ipv4_network_subnet_of(self):
        """测试子网关系检查"""
        parent = IPv4Network("192.168.0.0/16")
        child1 = IPv4Network("192.168.1.0/24")
        child2 = IPv4Network("192.168.1.0/25")
        sibling = IPv4Network("192.168.2.0/24")
        unrelated = IPv4Network("10.0.0.0/8")

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
            child1.subnet_of("192.168.0.0/16")

    def test_ipv4_network_str_repr(self):
        """测试IPv4网络的字符串表示"""
        net = IPv4Network("192.168.1.0/24")
        assert str(net) == "192.168.1.0/24"
        assert repr(net) == "IPv4Network('192.168.1.0/24')'"

    def test_ipv4_network_edge_cases(self):
        """测试边界情况"""
        # /0 网络
        net1 = IPv4Network("0.0.0.0/0")
        assert str(net1.network_address) == "0.0.0.0"
        assert str(net1.broadcast_address) == "255.255.255.255"
        assert net1.num_addresses == 4294967296

        # /32 网络
        net2 = IPv4Network("192.168.1.1/32")
        assert str(net2.network_address) == "192.168.1.1"
        assert str(net2.broadcast_address) == "192.168.1.1"
        assert net2.num_addresses == 1

        # /31 网络（只有两个地址）
        net3 = IPv4Network("192.168.1.0/31")
        assert str(net3.network_address) == "192.168.1.0"
        assert str(net3.broadcast_address) == "192.168.1.1"
        assert net3.num_addresses == 2


def test_ipv4address_invalid_type():
    with pytest.raises(TypeError):
        IPv4Address([1, 2, 3])
    with pytest.raises(TypeError):
        IPv4Address({'a': 1})


def test_ipv4network_eq_invalid_type():
    net = IPv4Network('192.168.1.0/24')
    with pytest.raises(TypeError):
        net == 'not a network'


def test_ipv4network_lt_invalid_type():
    net = IPv4Network('192.168.1.0/24')
    with pytest.raises(TypeError):
        net < 'not a network'


def test_ipv4network_le_and_ge():
    net1 = IPv4Network('192.168.1.0/24')
    net2 = IPv4Network('192.168.1.0/25')
    assert (net2 < net1) is True
    assert (net2 <= net1) is True
    assert (net1 >= net2) is True
    assert (net1 <= net1) is True
    assert (net1 >= net1) is True


def test_hash_ipv4address():
    a1 = IPv4Address('192.168.1.1')
    a2 = IPv4Address('192.168.1.1')
    a3 = IPv4Address('192.168.1.2')
    assert hash(a1) == hash(a2)
    assert hash(a1) != hash(a3)
    s = set([a1, a2, a3])
    assert len(s) == 2

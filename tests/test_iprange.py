import pytest
from ippool.iprange import IPv4Range, IPv6Range
from ippool.ipv4 import IPv4Address, IPv4Network
from ippool.ipv6 import IPv6Address, IPv6Network


# Test cases for IPv4Range
def test_ipv4_range_init_basic():
    r1 = IPv4Range("192.168.1.1", "192.168.1.10")
    assert str(r1.start) == "192.168.1.1"
    assert str(r1.end) == "192.168.1.10"
    assert str(r1) == "192.168.1.1-192.168.1.10"
    assert repr(r1) == 'IPv4Range("192.168.1.1","192.168.1.10")'
    assert len(r1) == 10

    r2 = IPv4Range("192.168.1.0/24")
    assert str(r2.start) == "192.168.1.0"
    assert str(r2.end) == "192.168.1.255"

    r3 = IPv4Range("192.168.1.1-192.168.1.10")
    assert str(r3.start) == "192.168.1.1"
    assert str(r3.end) == "192.168.1.10"

    assert str(IPv4Range("192.168.1.1")) == "192.168.1.1"

    # start/end 为同一个地址
    r4 = IPv4Range("192.168.1.5", "192.168.1.5")
    assert str(r4.start) == "192.168.1.5"
    assert str(r4.end) == "192.168.1.5"
    assert str(r4) == "192.168.1.5"

    # 极限区间
    r5 = IPv4Range("0.0.0.0", "255.255.255.255")
    assert str(r5.start) == "0.0.0.0"
    assert str(r5.end) == "255.255.255.255"

    # 新增：192.168.1.100-200 区间
    r6 = IPv4Range("192.168.1.100-200")
    assert str(r6.start) == "192.168.1.100"
    assert str(r6.end) == "192.168.1.200"


def test_ipv6_range_init_basic():
    # 测试IPv6Range的基本初始化和属性
    r1 = IPv6Range("2001:db8::1-2001:db8::10")
    assert str(r1.start) == "2001:db8::1"
    assert str(r1.end) == "2001:db8::10"
    assert str(r1) == "2001:db8::1-2001:db8::10"
    assert repr(r1) == 'IPv6Range("2001:db8::1","2001:db8::10")'
    assert len(r1) == 16

    # 测试CIDR格式
    r2 = IPv6Range("2001:db8::/126")
    assert str(r2.start) == "2001:db8::"
    assert str(r2.end) == "2001:db8::3"

    # 测试单个IPv6地址
    r3 = IPv6Range("2001:db8::5")
    assert str(r3.start) == "2001:db8::5"
    assert str(r3.end) == "2001:db8::5"
    assert str(r3) == "2001:db8::5"

    # start/end 为同一个地址
    r4 = IPv6Range("2001:db8::a", "2001:db8::a")
    assert str(r4.start) == "2001:db8::a"
    assert str(r4.end) == "2001:db8::a"
    assert str(r4) == "2001:db8::a"

    # 极限区间
    r5 = IPv6Range("::", "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")
    assert str(r5.start) == "::"
    assert str(r5.end) == "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"


def test_ipv4_range_init_single_types():
    # 单个整数
    r = IPv4Range(int(IPv4Address("192.168.1.5")))
    assert str(r.start) == "192.168.1.5"
    assert str(r.end) == "192.168.1.5"

    # 单个 IPv4Address
    r = IPv4Range(IPv4Address("192.168.1.6"))
    assert str(r.start) == "192.168.1.6"
    assert str(r.end) == "192.168.1.6"

    # 直接传入 IPv4Range
    r0 = IPv4Range("192.168.1.1", "192.168.1.10")
    r = IPv4Range(r0)
    assert str(r.start) == "192.168.1.1"
    assert str(r.end) == "192.168.1.10"


def test_ipv4_range_init_tuple_types():
    # tuple (str, str)
    r = IPv4Range(("192.168.1.7", "192.168.1.8"))
    assert str(r.start) == "192.168.1.7"
    assert str(r.end) == "192.168.1.8"

    # tuple (int, int)
    r = IPv4Range(
        (int(IPv4Address("192.168.1.9")), int(IPv4Address("192.168.1.10"))))
    assert str(r.start) == "192.168.1.9"
    assert str(r.end) == "192.168.1.10"

    # tuple (IPv4Address, IPv4Address)
    r = IPv4Range((IPv4Address("192.168.1.11"), IPv4Address("192.168.1.12")))
    assert str(r.start) == "192.168.1.11"
    assert str(r.end) == "192.168.1.12"

    # list (str, str)
    r = IPv4Range(["192.168.1.7", "192.168.1.8"])
    assert str(r.start) == "192.168.1.7"
    assert str(r.end) == "192.168.1.8"


def test_ipv4_range_init_errors():
    # 无意义字符串
    with pytest.raises(TypeError):
        IPv4Range("not an ip")
    # 错误格式 '192.168.1.1-xxx'
    with pytest.raises(ValueError):
        IPv4Range("192.168.1.1-xxx")
    # 错误类型
    with pytest.raises(TypeError) as excinfo:
        _ = IPv4Range({})
    assert "Invalid type" in str(excinfo.value)
    # tuple 长度不为2
    with pytest.raises(TypeError):
        IPv4Range(("192.168.1.1", ))
    with pytest.raises(TypeError):
        IPv4Range(("192.168.1.1", "192.168.1.2", "192.168.1.3"))
    # start/end 为 None
    with pytest.raises(TypeError):
        IPv4Range(None, "192.168.1.1")


def test_ipv4_range_contains():
    r = IPv4Range("192.168.1.1", "192.168.1.10")
    assert IPv4Address("192.168.1.5") in r
    assert "192.168.1.1" in r
    assert "192.168.1.10" in r
    assert IPv4Address("192.168.1.0") not in r
    assert IPv4Address("192.168.1.11") not in r
    assert "192.168.2.1" not in r


def test_ipv4_range_and():
    r1 = IPv4Range("192.168.1.1", "192.168.1.10")
    r2 = IPv4Range("192.168.1.5", "192.168.1.15")
    intersection = r1 & r2
    assert str(intersection.start) == "192.168.1.5"
    assert str(intersection.end) == "192.168.1.10"

    r3 = IPv4Range("192.168.2.1", "192.168.2.10")
    intersection_none = r1 & r3
    assert intersection_none is None


def test_ipv4_range_add():
    r1 = IPv4Range("192.168.1.1", "192.168.1.7")
    r2 = IPv4Range("192.168.1.4", "192.168.1.10")
    combined = r1 + r2
    assert str(combined.start) == "192.168.1.1"
    assert str(combined.end) == "192.168.1.10"

    r3 = IPv4Range("192.168.1.12", "192.168.1.15")
    combined_list = r1 + r3
    assert len(combined_list) == 2
    assert str(combined_list[0].start) == "192.168.1.1"
    assert str(combined_list[0].end) == "192.168.1.7"
    assert str(combined_list[1].start) == "192.168.1.12"
    assert str(combined_list[1].end) == "192.168.1.15"


def test_ipv4_range_sub():
    r1 = IPv4Range("192.168.1.0", "192.168.1.255")
    r2 = IPv4Range("192.168.1.10", "192.168.1.20")
    result = r1 - r2
    assert len(result) == 2
    assert str(result[0].start) == "192.168.1.0"
    assert str(result[0].end) == "192.168.1.9"
    assert str(result[1].start) == "192.168.1.21"
    assert str(result[1].end) == "192.168.1.255"

    # 检查被减区间在前端重叠
    r3 = IPv4Range("192.168.1.0", "192.168.1.5")
    result2 = r1 - r3
    assert isinstance(result2, IPv4Range)
    assert str(result2.start) == "192.168.1.6"
    assert str(result2.end) == "192.168.1.255"

    # 检查被减区间在尾端重叠
    r4 = IPv4Range("192.168.1.250", "192.168.1.255")
    result3 = r1 - r4
    assert str(result3.start) == "192.168.1.0"
    assert str(result3.end) == "192.168.1.249"

    # 检查被减区间完全不重叠
    r5 = IPv4Range("192.168.2.0", "192.168.2.255")
    result4 = r1 - r5
    assert result4 == r1

    # 检查被减区间完全覆盖
    r6 = IPv4Range("192.168.0.0", "192.168.2.0")
    result5 = r1 - r6
    assert result5 is None


def test_ipv4_range_getitem():
    r = IPv4Range("192.168.1.1", "192.168.1.10")
    assert r[0] == r.start
    assert r[1] == r.end
    with pytest.raises(IndexError):
        _ = r[2]


# Test cases for IPv6Range (basic)
def test_ipv6_range_init():
    r1 = IPv6Range("::1", "::10")
    assert str(r1.start) == "::1"
    assert str(r1.end) == "::10"

    r2 = IPv6Range("2001:db8::/32")
    assert str(r2.start) == "2001:db8::"
    assert str(r2.end) == "2001:db8:ffff:ffff:ffff:ffff:ffff:ffff"


def test_ipv6_range_getitem():
    r = IPv6Range("::1", "::10")
    assert r[0] == r.start
    assert r[1] == r.end
    with pytest.raises(IndexError):
        _ = r[2]


def test_ipv4_range_invalid_start():
    with pytest.raises(ValueError):
        IPv4Range("invalid", "192.168.1.10")


def test_ipv4_range_invalid_end():
    with pytest.raises(ValueError):
        IPv4Range("192.168.1.1", "invalid")


def test_ipv4_range_start_after_end():
    with pytest.raises(ValueError):
        IPv4Range("192.168.1.10", "192.168.1.1")


def test_ipv6_range_invalid_start():
    with pytest.raises(ValueError):
        IPv6Range("invalid", "2001:db8::10")


def test_ipv6_range_invalid_end():
    with pytest.raises(ValueError):
        IPv6Range("2001:db8::1", "invalid")


def test_ipv6_range_start_after_end():
    with pytest.raises(ValueError):
        IPv6Range("2001:db8::10", "2001:db8::1")


def test_ipv4_range_contains_network():
    iprange = IPv4Range("192.168.1.1", "192.168.1.10")
    with pytest.raises(TypeError):
        IPv4Network("192.168.1.0/24") in iprange


def test_ipv4_range_contains_network_not_contained():
    iprange = IPv4Range("192.168.1.1", "192.168.1.10")
    with pytest.raises(TypeError):
        IPv4Network("192.168.2.0/24") in iprange


def test_ipv6_range_contains_network():
    iprange = IPv6Range("2001:db8::1", "2001:db8::10")
    with pytest.raises(TypeError):
        IPv6Network("2001:db8::/48") in iprange


def test_ipv6_range_contains_network_not_contained():
    iprange = IPv6Range("2001:db8::1", "2001:db8::10")
    with pytest.raises(TypeError):
        IPv6Network("2001:db9::/48") in iprange


def test_ipv4_range_contains_invalid_type():
    iprange = IPv4Range("192.168.1.1", "192.168.1.10")
    with pytest.raises(TypeError):
        IPv4Network("192.168.1.0/24") in iprange


def test_ipv6_range_contains_invalid_type():
    iprange = IPv6Range("2001:db8::1", "2001:db8::10")
    with pytest.raises(TypeError):
        IPv6Network("2001:db8::/48") in iprange


def test_ipv4_range_eq_different_type():
    iprange = IPv4Range("192.168.1.1", "192.168.1.10")
    assert iprange != "not a range"


def test_ipv6_range_eq_different_type():
    iprange = IPv6Range("2001:db8::1", "2001:db8::10")
    assert iprange != "not a range"


def test_ipv4_range_hash():
    pass


def test_ipv6_range_hash():
    pass


def test_hash_iprange():
    # IPv4Range hash
    r1 = IPv4Range('192.168.1.1', '192.168.1.10')
    r2 = IPv4Range('192.168.1.1', '192.168.1.10')
    r3 = IPv4Range('192.168.1.2', '192.168.1.10')
    assert hash(r1) == hash(r2)
    assert hash(r1) != hash(r3)
    s = set([r1, r2, r3])
    assert len(s) == 2

    # IPv6Range hash
    rr1 = IPv6Range('2001:db8::1', '2001:db8::10')
    rr2 = IPv6Range('2001:db8::1', '2001:db8::10')
    rr3 = IPv6Range('2001:db8::2', '2001:db8::10')
    assert hash(rr1) == hash(rr2)
    assert hash(rr1) != hash(rr3)
    s = set([rr1, rr2, rr3])
    assert len(s) == 2


def test_ipv4range_str_int_init():
    # start, end 都为 str
    r = IPv4Range("192.168.1.1", "192.168.1.10")
    assert str(r.start) == "192.168.1.1"
    assert str(r.end) == "192.168.1.10"
    # start, end 都为 int
    r2 = IPv4Range(int(IPv4Address("192.168.1.1")),
                   int(IPv4Address("192.168.1.10")))
    assert str(r2.start) == "192.168.1.1"
    assert str(r2.end) == "192.168.1.10"


def test_ipv4range_contains_int_str_typeerror():
    r = IPv4Range("192.168.1.1", "192.168.1.10")
    # int
    assert int(IPv4Address("192.168.1.5")) in r
    # str
    assert "192.168.1.5" in r
    # 错误类型

    with pytest.raises(TypeError):
        [1, 2, 3] in r


def test_ipv4range_and_with_network_and_typeerror():
    r = IPv4Range("192.168.1.1", "192.168.1.10")
    net = IPv4Network("192.168.1.0/24")
    # 与 network 取交集
    result = r & net
    assert isinstance(result, IPv4Range)
    # 错误类型

    with pytest.raises(TypeError):
        r & 123


def test_ipv4range_add_with_network_and_typeerror():
    r = IPv4Range("192.168.1.1", "192.168.1.10")
    net = IPv4Network("192.168.1.0/24")
    # 与 network 合并
    result = r + net
    assert isinstance(result, IPv4Range)
    # 错误类型

    with pytest.raises(TypeError):
        r + 123


def test_ipv4range_sub_with_network_and_typeerror():
    r = IPv4Range("192.168.1.1", "192.168.1.10")
    net = IPv4Network("192.168.1.0/24")
    # 与 network 相减
    result = r - net
    # net 覆盖 r，结果应为 None
    assert result is None
    # 错误类型

    with pytest.raises(TypeError):
        r - 123


def test_ipv4range_sub_no_overlap():
    r1 = IPv4Range("192.168.1.1", "192.168.1.10")
    r2 = IPv4Range("192.168.2.1", "192.168.2.10")
    result = r1 - r2
    assert result == r1


def test_ipv4range_sub_full_cover():
    r1 = IPv4Range("192.168.1.1", "192.168.1.10")
    r2 = IPv4Range("192.168.1.0", "192.168.1.255")
    result = r1 - r2
    assert result is None


def test_ipv4range_sub_middle_split():
    r1 = IPv4Range("192.168.1.1", "192.168.1.10")
    r2 = IPv4Range("192.168.1.3", "192.168.1.7")
    result = r1 - r2
    assert isinstance(result, list)
    assert str(result[0].start) == "192.168.1.1"
    assert str(result[0].end) == "192.168.1.2"
    assert str(result[1].start) == "192.168.1.8"
    assert str(result[1].end) == "192.168.1.10"


def test_ipv4range_sub_left_cover_newstart_gt_end():
    r1 = IPv4Range("192.168.1.1", "192.168.1.10")
    r2 = IPv4Range("192.168.1.0", "192.168.1.15")
    # left cover, new_start > self.end
    result = r1 - r2
    assert result is None


def test_ipv4range_sub_right_cover_newend_lt_start():
    r1 = IPv4Range("192.168.1.1", "192.168.1.10")
    r2 = IPv4Range("192.168.1.0", "192.168.1.0")
    # right cover, new_end < self.start
    result = r1 - r2
    assert result == r1


def test_ipv4range_invalid_ip_range_int():
    # int 形式，start > end

    with pytest.raises(ValueError):
        IPv4Range(int(IPv4Address("192.168.1.10")),
                  int(IPv4Address("192.168.1.1")))


def test_ipv4range_sub_no_overlap_left():
    # other 在 self 左侧完全不重叠
    r1 = IPv4Range("192.168.1.10", "192.168.1.20")
    r2 = IPv4Range("192.168.1.0", "192.168.1.5")
    result = r1 - r2
    assert result == r1


def test_ipv4range_sub_no_overlap_right():
    # other 在 self 右侧完全不重叠
    r1 = IPv4Range("192.168.1.10", "192.168.1.20")
    r2 = IPv4Range("192.168.1.25", "192.168.1.30")
    result = r1 - r2
    assert result == r1


def test_ipv4range_sub_left_cover_newstart_eq_end():
    # left cover, new_start == self.end
    r1 = IPv4Range("192.168.1.10", "192.168.1.20")
    r2 = IPv4Range("192.168.1.0", "192.168.1.19")
    result = r1 - r2
    assert isinstance(result, IPv4Range)
    assert str(result.start) == "192.168.1.20"
    assert str(result.end) == "192.168.1.20"


def test_ipv4range_sub_right_cover_newend_eq_start():
    # right cover, new_end == self.start
    r1 = IPv4Range("192.168.1.10", "192.168.1.20")
    r2 = IPv4Range("192.168.1.20", "192.168.1.30")
    result = r1 - r2
    assert isinstance(result, IPv4Range)
    assert str(result.start) == "192.168.1.10"
    assert str(result.end) == "192.168.1.19"


def test_ipv4range_sub_right_cover_newend_lt_start():
    # right cover, new_end < self.start，返回 None
    r1 = IPv4Range("192.168.1.10", "192.168.1.20")
    r2 = IPv4Range("192.168.1.0", "192.168.1.9")
    result = r1 - r2
    assert result == r1


def test_ipv4range_lt():
    r1 = IPv4Range("192.168.1.1", "192.168.1.10")
    r2 = IPv4Range("192.168.1.5", "192.168.1.20")
    r3 = IPv4Range("192.168.1.1", "192.168.1.10")
    assert (r1 < r2) is True
    assert (r2 < r1) is False
    assert (r1 < r3) is False


def test_ipv4range_lt_typeerror():
    r1 = IPv4Range("192.168.1.1", "192.168.1.10")
    with pytest.raises(TypeError):
        r1 < "not a range"
    with pytest.raises(TypeError):
        r1 < 123
    with pytest.raises(TypeError):
        r1 < None


def test_ipv4range_from_input():
    r = IPv4Range.from_input("192.168.1.1-192.168.1.10")
    assert isinstance(r, IPv4Range)
    assert str(r.start) == "192.168.1.1"
    assert str(r.end) == "192.168.1.10"
    # 异常用例
    with pytest.raises(ValueError):
        IPv4Range.from_input("not-an-ip")
    with pytest.raises(ValueError):
        IPv4Range.from_input({})


def test_ipv6range_from_input():
    r = IPv6Range.from_input("2001:db8::1-2001:db8::10")
    assert isinstance(r, IPv6Range)
    assert str(r.start) == "2001:db8::1"
    assert str(r.end) == "2001:db8::10"
    # 异常用例
    with pytest.raises(ValueError):
        IPv6Range.from_input("not-an-ipv6")
    with pytest.raises(ValueError):
        IPv6Range.from_input({})

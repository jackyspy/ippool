# -*- coding: utf-8 -*-
# Created by jackyspy at 2020/3/12
from functools import total_ordering

from .ipv4 import IPv4Address, IPv4Network
from .ipv6 import IPv6Address, IPv6Network


@total_ordering
class _IPRangeBase:
    """
    管理IP地址段的基类。

    参数:
        start (str | int | IPv4Address | IPv6Address | IPv4Network | IPv6Network):
            IP地址段的起始地址，可以为字符串、整数、IP地址对象或网络对象。
            - 如果为字符串，支持单个IP、IP段（如"192.168.1.1-192.168.1.10"）、或CIDR格式（如"192.168.1.0/24"）。
            - 如果为整数，表示IP地址的整数表示。
            - 如果为IP地址对象（IPv4Address/IPv6Address），则end也必须为同类型。
            - 如果为网络对象（IPv4Network/IPv6Network），则自动取其network_address和broadcast_address。

        end (str | int | IPv4Address | IPv6Address, 可选):
            IP地址段的结束地址。仅在start为单个IP或整数时需要指定。

    属性:
        start (IPv4Address | IPv6Address): IP地址段的起始地址（包含）。
        end   (IPv4Address | IPv6Address): IP地址段的结束地址（包含）。

    说明:
        start和end表示一个闭区间的地址段。
    """

    __slots__ = ("start", "end")

    def __init__(
        self,
        start:
        "str | int | IPv4Address | IPv6Address | IPv4Network | IPv6Network | tuple | _IPRangeBase",
        end: "str | int | IPv4Address | IPv6Address" = None,
    ):
        cls_address = self._address_class
        cls_network = self._network_class
        cls_range = self.__class__

        # 优先判断end is None，分组处理
        if end is None:
            if isinstance(start, str):
                if '-' in start:
                    start_str, _, end_str = start.partition('-')
                    start_addr = cls_address(start_str)
                    # IPv4 支持 '192.168.1.1-10' 形式
                    if cls_network == IPv4Network:
                        if '.' in end_str:
                            end_addr = cls_address(end_str)
                        else:
                            if not (end_str.isdigit()
                                    and 0 <= int(end_str) <= 255):
                                raise ValueError(
                                    f"Invalid IP address in range: {start}")

                            end_addr = cls_address((int(start_addr)
                                                    & 0xFFFFFF00)
                                                   | int(end_str))

                    else:  # IPv6 必须完整写出
                        end_addr = cls_address(end_str)

                    self.start = start_addr
                    self.end = end_addr
                else:
                    # 普通网络字符串或单IP
                    try:
                        net = cls_network(start)
                        self.start = net.network_address
                        self.end = net.broadcast_address
                    except Exception:
                        raise TypeError(f"Invalid type: {type(start)}")

            elif isinstance(start, cls_network):
                self.start = start.network_address
                self.end = start.broadcast_address

            elif isinstance(start, _IPRangeBase):
                self.start = start.start
                self.end = start.end

            elif isinstance(start, (tuple, list)) and len(start) == 2:
                self.start, self.end = map(cls_address, start)

            elif isinstance(start, cls_address):
                self.start = self.end = start

            elif isinstance(start, int):
                self.start = self.end = cls_address(start)

            else:
                raise TypeError(f"Invalid type: {type(start)}")
        else:
            self.start = cls_address(start)
            self.end = cls_address(end)

        if self.start > self.end:
            raise ValueError("Invalid ip range")

    def __contains__(self, item):
        # 检查item是否在闭区间[start, end]内
        if isinstance(item, (str, int)):
            item = self._address_class(item)
        elif not isinstance(item, self._address_class):
            raise TypeError("item类型错误，不是正确的IP地址类型")

        return self.start <= item <= self.end

    def __and__(self, other):
        # 计算两个闭区间的交集
        cls = self.__class__
        if isinstance(other, self._network_class):
            other = cls(other)
        elif not isinstance(other, cls):
            raise TypeError(
                f"Unsupported operand type(s) for &: '{type(self)}' and '{type(other)}'"
            )

        r1, r2 = sorted([self, other])

        # 闭区间无交集
        if r2.start > r1.end:
            return None

        return cls(r2.start, min(r1.end, r2.end))

    def __add__(self, other):
        # 合并两个闭区间，如果相邻或有重叠则合并，否则返回两个区间
        cls = self.__class__
        if isinstance(other, self._network_class):
            other = cls(other)
        elif not isinstance(other, cls):
            raise TypeError(
                f"Unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'"
            )

        r1, r2 = sorted([self, other])

        # 检查是否可以合并（闭区间：r2.start <= r1.end + 1）
        if int(r2.start) > int(r1.end) + 1:
            return [r1, r2]

        return cls(r1.start, max(r1.end, r2.end))

    def __sub__(self, other):
        # 从当前闭区间中减去另一个闭区间
        cls = self.__class__
        if isinstance(other, self._network_class):
            other = cls(other)
        elif not isinstance(other, cls):
            raise TypeError(
                f"Unsupported operand type(s) for -: '{type(self)}' and '{type(other)}'"
            )

        # 无交集，直接返回自身
        if other.start > self.end or other.end < self.start:
            return self

        # other完全覆盖self，结果为空
        if other.start <= self.start and other.end >= self.end:
            return None

        # other在self中间，切分成两段
        if other.start > self.start and other.end < self.end:
            # 注意闭区间，左段为[self.start, other.start-1]，右段为[other.end+1, self.end]
            left = cls(self.start, self._address_class(other.start - 1))
            right = cls(self._address_class(other.end + 1), self.end)
            return [left, right]

        # other覆盖左侧
        if other.start <= self.start:
            # 结果为[other.end+1, self.end]
            return cls(self._address_class(other.end + 1), self.end)

        # other覆盖右侧
        if other.end >= self.end:
            # 结果为[self.start, other.start-1]
            return cls(self.start, self._address_class(other.start - 1))

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.start}","{self.end}")'

    def __str__(self):
        start, end = self.start, self.end
        if start == end:
            return str(start)

        return f"{start}-{end}"

    def __len__(self):
        return int(self.end) - int(self.start) + 1

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (self.start, self.end) == (other.start, other.end)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Unsupported operand type(s) for <: '{type(self)}' and '{type(other)}'"
            )
        return (self.start, self.end) < (other.start, other.end)

    def __getitem__(self, idx):
        if idx == 0:
            return self.start

        if idx == 1:
            return self.end

        raise IndexError('index out of range')

    def __hash__(self):
        return hash((self.start, self.end))


class IPv4Range(_IPRangeBase):
    _network_class = IPv4Network
    _address_class = IPv4Address

    @classmethod
    def from_input(cls, x):
        try:
            return cls(x)
        except Exception as e:
            raise ValueError(f"Invalid input for IPv4Range: {x!r}: {e}")


class IPv6Range(_IPRangeBase):
    _network_class = IPv6Network
    _address_class = IPv6Address

    @classmethod
    def from_input(cls, x):
        try:
            return cls(x)
        except Exception as e:
            raise ValueError(f"Invalid input for IPv6Range: {x!r}: {e}")

# -*- coding: utf-8 -*-
# Created by jackyspy at 2020/3/12
import itertools
from bisect import bisect, bisect_right
from typing import Any, Tuple, Union, Iterable

from .iprange import IPv4Range, IPv6Range
from .ipv4 import IPv4Address, IPv4Network
from .ipv6 import IPv6Address, IPv6Network
from .utils import (
    merge_ip_ranges,
    summarize_range,
    collapse_networks,
)


class _IPNetworkPoolBase:
    __slots__ = ("_ranges", "_networks_cache")

    def __init__(
        self,
        ip_networks:
        "None|str|list|tuple|_IPNetworkPoolBase|IPv4Network|IPv6Network" = None,
    ):
        self._ranges = ()  # 存储所有(start_int, end_int)区间
        self._networks_cache = None
        if ip_networks:
            self.add(ip_networks)

    @property
    def networks(self) -> tuple:
        if self._networks_cache is None:
            networks = []
            for start, end in self._ranges:
                networks.extend(
                    summarize_range(start, end, ip_version=self._ip_version))
            self._networks_cache = tuple(networks)

        return self._networks_cache

    def _invalidate_cache(self):
        self._networks_cache = None

    def add(self, ip_networks):
        if not ip_networks:
            return

        # 先合并，判断是否有变化
        new_ranges = self._format_ip_ranges(ip_networks)
        if self._ranges:
            new_ranges = tuple(merge_ip_ranges(self._ranges + new_ranges))

        if new_ranges != self._ranges:
            self._ranges = new_ranges
            self._invalidate_cache()

    def __iadd__(self, other):
        self.add(other)
        return self

    def __add__(self, other):
        if isinstance(other, self.__class__):
            other = other.networks

        pool = self.copy()
        pool.add(other)
        return pool

    def _format_ip_ranges(self,
                          ip_networks: Any) -> Tuple[Tuple[int, int], ...]:
        """
        将输入的ip_networks参数标准化为归并后的(start_int, end_int)区间tuple。

        参数:
            ip_networks: 可以为Pool对象、单个网络对象、字符串、区间元组或可迭代的上述类型。

        ip_networks支持以下类型：
        1. 本类对象（如IPv4Pool/IPv6Pool实例）：直接返回其networks属性。
        2. 单个网络对象（如IPv4Network/IPv6Network实例）：返回单元素元组。
        3. 字符串：
            a. 单个网络字符串（如"192.168.1.0/24"）
            b. 多行字符串，每行一个网络（如"192.168.1.0/24\\n10.0.0.0/8"）
            c. IP区间字符串（如"192.168.1.1-192.168.1.10"或"192.168.1.1-10"）
        4. 可迭代对象（如list/tuple），其中每个元素可以是上述的网络字符串、网络对象或数字类型。

        返回:
            Tuple[Tuple[int, int], ...]: 归并后的IP区间，每个元素为(start_int, end_int)的元组。
        """
        if not ip_networks:
            return ()

        # 1. Pool对象，直接返回其内部区间
        if isinstance(ip_networks, self.__class__):
            return ip_networks._ranges

        # 2. 单个网络对象
        network_class = self._network_class
        if isinstance(ip_networks, network_class):
            return ((ip_networks.network_address,
                     ip_networks.broadcast_address), )

        # 3. 字符串，按行分割
        if isinstance(ip_networks, str):
            ip_networks = [
                x.strip() for x in ip_networks.splitlines() if x.strip()
            ]

        # 4. 迭代处理
        address_class = self._address_class
        ranges = []
        for net in ip_networks:
            if isinstance(net, network_class):
                ranges.append((net.network_address, net.broadcast_address))
            elif isinstance(net, (tuple, list)) and len(net) == 2:
                ranges.append(tuple(map(address_class, net)))
            elif isinstance(net, (IPv4Range, IPv6Range)):
                ranges.append(net)
            elif isinstance(net, str):
                if '-' in net:
                    start_str, _, end_str = net.partition('-')
                    try:
                        start_addr = address_class(start_str)
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid IP address in range: {net}")

                    if self._network_class == IPv4Network:
                        if '.' in end_str:
                            try:
                                end_addr = address_class(end_str)
                                assert start_addr <= end_addr
                            except (ValueError, TypeError, AssertionError):
                                raise ValueError(
                                    f"Invalid IP address in range: {net}")

                        else:
                            if not (end_str.isdigit()
                                    and 0 <= int(end_str) <= 255 and
                                    (start_addr & 0xFF) <= int(end_str)):
                                raise ValueError(
                                    f"Invalid IP address in range: {net}")
                            end_addr = address_class((int(start_addr)
                                                      & 0xFFFFFF00)
                                                     | int(end_str))
                    elif self._network_class == IPv6Network:
                        try:
                            end_addr = address_class(end_str)
                            assert start_addr <= end_addr
                        except (ValueError, TypeError, AssertionError):
                            raise ValueError(
                                f"Invalid IP address in range: {net}")

                    ranges.append((start_addr, end_addr))
                else:
                    # 普通网络字符串
                    net_obj = network_class(net)
                    ranges.append(
                        (net_obj.network_address, net_obj.broadcast_address))

            else:
                raise TypeError(net)

        # 归并区间
        return tuple(merge_ip_ranges(ranges))

    def intersection(self, other):
        """
        返回当前IP池与另一个IP池（或IP网段集合）的交集。

        参数:
            other: 可以为另一个IP池对象、IP网络对象、字符串或可迭代的IP网络。

        返回:
            一个新的IP池对象，包含所有与other重叠的IP网段。
            如果没有交集，则返回空的IP池对象。
        """
        if not other or not self._ranges:
            return self.__class__()

        other_ranges = self._format_ip_ranges(other)
        if not other_ranges:
            return self.__class__()

        # 双指针遍历两个有序区间集合，计算交集
        # 优化：减少属性查找、局部变量提升、while循环展开
        ranges1 = self._ranges
        ranges2 = other_ranges
        len1 = len(ranges1)
        len2 = len(ranges2)
        result = []
        i = j = 0

        # 由于_ranges和other_ranges都已排序，双指针遍历
        while i < len1 and j < len2:
            a_start, a_end = ranges1[i]
            b_start, b_end = ranges2[j]

            # 如果当前区间无交集，推进较小区间
            if a_end < b_start:
                i += 1
            elif b_end < a_start:
                j += 1
            else:
                # 有交集
                start = max(a_start, b_start)
                end = min(a_end, b_end)
                result.append((start, end))
                # 谁先结束就推进谁
                if a_end <= b_end:
                    i += 1
                else:
                    j += 1

        return self.__class__(result)

    def __and__(self, other):
        return self.intersection(other)

    def remove(self, other, strict=False):
        """
        从当前IP池中移除指定的IP网段。

        参数:
            other: 需要移除的IP网段，可以为IP网络对象、字符串或可迭代的IP网络。
            strict (bool): 如果为True，只有当other中的所有网段都完全包含在当前IP池中时才允许移除，否则抛出异常。
                           如果为False，则尽可能移除重叠部分。

        返回:
            self: 移除操作后的IP池对象本身。
        """
        if not other or not self._ranges:
            return self

        remove_ranges = self._format_ip_ranges(other)  # 归一化为区间tuple
        if strict:
            # 严格模式，所有区间都必须完全包含
            for r in remove_ranges:
                if r not in self:
                    raise ValueError(f"{r} 超出范围")

        address_class = self._address_class
        # 直接基于_ranges做区间减法，利用两个已排序区间列表的双指针优化
        result = []
        j = 0
        n, m = len(self._ranges), len(remove_ranges)
        for cur_start, cur_end in self._ranges:
            # 跳过所有结束在当前区间左侧的remove区间
            while j < m and remove_ranges[j][1] < cur_start:
                j += 1

            temp_start, temp_end = cur_start, cur_end
            k = j
            while k < m and remove_ranges[k][0] <= temp_end:
                rem_start, rem_end = remove_ranges[k]

                # # 如果当前remove区间与当前区间无交集，直接跳过
                # if rem_start > temp_end or rem_end < temp_start:
                #     k += 1
                #     continue

                # 左侧有剩余
                if rem_start > temp_start:
                    result.append((temp_start, address_class(rem_start - 1)))

                # 更新temp_start为rem_end+1，继续处理后续重叠
                temp_start = max(temp_start, address_class(rem_end + 1))
                if temp_start > temp_end:
                    break

                k += 1

            # 如果还有剩余未被覆盖部分
            if temp_start <= temp_end:
                result.append((temp_start, temp_end))

        self._ranges = tuple(result)
        self._invalidate_cache()

        return self

    def __isub__(self, other):
        self.remove(other)
        return self

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            other = other.networks

        pool = self.copy()
        pool.remove(other)
        return pool

    def __contains__(
            self, item: "str|IPv4Address|IPv6Address|IPv4Network|IPv6Network"
    ) -> bool:
        if not self._ranges:
            return False

        # 统一转换为区间 (start_int, end_int)
        network_class = self._network_class
        address_class = self._address_class
        if isinstance(item, str):
            try:
                obj = network_class(item)
                start_int = obj.network_address
                end_int = obj.broadcast_address
            except (ValueError, TypeError):
                raise ValueError(f"Invalid IP address or network: {item}")
        elif isinstance(item, address_class):
            start_int = end_int = item
        elif isinstance(item, network_class):
            start_int = item.network_address
            end_int = item.broadcast_address
        elif isinstance(item, (tuple, self._iprange_class)):
            start_int, end_int = item
        elif isinstance(item, self.__class__):
            return all(self.__contains__(x) for x in item._ranges)
        elif isinstance(item, list):
            return all(self.__contains__(x) for x in item)
        else:
            raise TypeError(f"错误的类型：{item}")

        # 二分查找_ranges
        ranges = self._ranges
        # ranges 已经是有序的 (start, end)
        # 找到第一个 start > end_int 的位置
        pos = bisect_right(ranges, (end_int, float('inf')))
        if pos == 0:
            return False

        # 检查 pos-1 区间是否包含 [start_int, end_int]
        r_start, r_end = ranges[pos - 1]

        return r_start <= start_int and end_int <= r_end

    def copy(self):
        pool = self.__class__()
        pool._ranges = self._ranges
        pool._invalidate_cache()
        return pool

    @property
    def num_addresses(self):
        return sum(net.num_addresses for net in self.networks)

    def __len__(self):
        return self.num_addresses

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.networks)

    def __str__(self):
        return "{}[{}]".format(self.__class__.__name__,
                               ", ".join(map(str, self.networks)))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.networks == other.networks

    def __iter__(self):
        return iter(self.networks)

    @property
    def ip_ranges(self):
        """
        返回当前池中所有网络的IP范围列表。
        每个IP范围由起始地址和结束地址组成，表示池中每个连续网络段的范围。
        Returns:
            list: 包含所有IP范围对象的列表。
        """
        return [self._iprange_class(start, end) for start, end in self._ranges]

    push = add
    pop = remove

    def __bool__(self):
        return bool(self._ranges)


class IPv4Pool(_IPNetworkPoolBase):
    _network_class = IPv4Network
    _address_class = IPv4Address
    _iprange_class = IPv4Range
    _ip_version = 4

    @classmethod
    def from_inputs(cls, inputs):
        try:
            return cls(inputs)
        except Exception as e:
            raise ValueError(f"Invalid input for IPv4Pool: {inputs!r}: {e}")


class IPv6Pool(_IPNetworkPoolBase):
    _network_class = IPv6Network
    _address_class = IPv6Address
    _iprange_class = IPv6Range
    _ip_version = 6

    @classmethod
    def from_inputs(cls, inputs):
        try:
            return cls(inputs)
        except Exception as e:
            raise ValueError(f"Invalid input for IPv6Pool: {inputs!r}: {e}")

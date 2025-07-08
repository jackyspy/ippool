# -*- coding: utf-8 -*-
# 工具函数模块，原ippool.py剥离
from typing import List, Union, Tuple, Iterable, Iterator

from .ipv4 import IPv4Network, IPv4Address
from .ipv6 import IPv6Network, IPv6Address
from .iprange import IPv4Range, IPv6Range, _IPRangeBase


def merge_ip_ranges(
    ranges: Iterable[tuple[int, int]],
    is_sorted: bool = False,
    as_generator: bool = False
) -> Union[list[tuple[int, int]], Iterator[tuple[int, int]]]:
    """
    合并重叠或相邻的IP地址范围。
    支持生成器流式输出，适合大数据。
    Args:
        ranges: 包含(start_ip_int, end_ip_int)元组的列表
        as_generator: 是否以生成器方式输出
    Returns:
        合并后的范围列表或生成器
    """
    if not ranges:
        return [] if not as_generator else iter(())

    # 按地址排序
    if not is_sorted:
        ranges = sorted(ranges)
    elif not isinstance(ranges, (tuple, list)):
        ranges = list(ranges)

    def _gen():
        current_start, current_end = ranges[0]
        for next_start, next_end in ranges[1:]:
            if next_start <= current_end + 1:
                current_end = max(current_end, next_end)
            else:
                yield (current_start, current_end)
                current_start, current_end = next_start, next_end
        yield (current_start, current_end)

    if as_generator:
        return _gen()
    else:
        return list(_gen())


def summarize_range(start_ip_int, end_ip_int, ip_version=4):
    """
    将IP地址范围（start_ip_int到end_ip_int）汇总为IPv4Network或IPv6Network对象列表。
    这是ipaddress.summarize_address_range的自定义实现。
    
    Args:
        start_ip_int: 起始IP地址的整数值
        end_ip_int: 结束IP地址的整数值
        ip_version: IP版本，4表示IPv4，6表示IPv6，默认为4
        
    Returns:
        网络对象列表
    """
    networks = []
    current_ip = start_ip_int

    if ip_version == 4:
        max_bits = 32
        NetworkClass = IPv4Network
    elif ip_version == 6:
        max_bits = 128
        NetworkClass = IPv6Network
    else:
        raise ValueError("ip_version must be 4 or 6")

    while current_ip <= end_ip_int:
        for mask_bit in range(0, max_bits + 1):
            network_size = 1 << (max_bits - mask_bit)
            if ((current_ip & (network_size - 1))
                    == 0) and (current_ip + network_size - 1) <= end_ip_int:
                network = NetworkClass((current_ip, mask_bit))
                networks.append(network)
                current_ip = int(network.broadcast_address) + 1
                break

    return networks


def collapse_networks(networks: List[Union[IPv4Network, IPv6Network]],
                      ip_version=0):
    """
    将IPv4Network或IPv6Network对象列表合并为最小的非重叠网络列表。
    这是ipaddress.collapse_addresses的自定义实现。
    
    Args:
        networks: IPv4Network或IPv6Network对象的列表
        
    Returns:
        合并后的网络对象元组
    """
    if not networks:
        return ()

    # 如果ip_version为0，则根据第一个网络对象的类型判断，否则直接用传入的ip_version
    if ip_version == 0:
        first_network = networks[0]
        if isinstance(first_network, IPv4Network):
            ip_version = 4
        elif isinstance(first_network, IPv6Network):
            ip_version = 6
        else:
            raise ValueError(
                "networks must contain IPv4Network or IPv6Network objects")

    ranges = [(int(net.network_address), int(net.broadcast_address))
              for net in sorted(networks, key=lambda x: x.network_address)]

    merged_ranges = merge_ip_ranges(ranges)

    collapsed_networks = []
    for start_int, end_int in merged_ranges:
        collapsed_networks.extend(
            summarize_range(start_int, end_int, ip_version=ip_version))

    return tuple(collapsed_networks)


def find_overlapping_ranges(
        ranges: Iterable[Union[str, tuple, IPv4Range, IPv6Range, int,
                               IPv4Network, IPv6Network]],
        ipv6: bool = False) -> List[Tuple[_IPRangeBase, List[_IPRangeBase]]]:
    """
    查找多个地址段中的所有不同重叠部分，并返回重叠区域及其涉及的源地址段。
    
    Args:
        ranges: 地址段列表，支持多种格式：
            - 字符串：CIDR格式（如"192.168.1.0/24"）或IP范围（如"192.168.1.1-192.168.1.10"）
            - 元组：(start_ip, end_ip) 或 (start_int, end_int)
            - IPv4Range/IPv6Range 对象
            - 整数：单个IP地址的整数值
            - IPv4Network/IPv6Network 对象
        ipv6: 是否使用IPv6地址类型，默认为False（IPv4）
    
    Returns:
        重叠区域列表，每个元素为 (重叠区域, [涉及的源地址段列表])
        重叠区域和源地址段都用 Range 对象表示
    """
    if not ranges:
        return []

    RangeClass = IPv6Range if ipv6 else IPv4Range
    AddressClass = IPv6Address if ipv6 else IPv4Address
    normalized_ranges = [RangeClass(x) for x in ranges]

    # 生成事件
    events = []
    for idx, rng in enumerate(normalized_ranges):
        events.append((rng.start, 'L', idx))
        # 闭区间，end+1 作为右端点
        events.append((rng.end + 1, 'R', idx))

    # 按位置排序，R优先于L
    events.sort(key=lambda x: (x[0], 0 if x[1] == 'R' else 1))
    active = set()
    last_pos = 1 << 128
    result = []
    for pos, typ, idx in events:
        if pos > last_pos and len(active) > 1:
            # 记录重叠区间
            overlap_range = RangeClass(last_pos, AddressClass(int(pos) - 1))
            involved = [normalized_ranges[i] for i in active]
            result.append((overlap_range, involved))

        if typ == 'L':
            active.add(idx)
        else:
            active.remove(idx)

        last_pos = pos

    return [(overlap_range, sorted(set(involved_sources)))
            for overlap_range, involved_sources in result]

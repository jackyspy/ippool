# -*- coding: utf-8 -*-
# Created by jackyspy at 2020/3/12
from functools import total_ordering
import socket
import struct


@total_ordering
class IPv4Address(int):
    __slots__ = ()

    def __new__(cls, address):
        if isinstance(address, (int, IPv4Address)):
            # 检查数值范围是否在IPv4地址的有效范围内 (0-4294967295)
            if not (0 <= address <= 0xFFFFFFFF):
                raise ValueError(
                    f"IPv4 address value {address} is out of valid range (0-4294967295)"
                )
            value = address
        elif isinstance(address, str):
            try:
                value = int(struct.unpack("!I", socket.inet_aton(address))[0])
            except OSError as e:
                raise ValueError(f"Invalid IPv4 address: {address}") from e
        else:
            raise TypeError(f"Invalid address type: {type(address)}")

        return super().__new__(cls, value)

    def __str__(self):
        return socket.inet_ntoa(struct.pack("!I", self))

    def __repr__(self):
        return f"IPv4Address('{str(self)}')"

    def __eq__(self, other):
        if isinstance(other, str):
            other = IPv4Address(other)

        return super().__eq__(other)

    def __lt__(self, other):
        if isinstance(other, str):
            other = IPv4Address(other)

        return super().__lt__(other)

    def __hash__(self):
        return int(self)


@total_ordering
class IPv4Network:
    __slots__ = ("_ip", "_mask_bit")

    def __init__(self, network):
        """
        初始化IPv4Network对象。

        参数:
            network (str | tuple | IPv4Network):
                - 字符串格式: 支持"192.168.1.0/24"或单个IP（视为/32网络）。
                - 元组格式: (ip, mask_bit)，ip为整数或IPv4Address，mask_bit为掩码位数。
                - IPv4Network对象: 拷贝其网络地址和掩码位数。

        属性:
            _ip (int): 网络地址（整数形式）。
            _mask_bit (int): 掩码位数（0-32）。

        异常:
            TypeError: 输入类型不支持。
            ValueError: 掩码位数不在0~32范围内。
        """
        if isinstance(network, str):
            if "/" in network:
                ip_str, mask_bit_str = network.split("/")
                self._ip = int(IPv4Address(ip_str))
                self._mask_bit = int(mask_bit_str)
            else:
                # 处理单个IP，视为/32网络
                self._ip = int(IPv4Address(network))
                self._mask_bit = 32
        elif isinstance(network, tuple) and len(network) == 2:
            self._ip = int(network[0])
            self._mask_bit = int(network[1])
        elif isinstance(network, IPv4Network):
            self._ip = network._ip
            self._mask_bit = network._mask_bit
        else:
            raise TypeError(f"Invalid network type: {type(network)}")

        if not (0 <= self._mask_bit <= 32):
            raise ValueError("mask_bit must be between 0 and 32")

        # 保证_ip为网络地址
        self._ip = self._ip & self._netmask_int()

    def _netmask_int(self):
        return ((1 << self._mask_bit) -
                1) << (32 - self._mask_bit) if self._mask_bit else 0

    @property
    def network_address(self):
        return IPv4Address(self._ip)

    @property
    def broadcast_address(self):
        return IPv4Address(self._ip | ((1 << (32 - self._mask_bit)) - 1))

    @property
    def num_addresses(self):
        return 1 << (32 - self._mask_bit)

    def __str__(self):
        return f"{str(self.network_address)}/{self._mask_bit}"

    def __repr__(self):
        return f"IPv4Network('{str(self)}')'"

    def __eq__(self, other):
        if isinstance(other, IPv4Network):
            return self._ip == other._ip and self._mask_bit == other._mask_bit

        raise TypeError("other must be an IPv4Network object")

    def __lt__(self, other):
        if isinstance(other, IPv4Network):
            print(self._ip, other._ip, self._mask_bit, other._mask_bit)
            if self._ip != other._ip:
                return self._ip < other._ip

            return self._mask_bit > other._mask_bit

        raise TypeError("other must be an IPv4Network object")

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not (self < other or self == other)

    def __ge__(self, other):
        return not (self < other)

    def subnet_of(self, other):
        """Check if this network is a subnet of another network."""
        if not isinstance(other, IPv4Network):
            raise TypeError("other must be an IPv4Network object")

        return (self._mask_bit >= other._mask_bit
                and (self._ip & other._netmask_int()) == other._ip)

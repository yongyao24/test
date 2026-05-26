#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钱包动态追踪器 - 从 gmgn.ai 获取数据
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import time

class WalletTracker:
    """追踪钱包动态的类"""
    
    BASE_URL = "https://gmgn.ai/api"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    def __init__(self, timeout: int = 10):
        """
        初始化追踪器
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def get_wallet_info(self, wallet_address: str) -> Optional[Dict]:
        """
        获取钱包信息
        
        Args:
            wallet_address: 钱包地址
            
        Returns:
            钱包信息字典，失败返回 None
        """
        try:
            url = f"{self.BASE_URL}/wallet/info"
            params = {
                "address": wallet_address
            }
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取钱包信息失败: {e}")
            return None
    
    def get_wallet_transactions(self, wallet_address: str, limit: int = 50) -> Optional[List[Dict]]:
        """
        获取钱包交易记录
        
        Args:
            wallet_address: 钱包地址
            limit: 返回记录数量限制
            
        Returns:
            交易记录列表，失败返回 None
        """
        try:
            url = f"{self.BASE_URL}/wallet/transactions"
            params = {
                "address": wallet_address,
                "limit": limit
            }
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"获取交易记录失败: {e}")
            return None
    
    def get_wallet_balance(self, wallet_address: str) -> Optional[Dict]:
        """
        获取钱包余额
        
        Args:
            wallet_address: 钱包地址
            
        Returns:
            余额信息字典，失败返回 None
        """
        try:
            url = f"{self.BASE_URL}/wallet/balance"
            params = {
                "address": wallet_address
            }
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取余额失败: {e}")
            return None
    
    def get_token_holders(self, token_address: str, limit: int = 100) -> Optional[List[Dict]]:
        """
        获取代币持有者列表
        
        Args:
            token_address: 代币合约地址
            limit: 返回持有者数量限制
            
        Returns:
            持有者列表，失败返回 None
        """
        try:
            url = f"{self.BASE_URL}/token/holders"
            params = {
                "address": token_address,
                "limit": limit
            }
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"获取持有者列表失败: {e}")
            return None
    
    def monitor_wallet(self, wallet_address: str, interval: int = 60, duration: Optional[int] = None):
        """
        持续监控钱包动态
        
        Args:
            wallet_address: 钱包地址
            interval: 检查间隔（秒）
            duration: 监控持续时间（秒），None 表示无限监控
        """
        print(f"开始监控钱包: {wallet_address}")
        print(f"检查间隔: {interval}秒")
        
        start_time = time.time()
        previous_balance = None
        
        while True:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{current_time}] 检查钱包动态...")
                
                # 获取余额
                balance_info = self.get_wallet_balance(wallet_address)
                if balance_info:
                    current_balance = balance_info.get("balance")
                    print(f"当前余额: {current_balance}")
                    
                    if previous_balance is not None and current_balance != previous_balance:
                        change = float(current_balance) - float(previous_balance)
                        print(f"⚠️ 余额变化: {change:+.6f}")
                    
                    previous_balance = current_balance
                
                # 获取最新交易
                transactions = self.get_wallet_transactions(wallet_address, limit=5)
                if transactions:
                    print(f"最近5笔交易:")
                    for tx in transactions:
                        print(f"  - {tx.get('hash', 'N/A')}: {tx.get('from')} -> {tx.get('to')}")
                
                # 检查是否超时
                if duration and (time.time() - start_time) > duration:
                    print(f"\n监控时间已到，停止监控")
                    break
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print(f"\n监控已中断")
                break
            except Exception as e:
                print(f"监控过程中出错: {e}")
                time.sleep(interval)
    
    def close(self):
        """关闭会话"""
        self.session.close()


def main():
    """主函数示例"""
    # 创建追踪器实例
    tracker = WalletTracker()
    
    try:
        # 示例：获取钱包信息
        wallet_address = "0x1234567890abcdef1234567890abcdef12345678"  # 替换为实际的钱包地址
        
        print("=" * 50)
        print("钱包追踪器 - gmgn.ai 数据获取")
        print("=" * 50)
        
        # 获取钱包信息
        print("\n1. 获取钱包信息...")
        wallet_info = tracker.get_wallet_info(wallet_address)
        if wallet_info:
            print(json.dumps(wallet_info, indent=2, ensure_ascii=False))
        
        # 获取余额
        print("\n2. 获取钱包余额...")
        balance = tracker.get_wallet_balance(wallet_address)
        if balance:
            print(json.dumps(balance, indent=2, ensure_ascii=False))
        
        # 获取交易记录
        print("\n3. 获取交易记录...")
        transactions = tracker.get_wallet_transactions(wallet_address, limit=10)
        if transactions:
            print(json.dumps(transactions, indent=2, ensure_ascii=False))
        
        # 持续监控（可选，监控60秒）
        # tracker.monitor_wallet(wallet_address, interval=10, duration=60)
        
    finally:
        tracker.close()


if __name__ == "__main__":
    main()

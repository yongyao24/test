#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钱包动态追踪器 - 从 gmgn.ai 获取数据
支持登录认证和 Token 管理
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import time
import os
from urllib.parse import urljoin

class WalletTracker:
    """追踪钱包动态的类"""
    
    BASE_URL = "https://gmgn.ai"
    API_URL = "https://gmgn.ai/api"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://gmgn.ai/",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
    }
    
    def __init__(self, timeout: int = 10, token: Optional[str] = None, cookies: Optional[Dict] = None):
        """
        初始化追踪器
        
        Args:
            timeout: 请求超时时间（秒）
            token: JWT Token 或 API Key
            cookies: 已有的 Cookie 字典
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.token = token
        self.cookies = cookies or {}
        
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        
        if cookies:
            self.session.cookies.update(cookies)
    
    def login(self, email: str, password: str) -> bool:
        """
        使用邮箱和密码登录
        
        Args:
            email: 邮箱地址
            password: 密码
            
        Returns:
            登录成功返回 True，失败返回 False
        """
        try:
            url = urljoin(self.BASE_URL, "/api/v1/auth/login")
            
            payload = {
                "email": email,
                "password": password
            }
            
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers=self.HEADERS
            )
            
            print(f"登录响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # 提取 Token
                if "token" in data:
                    self.token = data["token"]
                    self.session.headers["Authorization"] = f"Bearer {self.token}"
                    print(f"✅ 登录成功，Token: {self.token[:20]}...")
                
                if "access_token" in data:
                    self.token = data["access_token"]
                    self.session.headers["Authorization"] = f"Bearer {self.token}"
                    print(f"✅ 登录成功，Access Token: {self.token[:20]}...")
                
                # 保存 Cookie
                self.cookies = dict(self.session.cookies)
                print(f"✅ 已保存 Cookie")
                
                return True
            else:
                print(f"❌ 登录失败: {response.status_code}")
                print(f"响应: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 登录请求失败: {e}")
            return False
    
    def login_with_token(self, token: str) -> bool:
        """
        使用已有的 Token 直接登录
        
        Args:
            token: JWT Token 或 API Key
            
        Returns:
            设置成功返回 True
        """
        self.token = token
        self.session.headers["Authorization"] = f"Bearer {token}"
        print(f"✅ 已设置 Token: {token[:20]}...")
        return True
    
    def verify_auth(self) -> bool:
        """
        验证身份认证是否有效
        
        Returns:
            认证有效返回 True，失败返回 False
        """
        try:
            url = urljoin(self.API_URL, "/v1/auth/verify")
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                print("✅ 身份认证有效")
                return True
            else:
                print(f"❌ 身份认证失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 验证身份认证失败: {e}")
            return False
    
    def get_wallet_info(self, wallet_address: str) -> Optional[Dict]:
        """
        获取钱包信息
        
        Args:
            wallet_address: 钱包地址
            
        Returns:
            钱包信息字典，失败返回 None
        """
        try:
            # 尝试多个可能的 API 端点
            endpoints = [
                f"/api/v1/wallet/info",
                f"/api/wallet/info",
                f"/api/v1/address/{wallet_address}",
            ]
            
            for endpoint in endpoints:
                url = urljoin(self.API_URL, endpoint)
                params = {"address": wallet_address}
                
                response = self.session.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    print("⚠️ 需要身份认证，请先登录")
                    break
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取钱包信息失败: {e}")
            return None
    
    def get_wallet_transactions(self, wallet_address: str, limit: int = 50, offset: int = 0) -> Optional[List[Dict]]:
        """
        获取钱包交易记录
        
        Args:
            wallet_address: 钱包地址
            limit: 返回记录数量限制
            offset: 偏移量
            
        Returns:
            交易记录列表，失败返回 None
        """
        try:
            endpoints = [
                f"/api/v1/wallet/transactions",
                f"/api/wallet/tx",
                f"/api/v1/address/{wallet_address}/transactions",
            ]
            
            for endpoint in endpoints:
                url = urljoin(self.API_URL, endpoint)
                params = {
                    "address": wallet_address,
                    "limit": limit,
                    "offset": offset
                }
                
                response = self.session.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        return data.get("data", [])
                    return data
                elif response.status_code == 401:
                    print("⚠️ 需要身份认证，请先登录")
                    break
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取交易记录失败: {e}")
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
            endpoints = [
                f"/api/v1/wallet/balance",
                f"/api/wallet/balance",
                f"/api/v1/address/{wallet_address}/balance",
            ]
            
            for endpoint in endpoints:
                url = urljoin(self.API_URL, endpoint)
                params = {"address": wallet_address}
                
                response = self.session.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    print("⚠️ 需要身份认证，请先登录")
                    break
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取余额失败: {e}")
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
            endpoints = [
                f"/api/v1/token/holders",
                f"/api/token/holders",
                f"/api/v1/token/{token_address}/holders",
            ]
            
            for endpoint in endpoints:
                url = urljoin(self.API_URL, endpoint)
                params = {
                    "address": token_address,
                    "limit": limit
                }
                
                response = self.session.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        return data.get("data", [])
                    return data
                elif response.status_code == 401:
                    print("⚠️ 需要身份认证，请先登录")
                    break
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取持有者列表失败: {e}")
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
                        tx_hash = tx.get("hash", tx.get("tx_hash", "N/A"))
                        tx_from = tx.get("from", "N/A")
                        tx_to = tx.get("to", "N/A")
                        print(f"  - {tx_hash[:10]}...: {tx_from[:10]}... -> {tx_to[:10]}...")
                
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
    
    def save_session(self, filepath: str) -> bool:
        """
        保存会话信息到文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            保存成功返回 True
        """
        try:
            session_data = {
                "token": self.token,
                "cookies": self.cookies
            }
            
            with open(filepath, "w") as f:
                json.dump(session_data, f, indent=2)
            
            print(f"✅ 会话已保存到: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 保存会话失败: {e}")
            return False
    
    def load_session(self, filepath: str) -> bool:
        """
        从文件加载会话信息
        
        Args:
            filepath: 文件路径
            
        Returns:
            加载成功返回 True
        """
        try:
            if not os.path.exists(filepath):
                print(f"⚠️ 会话文件不存在: {filepath}")
                return False
            
            with open(filepath, "r") as f:
                session_data = json.load(f)
            
            if session_data.get("token"):
                self.login_with_token(session_data["token"])
            
            if session_data.get("cookies"):
                self.cookies = session_data["cookies"]
                self.session.cookies.update(self.cookies)
            
            print(f"✅ 会话已从文件加载: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 加载会话失败: {e}")
            return False
    
    def close(self):
        """关闭会话"""
        self.session.close()


def main():
    """主函数示例"""
    # 创建追踪器实例
    tracker = WalletTracker()
    
    try:
        print("=" * 60)
        print("钱包追踪器 - gmgn.ai 数据获取")
        print("=" * 60)
        
        # 方式 1: 使用邮箱和密码登录
        # email = "your_email@example.com"
        # password = "your_password"
        # if tracker.login(email, password):
        #     tracker.save_session("session.json")
        # else:
        #     print("登录失败")
        #     return
        
        # 方式 2: 使用已保存的会话
        # if tracker.load_session("session.json"):
        #     print("会话已恢复")
        
        # 方式 3: 直接使用 Token
        # token = "your_api_token_here"
        # tracker.login_with_token(token)
        
        # 验证身份认证
        print("\n验证身份认证...")
        # if not tracker.verify_auth():
        #     print("⚠️ 身份认证失败，某些功能可能不可用")
        
        # 示例：获取钱包信息
        wallet_address = "0x1234567890abcdef1234567890abcdef12345678"  # 替换为实际的钱包地址
        
        print(f"\n1. 获取钱包信息 ({wallet_address})...")
        wallet_info = tracker.get_wallet_info(wallet_address)
        if wallet_info:
            print(json.dumps(wallet_info, indent=2, ensure_ascii=False))
        else:
            print("❌ 获取失败，可能需要有效的 Token 或登录信息")
        
        # 获取余额
        print("\n2. 获取钱包余额...")
        balance = tracker.get_wallet_balance(wallet_address)
        if balance:
            print(json.dumps(balance, indent=2, ensure_ascii=False))
        
        # 获取交易记录
        print("\n3. 获取交易记录...")
        transactions = tracker.get_wallet_transactions(wallet_address, limit=10)
        if transactions:
            print(json.dumps(transactions[:3], indent=2, ensure_ascii=False))  # 只显示前 3 条
        
        # 持续监控（可选，监控60秒）
        # tracker.monitor_wallet(wallet_address, interval=10, duration=60)
        
    finally:
        tracker.close()


if __name__ == "__main__":
    main()

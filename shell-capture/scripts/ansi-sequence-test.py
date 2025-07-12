#!/usr/bin/env python3
"""
ANSI Control Sequence Test Tool
Comprehensive test for all ANSI control sequences and escape codes
Tests both single-byte control characters and multi-byte escape sequences
"""

import sys
import tty
import termios
import select
import re
from typing import List, Tuple, Dict

class ANSISequenceTester:
    def __init__(self):
        self.control_chars = {
            0: 'NULL (NUL)',
            1: 'START OF HEADING (SOH)',
            2: 'START OF TEXT (STX)',
            3: 'END OF TEXT (ETX)',
            4: 'END OF TRANSMISSION (EOT)',
            5: 'ENQUIRY (ENQ)',
            6: 'ACKNOWLEDGE (ACK)',
            7: 'BELL (BEL)',
            8: 'BACKSPACE (BS)',
            9: 'HORIZONTAL TAB (HT)',
            10: 'LINE FEED (LF)',
            11: 'VERTICAL TAB (VT)',
            12: 'FORM FEED (FF)',
            13: 'CARRIAGE RETURN (CR)',
            14: 'SHIFT OUT (SO)',
            15: 'SHIFT IN (SI)',
            16: 'DATA LINK ESCAPE (DLE)',
            17: 'DEVICE CONTROL 1 (DC1)',
            18: 'DEVICE CONTROL 2 (DC2)',
            19: 'DEVICE CONTROL 3 (DC3)',
            20: 'DEVICE CONTROL 4 (DC4)',
            21: 'NEGATIVE ACKNOWLEDGE (NAK)',
            22: 'SYNCHRONOUS IDLE (SYN)',
            23: 'END OF TRANSMISSION BLOCK (ETB)',
            24: 'CANCEL (CAN)',
            25: 'END OF MEDIUM (EM)',
            26: 'SUBSTITUTE (SUB)',
            27: 'ESCAPE (ESC)',
            28: 'FILE SEPARATOR (FS)',
            29: 'GROUP SEPARATOR (GS)',
            30: 'RECORD SEPARATOR (RS)',
            31: 'UNIT SEPARATOR (US)',
            127: 'DELETE (DEL)'
        }
        
        self.ansi_sequences = {
            b'\x1b[A': 'UP ARROW',
            b'\x1b[B': 'DOWN ARROW',
            b'\x1b[C': 'RIGHT ARROW',
            b'\x1b[D': 'LEFT ARROW',
            b'\x1b[H': 'HOME',
            b'\x1b[F': 'END',
            b'\x1b[5~': 'PAGE UP',
            b'\x1b[6~': 'PAGE DOWN',
            b'\x1b[2~': 'INSERT',
            b'\x1b[3~': 'DELETE',
            b'\x1b[1~': 'HOME (alternative)',
            b'\x1b[4~': 'END (alternative)',
            b'\x1bOP': 'F1',
            b'\x1bOQ': 'F2',
            b'\x1bOR': 'F3',
            b'\x1bOS': 'F4',
            b'\x1b[15~': 'F5',
            b'\x1b[17~': 'F6',
            b'\x1b[18~': 'F7',
            b'\x1b[19~': 'F8',
            b'\x1b[20~': 'F9',
            b'\x1b[21~': 'F10',
            b'\x1b[23~': 'F11',
            b'\x1b[24~': 'F12',
        }
        
        self.escape_sequences = [
            b'\x1b',  # ESC
            b'\x1b[', # CSI
            b'\x1bO', # SS3
            b'\x1b[1',
            b'\x1b[2',
            b'\x1b[3',
            b'\x1b[4',
            b'\x1b[5',
            b'\x1b[6',
            b'\x1b[1~',
            b'\x1b[2~',
            b'\x1b[3~',
            b'\x1b[4~',
            b'\x1b[5~',
            b'\x1b[6~',
            b'\x1b[15~',
            b'\x1b[17~',
            b'\x1b[18~',
            b'\x1b[19~',
            b'\x1b[20~',
            b'\x1b[21~',
            b'\x1b[23~',
            b'\x1b[24~',
        ]
        
        self.buffer = b''
        self.old_attrs = None

    def get_control_char_name(self, byte_val: int) -> str:
        """获取控制字符的名称"""
        if byte_val in self.control_chars:
            return self.control_chars[byte_val]
        elif 32 <= byte_val <= 126:
            return f"PRINTABLE: '{chr(byte_val)}'"
        else:
            return f"UNKNOWN: byte={byte_val} (0x{byte_val:02x})"

    def parse_escape_sequence(self, data: bytes) -> Tuple[str, int]:
        """解析转义序列"""
        # 检查是否匹配已知序列
        for seq, name in self.ansi_sequences.items():
            if data.startswith(seq):
                return name, len(seq)
        
        # 检查是否是转义序列的开头
        if data.startswith(b'\x1b'):
            # 查找完整序列的结束
            if len(data) >= 2:
                if data[1:2] == b'[':
                    # CSI序列
                    match = re.search(rb'\x1b\[[\d;]*[~ABCDEFGHJKLMPQRS]', data)
                    if match:
                        return f"CSI SEQUENCE: {match.group().hex()}", len(match.group())
                    else:
                        # 可能是部分序列
                        return "PARTIAL CSI SEQUENCE", 0
                elif data[1:2] == b'O':
                    # SS3序列
                    if len(data) >= 3:
                        return f"SS3 SEQUENCE: {data[:3].hex()}", 3
                    else:
                        return "PARTIAL SS3 SEQUENCE", 0
                else:
                    return f"ESC+{chr(data[1]) if len(data) > 1 else 'PARTIAL'}", min(2, len(data))
            else:
                return "ESC (partial)", 0
        
        return None, 0

    def format_bytes(self, data: bytes) -> str:
        """格式化字节数据为可读字符串"""
        if not data:
            return ""
        
        hex_str = ' '.join(f'{b:02x}' for b in data)
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in data)
        return f"bytes=[{hex_str}] ascii='{ascii_str}'"

    def print_help(self):
        """打印帮助信息"""
        print("ANSI Control Sequence Test Tool")
        print("=" * 50)
        print("This tool captures and displays all input including:")
        print("- Single-byte control characters (0-31, 127)")
        print("- Multi-byte escape sequences (arrow keys, function keys, etc.)")
        print("- Printable characters")
        print()
        print("Commands:")
        print("  q - Quit")
        print("  h - Show this help")
        print("  c - Clear screen")
        print("  r - Reset buffer")
        print()
        print("Press any keys to see their raw byte representation...")
        print("-" * 50)

    def run_test(self):
        """运行测试"""
        self.print_help()
        
        # 保存原始terminal设置
        self.old_attrs = termios.tcgetattr(sys.stdin.fileno())
        
        try:
            # 设置raw模式以捕获所有字节
            tty.setraw(sys.stdin.fileno())
            
            while True:
                # 等待输入
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    if not char:
                        continue
                    
                    self.buffer += char.encode('latin1')
                    
                    # 尝试解析序列
                    sequence_name, consumed = self.parse_escape_sequence(self.buffer)
                    
                    if consumed > 0:
                        # 找到完整序列
                        sequence_data = self.buffer[:consumed]
                        self.buffer = self.buffer[consumed:]
                        
                        print(f"\r[ESC] {sequence_name}")
                        print(f"      Raw: {self.format_bytes(sequence_data)}")
                        
                    elif len(self.buffer) == 1:
                        # 单字节字符
                        byte_val = ord(char)
                        char_name = self.get_control_char_name(byte_val)
                        
                        if byte_val == ord('q'):
                            print("\r[QUIT] User requested quit")
                            break
                        elif byte_val == ord('h'):
                            self.print_help()
                        elif byte_val == ord('c'):
                            print("\033[2J\033[H", end='')  # 清屏
                        elif byte_val == ord('r'):
                            self.buffer = b''
                            print("\r[RESET] Buffer cleared")
                        else:
                            print(f"\r[{byte_val:3d}] {char_name}")
                            print(f"      Raw: {self.format_bytes(self.buffer)}")
                        
                        self.buffer = b''
                    
                    # 如果缓冲区太长，可能是无效序列
                    if len(self.buffer) > 10:
                        print(f"\r[ERROR] Buffer overflow: {self.format_bytes(self.buffer)}")
                        self.buffer = b''
                        
        except KeyboardInterrupt:
            print("\n\n[INTERRUPT] Interrupted by user (Ctrl+C)")
        except Exception as e:
            print(f"\n\n[ERROR] {e}")
        finally:
            # 恢复terminal设置
            if self.old_attrs:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, self.old_attrs)
            print("\n[COMPLETE] Test completed.")

    def run_batch_test(self):
        """运行批处理测试，显示所有控制字符"""
        print("Control Character Reference")
        print("=" * 40)
        
        # 打印所有控制字符
        print("\nControl Characters (0-31, 127):")
        for i in sorted(self.control_chars.keys()):
            name = self.control_chars[i]
            char = '^' + chr(ord('@') + i) if 0 <= i <= 26 else repr(chr(i))
            print(f"  {i:3d} (0x{i:02x}): {name} {char}")
        
        # 打印常见ANSI序列
        print("\nCommon ANSI Escape Sequences:")
        for seq, name in self.ansi_sequences.items():
            hex_str = ' '.join(f'{b:02x}' for b in seq)
            print(f"  {name:20} {hex_str}")
        
        print("\n" + "=" * 40)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ANSI Control Sequence Test Tool')
    parser.add_argument('--batch', '-b', action='store_true', 
                       help='Run batch test to show all control characters')
    
    args = parser.parse_args()
    
    tester = ANSISequenceTester()
    
    if args.batch:
        tester.run_batch_test()
    else:
        tester.run_test()
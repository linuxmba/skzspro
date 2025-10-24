# -*- coding: utf-8 -*-
"""
网课平台登录模块
支持自动获取验证码和登录功能
"""

import requests
import json
from typing import Dict, Tuple, Optional


class WdxuetangSession:
    """网课平台会话管理类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://admin.wdxuetang.cn"
        self.token = None
        self.user_info = None
        
        # 设置默认请求头
        self.session.headers.update({
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://cqwlxycrjy.wdxuetang.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://cqwlxycrjy.wdxuetang.cn/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36 Edg/141.0.0.0',
            'sec-ch-ua': '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"'
        })
    
    def get_captcha(self) -> Tuple[str, str]:
        """
        获取验证码
        
        Returns:
            Tuple[str, str]: (验证码值, uuid)
        """
        url = f"{self.base_url}/cgi-bin/api/account/student-mobile/auth/code-image"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success') and data.get('code') == 0:
                captcha_data = data.get('data', {})
                code = captcha_data.get('code', '')
                uuid = captcha_data.get('uuid', '')
                
                return code, uuid
            else:
                raise Exception(f"获取验证码失败: {data.get('message', '未知错误')}")
                
        except requests.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"响应解析失败: {str(e)}")
    
    def login(self, account: str, password: str, captcha_code: str, uuid: str) -> bool:
        """
        登录网课平台
        
        Args:
            account: 账号
            password: 密码
            captcha_code: 验证码
            uuid: 验证码UUID
            
        Returns:
            bool: 登录是否成功
        """
        url = f"{self.base_url}/cgi-bin/api/account/student-mobile/auth/account-login"
        
        # 设置Content-Type
        headers = {'Content-Type': 'application/json'}
        
        # 登录数据
        login_data = {
            "account": account,
            "loginType": "Mini_App",
            "password": password,
            "code": captcha_code,
            "uuid": uuid
        }
        
        try:
            response = self.session.post(url, headers=headers, json=login_data)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success') and data.get('code') == 0:
                # 保存登录信息
                self.token = data.get('data', {}).get('token')
                self.user_info = data.get('data', {}).get('user', {})
                
                print("登录成功!")
                print(f"用户: {self.user_info.get('username', '未知')}")
                print(f"学号: {self.user_info.get('studentNumber', '未知')}")
                print(f"Token: {self.token}")
                
                return True
            else:
                print(f"登录失败: {data.get('message', '未知错误')}")
                return False
                
        except requests.RequestException as e:
            print(f"网络请求失败: {str(e)}")
            return False
        except json.JSONDecodeError as e:
            print(f"响应解析失败: {str(e)}")
            return False
    
    def auto_login(self, account: str, password: str) -> bool:
        """
        自动登录（自动获取验证码）
        
        Args:
            account: 账号
            password: 密码
            
        Returns:
            bool: 登录是否成功
        """
        try:
            print("正在获取验证码...")
            captcha_code, uuid = self.get_captcha()
            
            print(f"验证码: {captcha_code}")
            print("正在登录...")
            return self.login(account, password, captcha_code, uuid)
            
        except Exception as e:
            print(f"自动登录失败: {str(e)}")
            return False
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.token is not None
    
    def get_user_info(self) -> Optional[Dict]:
        """获取用户信息"""
        return self.user_info
    
    def get_token(self) -> Optional[str]:
        """获取登录token"""
        return self.token
    
    def get_my_courses(self) -> Optional[list]:
        """
        获取我的课程列表
        
        Returns:
            Optional[list]: 课程列表，失败时返回None
        """
        if not self.is_logged_in():
            print("请先登录")
            return None
            
        url = f"{self.base_url}/cgi-bin/api/lessons/student-mobile/learningCenter/myCourse"
        params = {"testType": "false"}
        
        # 添加token到请求头 - 使用Studenttoken
        headers = {"Studenttoken": self.token}
        
        try:
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success') and data.get('code') == 0:
                courses = data.get('data', [])
                print(f"成功获取到 {len(courses)} 门课程")
                return courses
            else:
                print(f"获取课程列表失败: {data.get('message', '未知错误')}")
                return None
                
        except requests.RequestException as e:
            print(f"网络请求失败: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"响应解析失败: {str(e)}")
            return None
    
    def display_courses(self, courses: list = None) -> None:
        """
        显示课程列表
        
        Args:
            courses: 课程列表，如果为None则自动获取
        """
        if courses is None:
            courses = self.get_my_courses()
            
        if not courses:
            print("没有课程数据")
            return
            
        print("\n" + "="*80)
        print("课程列表")
        print("="*80)
        
        for i, course in enumerate(courses, 1):
            print(f"{i:2d}. {course.get('name', '未知课程')}")
            print(f"    学科: {course.get('subjectName', '未知')}")
            print(f"    进度: {course.get('finishRate', 0)}%")
            print(f"    课程ID: {course.get('id', '未知')}")
            print(f"    作业分数: {course.get('homeworkScore', 0)}")
            print(f"    练习分数: {course.get('practiceScore', 0)}")
            print(f"    时间点: {course.get('timePoint', 0)}")
            print("-" * 80)
    
    def get_course_by_id(self, course_id: int) -> Optional[dict]:
        """
        根据ID获取特定课程信息
        
        Args:
            course_id: 课程ID
            
        Returns:
            Optional[dict]: 课程信息，未找到时返回None
        """
        courses = self.get_my_courses()
        if not courses:
            return None
            
        for course in courses:
            if course.get('id') == course_id:
                return course
        return None
    
    def get_course_chapters(self, course_id: int) -> Optional[list]:
        """
        获取课程章节列表
        
        Args:
            course_id: 课程ID
            
        Returns:
            Optional[list]: 章节列表，失败时返回None
        """
        if not self.is_logged_in():
            print("请先登录")
            return None
            
        url = f"{self.base_url}/cgi-bin/api/lessons/student-mobile/course/catalogue/{course_id}"
        params = {"id": course_id}
        
        # 添加token到请求头 - 使用Studenttoken
        headers = {"Studenttoken": self.token}
        
        try:
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success') and data.get('code') == 0:
                chapters = data.get('data', [])
                print(f"成功获取到 {len(chapters)} 个章节")
                return chapters
            else:
                print(f"获取章节列表失败: {data.get('message', '未知错误')}")
                return None
                
        except requests.RequestException as e:
            print(f"网络请求失败: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"响应解析失败: {str(e)}")
            return None
    
    def display_chapters(self, chapters: list) -> None:
        """
        显示章节列表（支持嵌套结构）
        
        Args:
            chapters: 章节列表
        """
        if not chapters:
            print("没有章节数据")
            return
            
        print("\n" + "="*100)
        print("章节列表")
        print("="*100)
        
        self._display_chapters_recursive(chapters, 0)
    
    def _display_chapters_recursive(self, chapters: list, level: int = 0) -> None:
        """
        递归显示章节列表
        
        Args:
            chapters: 章节列表
            level: 缩进级别
        """
        indent = "  " * level
        
        for i, chapter in enumerate(chapters, 1):
            duration = chapter.get('duration', 0)
            duration_min = duration // 60 if duration else 0
            duration_sec = duration % 60 if duration else 0
            
            # 显示章节信息
            if level == 0:
                print(f"{i:2d}. {chapter.get('name', '未知章节') or '第' + str(i) + '章'}")
            else:
                print(f"{indent}{i:2d}. {chapter.get('name', '未知章节')}")
            
            print(f"{indent}    章节ID: {chapter.get('id', '未知')}")
            if duration:
                print(f"{indent}    时长: {duration_min}分{duration_sec}秒 ({duration}秒)")
            else:
                print(f"{indent}    类型: {chapter.get('dirName', '未知')}")
            print(f"{indent}    是否完成: {'是' if chapter.get('isPlayFinish') else '否'}")
            print(f"{indent}    是否可播放: {'是' if chapter.get('isPlay') else '否'}")
            print(f"{indent}    是否免费: {'是' if chapter.get('isFree') else '否'}")
            
            # 如果有子章节，递归显示
            children = chapter.get('children')
            if children:
                print(f"{indent}    子章节:")
                self._display_chapters_recursive(children, level + 1)
            
            print("-" * 100)
    
    def extract_learnable_chapters(self, chapters: list) -> list:
        """
        提取所有可学习的章节（包括嵌套结构中的子章节）
        按顺序处理，确保学习顺序正确
        
        Args:
            chapters: 章节列表
            
        Returns:
            list: 可学习的章节列表（按顺序排列）
        """
        learnable_chapters = []
        
        for chapter in chapters:
            # 检查是否有子章节
            children = chapter.get('children')
            if children:
                # 如果有子章节，递归提取（保持顺序）
                learnable_chapters.extend(self.extract_learnable_chapters(children))
            else:
                # 如果没有子章节，检查是否可学习
                duration = chapter.get('duration', 0)
                arrange_id = chapter.get('arrangeId')
                is_play = chapter.get('isPlay', False)
                is_play_finish = chapter.get('isPlayFinish', False)
                
                # 只学习有duration和arrangeId的章节
                if duration and arrange_id:
                    # 如果已完成，跳过
                    if is_play_finish:
                        print(f"跳过已完成的章节: {chapter.get('name', '未知章节')}")
                        continue
                    # 如果可播放，添加到学习列表
                    elif is_play:
                        learnable_chapters.append(chapter)
                    # 如果不可播放，说明需要先完成前面的章节
                    else:
                        print(f"跳过不可播放的章节（需要先完成前面的）: {chapter.get('name', '未知章节')}")
                        # 继续处理后续章节，但不会学习这个章节
        
        return learnable_chapters
    
    def submit_study_time(self, course_id: str, course_arrange_id: int, duration: int) -> bool:
        """
        提交学习时长
        
        Args:
            course_id: 课程ID (字符串)
            course_arrange_id: 课程安排ID
            duration: 视频时长(秒)
            
        Returns:
            bool: 提交是否成功
        """
        if not self.is_logged_in():
            print("请先登录")
            return False
            
        url = f"{self.base_url}/cgi-bin/api/lessons/student-mobile/course/updatePlay"
        
        # 设置请求头 - 使用与curl命令相同的格式
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://cqwlxycrjy.wdxuetang.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://cqwlxycrjy.wdxuetang.cn/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Studenttoken': self.token,  # 使用Studenttoken而不是token
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',
            'sec-ch-ua': '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        # 提交数据 - 根据测试结果修正参数
        data = {
            "courseArrangeId": int(course_arrange_id),  # 确保是整数
            "courseId": str(course_id),  # 确保是字符串
            "lastPlayTime": int(duration),  # 视频总长度
            "playTime": int(duration),  # 视频总长度
            "incrementalTime": 0,  # 必须为0
            "timePoint": int(duration)  # 视频总长度
        }
        
        # 添加调试信息
        print(f"调试信息 - 课程ID: {course_id}, 安排ID: {course_arrange_id}, 时长: {duration}")
        print(f"调试信息 - 请求数据: {data}")
        
        try:
            response = self.session.post(url, headers=headers, json=data)
            print(f"调试信息 - 响应状态码: {response.status_code}")
            
            # 打印响应内容用于调试
            response_text = response.text
            print(f"调试信息 - 响应内容: {response_text}")
            
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success') and result.get('code') == 0:
                print(f"成功提交学习时长: {duration}秒")
                return True
            else:
                print(f"提交学习时长失败: {result.get('message', '未知错误')}")
                print(f"完整响应: {result}")
                return False
                
        except requests.RequestException as e:
            print(f"网络请求失败: {str(e)}")
            return False
        except json.JSONDecodeError as e:
            print(f"响应解析失败: {str(e)}")
            print(f"原始响应: {response_text}")
            return False
    
    def complete_chapter(self, course_id: str, course_arrange_id: int, duration: int) -> bool:
        """
        完成单个章节
        
        Args:
            course_id: 课程ID (字符串)
            course_arrange_id: 课程安排ID
            duration: 视频时长(秒)
            
        Returns:
            bool: 完成是否成功
        """
        print(f"正在完成章节 {course_arrange_id}...")
        return self.submit_study_time(course_id, course_arrange_id, duration)
    
    def complete_all_chapters(self, course_id: int) -> bool:
        """
        完成课程的所有章节（支持嵌套结构和学习顺序限制）
        
        Args:
            course_id: 课程ID
            
        Returns:
            bool: 是否全部完成成功
        """
        if not self.is_logged_in():
            print("请先登录")
            return False
        
        print(f"开始完成课程 {course_id} 的所有章节...")
        total_completed = 0
        max_attempts = 50  # 防止无限循环
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            print(f"\n--- 第 {attempt} 轮学习 ---")
            
            # 重新获取章节列表（获取最新状态）
            chapters = self.get_course_chapters(course_id)
            if not chapters:
                print("无法获取章节列表")
                return False
            
            # 提取当前可学习的章节
            learnable_chapters = self.extract_learnable_chapters(chapters)
            
            if not learnable_chapters:
                print("没有更多可学习的章节，学习完成！")
                break
            
            print(f"本轮找到 {len(learnable_chapters)} 个可学习的章节")
            
            # 只学习第一个可学习的章节（按顺序）
            chapter = learnable_chapters[0]
            chapter_id = chapter.get('arrangeId')
            duration = chapter.get('duration', 0)
            chapter_name = chapter.get('name', '未知章节')
            
            print(f"学习章节: {chapter_name}")
            
            if self.complete_chapter(str(course_id), chapter_id, duration):
                total_completed += 1
                print(f"章节 {chapter_name} 学习完成")
            else:
                print(f"章节 {chapter_name} 学习失败")
                break
        
        if attempt >= max_attempts:
            print(f"达到最大尝试次数 ({max_attempts})，停止学习")
        
        print(f"总共完成 {total_completed} 个章节")
        return total_completed > 0
    
    def test_single_chapter(self, course_id: int, chapter_index: int = 0) -> bool:
        """
        测试完成单个章节（用于调试，支持嵌套结构）
        
        Args:
            course_id: 课程ID
            chapter_index: 章节索引（从0开始）
            
        Returns:
            bool: 是否成功
        """
        if not self.is_logged_in():
            print("请先登录")
            return False
            
        # 获取章节列表
        chapters = self.get_course_chapters(course_id)
        if not chapters:
            print("无法获取章节列表")
            return False
        
        # 提取所有可学习的章节
        learnable_chapters = self.extract_learnable_chapters(chapters)
        
        if not learnable_chapters or chapter_index >= len(learnable_chapters):
            print("无法获取可学习章节或索引超出范围")
            return False
        
        chapter = learnable_chapters[chapter_index]
        chapter_id = chapter.get('arrangeId')  # 使用arrangeId
        duration = chapter.get('duration', 0)
        chapter_name = chapter.get('name', '未知章节')
        
        print(f"测试章节: {chapter_name}")
        print(f"章节ID: {chapter_id}, 时长: {duration}秒")
        
        return self.complete_chapter(str(course_id), chapter_id, duration)
    
    def complete_all_courses(self) -> bool:
        """
        完成所有课程的所有章节
        
        Returns:
            bool: 是否全部完成成功
        """
        if not self.is_logged_in():
            print("请先登录")
            return False
            
        # 获取课程列表
        courses = self.get_my_courses()
        if not courses:
            print("无法获取课程列表")
            return False
        
        print(f"开始完成所有课程的学习...")
        total_courses = len(courses)
        completed_courses = 0
        
        for i, course in enumerate(courses, 1):
            course_id = course.get('id')
            course_name = course.get('name', '未知课程')
            progress = course.get('finishRate', 0)
            
            print(f"\n[{i}/{total_courses}] 处理课程: {course_name} (当前进度: {progress}%)")
            
            if progress >= 100:
                print(f"课程 {course_name} 已完成，跳过")
                completed_courses += 1
                continue
            
            # 完成该课程的所有章节
            if self.complete_all_chapters(course_id):
                completed_courses += 1
                print(f"课程 {course_name} 学习完成")
            else:
                print(f"课程 {course_name} 学习失败")
        
        print(f"\n完成进度: {completed_courses}/{total_courses} 门课程")
        return completed_courses == total_courses


def main():
    """主函数示例"""
    # 创建会话对象
    session = WdxuetangSession()
    
    # 用户输入账号密码
    account = input("请输入账号: ").strip()
    password = input("请输入密码: ").strip()
    
    if not account or not password:
        print("账号和密码不能为空")
        return
    
    # 自动登录（无需手动输入验证码）
    if session.auto_login(account, password):
        print("登录成功，可以继续使用其他API功能")
        
        # 获取并显示课程列表
        print("\n正在获取课程列表...")
        session.display_courses()
        
        # 让用户选择学习方式
        print("\n请选择学习方式:")
        print("1. 学习单个课程")
        print("2. 学习所有课程")
        print("3. 只查看课程列表，不学习")
        
        main_choice = input("请输入选择 (1/2/3): ").strip()
        
        if main_choice == '1':
            # 学习单个课程
            print("\n请选择要学习的课程:")
            courses = session.get_my_courses()
            if courses:
                # 显示课程选择菜单
                for i, course in enumerate(courses, 1):
                    progress = course.get('finishRate', 0)
                    print(f"{i:2d}. {course.get('name', '未知课程')} - 进度: {progress}%")
                
                try:
                    course_choice = int(input("\n请输入课程编号: ")) - 1
                    if 0 <= course_choice < len(courses):
                        selected_course = courses[course_choice]
                        course_id = selected_course.get('id')
                        course_name = selected_course.get('name', '未知课程')
                        
                        print(f"\n已选择课程: {course_name} (ID: {course_id})")
                        
                        # 直接开始学习该课程的所有章节
                        print("开始学习该课程的所有章节...")
                        session.complete_all_chapters(course_id)
                    else:
                        print("无效的课程编号")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("无法获取课程列表")
                
        elif main_choice == '2':
            # 学习所有课程
            print("\n开始学习所有课程...")
            session.complete_all_courses()
            
        elif main_choice == '3':
            print("已显示课程列表，未进行学习")
        else:
            print("无效选择")
    else:
        print("登录失败")


if __name__ == "__main__":
    main()

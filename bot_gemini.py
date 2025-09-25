import random
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import google.generativeai as genai
import time

# 已移除 generate_answer 函式，改用專門的 answer_likert_question 和 answer_multiple_choice_question

def click_element(driver, xpath):
    """點擊元素的通用函數"""
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
        return True
    except Exception:
        return False

def answer_likert_question(driver, question, question_number):
    """處理李克特量表問題（第一頁）"""
    # 李克特量表選項固定為：非常同意(5), 同意(4), 普通(3), 不同意(2), 非常不同意(1)
    # 統一使用"普通"選項，對應 value="3"，id 為 q_X_3
    
    try:
        print(f"問題 {question_number}: {question}")
        print(f"選擇答案: 普通")
        
        # 直接點擊"普通"選項 (value="3")
        radio_id = f"q_{question_number}_3"
        if click_element(driver, f"//input[@id='{radio_id}']"):
            return
        
        # 如果無法點擊，嘗試備選方法
        print(f"嘗試備選點擊方法...")
        click_element(driver, f"//div[@id='div_q_{question_number}']//input[@value='3']")
        
    except Exception as e:
        print(f"處理問題時出錯: {e}，使用備選方法")
        # 備選方法：直接通過 value 屬性點擊
        click_element(driver, f"//div[@id='div_q_{question_number}']//input[@value='3']")

def answer_multiple_choice_question(driver, question, options, question_number):
    """處理選擇題問題（第二頁）"""
    try:
        prompt = f"這是一個數位素養測驗題目，請選擇正確答案：\n問題: {question}\n選項: {', '.join(options)}\n只返回正確選項的內容，不要其他說明。"
        response = genai.GenerativeModel('gemini-2.5-flash-lite').generate_content(prompt)
        answer = response.text.strip()
        print(f"問題 {question_number}: {question}")
        print(f"AI 回答: {answer}")
        print(f"可選選項: {options}")
        
        # 嘗試點擊對應答案
        for i, option in enumerate(options, 1):
            # 更寬鬆的匹配邏輯
            clean_answer = answer.replace(' ', '').replace('\n', '').replace('。', '').lower()
            clean_option = option.replace(' ', '').replace('\n', '').replace('。', '').lower()
            
            if clean_answer in clean_option or clean_option in clean_answer:
                radio_id = f"q_{question_number}_{i}"
                if click_element(driver, f"//input[@id='{radio_id}']"):
                    return
                    
            # 也嘗試部分關鍵字匹配
            answer_words = answer.split()
            if len(answer_words) > 2:  # 如果答案有多個詞
                main_keywords = [word for word in answer_words if len(word) > 2]
                if any(keyword in option for keyword in main_keywords):
                    radio_id = f"q_{question_number}_{i}"
                    if click_element(driver, f"//input[@id='{radio_id}']"):
                        return
        
        # 如果找不到匹配的答案，隨機選擇
        random_choice = random.randint(1, len(options))
        click_element(driver, f"//input[@id='q_{question_number}_{random_choice}']")
        print(f"使用隨機答案: {options[random_choice-1]}")
        
    except Exception as e:
        print(f"處理問題時出錯: {e}，使用隨機答案")
        random_choice = random.randint(1, len(options))
        click_element(driver, f"//input[@id='q_{question_number}_{random_choice}']")

def complete_quiz(driver):
    """完成一次測驗（處理兩頁測驗）"""
    driver.get('https://isafeevent.moe.edu.tw/exam/')
    
    # 點擊開始按鈕
    if not click_element(driver, "//button[contains(@class, 'btnStartExam')]"):
        print("❌ 無法找到開始按鈕")
        return False
    
    time.sleep(2)
    
    # 第一頁：處理李克特量表題目（1-16題）
    print("\n" + "="*50)
    print("📝 開始處理第一頁（李克特量表）...")
    print("="*50)
    
    for i in range(1, 17):
        try:
            div = driver.find_element(By.ID, f'div_q_{i}')
            question_text = div.find_element(By.TAG_NAME, 'h4').text
            # 清理問題文字，移除題號部分
            question = question_text.split('/', 1)[1].strip() if '/' in question_text else question_text
            answer_likert_question(driver, question, i)
            time.sleep(0.5)  # 短暫延遲避免過快操作
        except Exception as e:
            print(f"❌ 處理第一頁第 {i} 題時出錯: {e}")
    
    # 提交第一頁答案
    print("\n📤 提交第一頁答案...")
    if not click_element(driver, "//button[contains(@class, 'btnSendExam')]"):
        print("❌ 無法點擊第一頁送出按鈕")
        return False
    
    time.sleep(3)  # 等待頁面跳轉
    
    # 第二頁：處理選擇題（1-16題）
    print("\n" + "="*50)
    print("🤖 開始處理第二頁（選擇題）- 使用 Gemini 2.5 Flash Lite...")
    print("="*50)
    
    for i in range(1, 17):
        try:
            div = driver.find_element(By.ID, f'div_q_{i}')
            question_text = div.find_element(By.TAG_NAME, 'h4').text
            # 清理問題文字，移除題號部分
            question = question_text.split('/', 1)[1].strip() if '/' in question_text else question_text
            
            # 獲取選擇題選項
            option_labels = div.find_elements(By.CSS_SELECTOR, ".form-check-label")
            options = [opt.text.strip() for opt in option_labels if opt.text.strip()]
            
            answer_multiple_choice_question(driver, question, options, i)
            time.sleep(0.8)  # 稍微延長延遲避免 API 限制
        except Exception as e:
            print(f"❌ 處理第二頁第 {i} 題時出錯: {e}")
    
    # 提交第二頁答案（完成測驗）
    print("\n🎯 提交第二頁答案，完成測驗...")
    if not click_element(driver, "//button[contains(@class, 'btnSendExam')]"):
        print("❌ 無法點擊第二頁送出按鈕")
        return False
    
    time.sleep(2)
    return True

def main():
    # 初始化
    print("🤖 2025年數位素養自動答題腳本 (Gemini 版本)")
    print("📋 本腳本支援兩頁測驗格式：")
    print("   - 第一頁：16題李克特量表（統一選擇「普通」）")
    print("   - 第二頁：16題選擇題（使用 Gemini 2.5 Flash Lite 智能答題）")
    print("-" * 60)
    
    # 初始化瀏覽器
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir=C:/temp/chrome-profile")
    # chrome_options.add_argument("--headless")  # 如需無頭模式可取消註解
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.get("https://isafeevent.moe.edu.tw/")
    
    # 設定
    print("請在瀏覽器中完成登入操作，完成後按下 Enter 鍵繼續...")
    input()
    
    genai.configure(api_key=input("輸入 Gemini API 金鑰: "))
    attempts = int(input("輸入要重複答題的次數: "))
    delay = int(input("輸入每次答題完成後的等待秒數: "))
    
    # 主循環
    success_count = 0
    for i in range(attempts):
        try:
            print(f"\n{'🎯'*20}")
            print(f"🚀 開始第 {i + 1} 次答題（共 {attempts} 次）...")
            print(f"{'🎯'*20}")
            
            if complete_quiz(driver):
                success_count += 1
                print(f"✅ 第 {i + 1} 次答題完成！成功率: {success_count}/{i+1}")
            else:
                print(f"❌ 第 {i + 1} 次答題失敗")
            
            if i < attempts - 1:  # 不是最後一次才等待
                print(f"⏸ 等待 {delay} 秒後開始下一次答題...")
                time.sleep(delay)
        except Exception as e:
            print(f"💥 錯誤: {e}")
            print("⏸ 等待 30 秒後重試...")
            time.sleep(30)
    
    print(f"\n🎊 所有答題完成！")
    print(f"📊 總共完成 {success_count}/{attempts} 次答題")
    print(f"📈 成功率: {(success_count/attempts)*100:.1f}%")
    print("\n按下 Enter 鍵關閉瀏覽器...")
    input()
    driver.quit()

if __name__ == "__main__":
    main()
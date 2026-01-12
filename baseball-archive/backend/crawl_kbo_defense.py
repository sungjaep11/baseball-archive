"""
KBO 수비 기록 크롤링 스크립트 (포지션 정보 수집)
https://www.koreabaseball.com/Record/Player/Defense/Basic.aspx
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os

def setup_driver(headless=False):
    """Chrome 드라이버 설정 (자동 설치)"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def crawl_page(driver, page_num):
    """특정 페이지의 수비 기록 크롤링 (선수명 + 포지션만)"""
    print(f"📄 {page_num}페이지 크롤링 중...")
    
    # 한글 포지션 → 영문 포지션 매핑
    position_mapping = {
        '포수': 'C',
        '1루수': '1B',
        '2루수': '2B',
        '3루수': '3B',
        '유격수': 'SS',
        '좌익수': 'LF',
        '중견수': 'CF',
        '우익수': 'RF',
        '지명타자': 'DH',
    }
    
    wait = WebDriverWait(driver, 15)
    
    # 테이블 찾기
    table_selectors = [
        "table.tData",
        "table[summary='수비 기록']",
        "div.record_result table",
    ]
    
    table = None
    for selector in table_selectors:
        try:
            table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            print(f"  ✓ 테이블 발견: {selector}")
            break
        except:
            continue
    
    if not table:
        print("  ❌ 테이블을 찾을 수 없습니다.")
        with open('backend/data/debug_defense_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        raise Exception("테이블을 찾을 수 없습니다.")
    
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    
    page_data = []
    for row in rows:
        try:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 4:  # 순위, 선수명, 팀명, POS 최소 필요
                position_kr = cols[3].text.strip()  # 한글 포지션
                position_en = position_mapping.get(position_kr, '')  # 영문 포지션 변환
                
                player_data = {
                    '순위': cols[0].text.strip(),
                    '선수명': cols[1].text.strip(),
                    '팀명': cols[2].text.strip(),
                    '포지션': position_kr,  # 한글 포지션
                    '포지션_영문': position_en,  # 영문 포지션
                }
                page_data.append(player_data)
                print(f"  ✓ {player_data['선수명']} ({player_data['팀명']}) - {player_data['포지션']} ({position_en})")
        except Exception as e:
            continue
    
    return page_data

def click_next_page(driver, page_num):
    """다음 페이지 버튼 클릭"""
    try:
        paging_selectors = [
            "div.paging a",
            "div.paging-wrap a",
        ]
        
        page_buttons = []
        for selector in paging_selectors:
            page_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            if page_buttons:
                break
        
        if not page_buttons:
            return False
        
        for button in page_buttons:
            if button.text.strip() == str(page_num):
                print(f"🔄 {page_num}페이지로 이동 중...")
                driver.execute_script("arguments[0].click();", button)
                time.sleep(3)
                return True
        
        return False
    except Exception as e:
        print(f"❌ 페이지 이동 실패: {e}")
        return False

def main():
    """메인 크롤링 함수"""
    print("=" * 60)
    print("🛡️  KBO 수비 기록 크롤링 (포지션 정보)")
    print("=" * 60)
    
    url = "https://www.koreabaseball.com/Record/Player/Defense/Basic.aspx"
    
    driver = None
    all_data = []
    
    try:
        driver = setup_driver(headless=False)
        driver.get(url)
        print(f"✅ 페이지 로드 완료: {url}\n")
        
        print("⏳ 페이지 로딩 대기 중...")
        time.sleep(5)
        
        # 1페이지 크롤링
        page_1_data = crawl_page(driver, 1)
        all_data.extend(page_1_data)
        print(f"✅ 1페이지 완료: {len(page_1_data)}명\n")
        
        # 2~5페이지 크롤링
        for page_num in range(2, 6):
            if click_next_page(driver, page_num):
                page_data = crawl_page(driver, page_num)
                all_data.extend(page_data)
                print(f"✅ {page_num}페이지 완료: {len(page_data)}명\n")
            else:
                print(f"⚠️ {page_num}페이지 이동 실패\n")
                break
        
        # 데이터프레임 생성
        df = pd.DataFrame(all_data)
        
        # 중복 제거 (같은 선수가 여러 포지션에 있을 수 있음 - 최초 포지션만 유지)
        df = df.drop_duplicates(subset=['선수명', '팀명'], keep='first')
        
        # 데이터 폴더 생성
        os.makedirs('backend/data', exist_ok=True)
        
        # CSV 저장
        output_csv = 'backend/data/kbo_defense_positions.csv'
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print("=" * 60)
        print(f"✅ CSV 저장 완료: {output_csv}")
        print(f"📊 총 {len(df)}명의 선수 포지션 정보 수집")
        print("=" * 60)
        
        # 엑셀 저장
        output_excel = 'backend/data/kbo_defense_positions.xlsx'
        df.to_excel(output_excel, index=False, engine='openpyxl')
        print(f"✅ Excel 저장 완료: {output_excel}")
        print("=" * 60)
        
        # 포지션별 통계
        print("\n📊 포지션별 선수 수:")
        position_counts = df['포지션'].value_counts()
        for pos, count in position_counts.items():
            print(f"  {pos}: {count}명")
        
        # 데이터 미리보기
        print("\n📋 수집된 데이터 미리보기:")
        print(df.head(20).to_string(index=False))
        
    except Exception as e:
        print(f"❌ 크롤링 오류: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("\n✅ 브라우저 종료")

if __name__ == "__main__":
    main()


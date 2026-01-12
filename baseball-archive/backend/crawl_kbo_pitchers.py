"""
KBO 투수 기록 크롤링 스크립트
https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx
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
        chrome_options.add_argument('--headless')  # 브라우저 창 숨기기
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    # Chrome 드라이버 자동 설치 및 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def crawl_page(driver, page_num):
    """특정 페이지의 투수 기록 크롤링"""
    print(f"📄 {page_num}페이지 크롤링 중...")
    
    # 테이블 로딩 대기 (여러 셀렉터 시도)
    wait = WebDriverWait(driver, 15)
    
    # KBO 페이지의 실제 테이블 구조를 찾기 위해 여러 셀렉터 시도
    table_selectors = [
        "table.tData",
        "table[summary='투수 기본 기록']",
        "table.table_basic",
        "div.record_result table",
        "#cphContents_cphContents_cphContents_udpContent table"
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
        print("  ❌ 테이블을 찾을 수 없습니다. 페이지 소스 저장 중...")
        with open('backend/data/debug_pitcher_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        raise Exception("테이블을 찾을 수 없습니다. debug_pitcher_page_source.html 파일을 확인하세요.")
    
    # 테이블 데이터 파싱 (tbody tr 찾기)
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    
    page_data = []
    for row in rows:
        try:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 19:  # 투수 기록은 19개 컬럼 (순위~WHIP)
                player_data = {
                    '순위': cols[0].text.strip(),
                    '선수명': cols[1].text.strip(),
                    '팀명': cols[2].text.strip(),
                    'ERA': cols[3].text.strip(),
                    'G': cols[4].text.strip(),
                    'W': cols[5].text.strip(),
                    'L': cols[6].text.strip(),
                    'SV': cols[7].text.strip(),
                    'HLD': cols[8].text.strip(),
                    'WPCT': cols[9].text.strip(),
                    'IP': cols[10].text.strip(),
                    'H': cols[11].text.strip(),
                    'HR': cols[12].text.strip(),
                    'BB': cols[13].text.strip(),
                    'HBP': cols[14].text.strip(),
                    'SO': cols[15].text.strip(),
                    'R': cols[16].text.strip(),
                    'ER': cols[17].text.strip(),
                    'WHIP': cols[18].text.strip(),
                }
                
                page_data.append(player_data)
                print(f"  ✓ {player_data['순위']}위: {player_data['선수명']} ({player_data['팀명']}) - {player_data['G']}G, ERA {player_data['ERA']}, {player_data['W']}승")
        except Exception as e:
            print(f"  ⚠️ 행 파싱 실패: {e}")
            continue
    
    return page_data

def click_next_page(driver, page_num):
    """다음 페이지 버튼 클릭"""
    try:
        # 여러 페이징 셀렉터 시도
        paging_selectors = [
            "div.paging a",
            "div.paging-wrap a",
            "div.page-navigation a",
            ".paging a"
        ]
        
        page_buttons = []
        for selector in paging_selectors:
            page_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            if page_buttons:
                break
        
        if not page_buttons:
            print(f"⚠️ 페이징 버튼을 찾을 수 없습니다.")
            return False
        
        for button in page_buttons:
            if button.text.strip() == str(page_num):
                print(f"🔄 {page_num}페이지로 이동 중...")
                driver.execute_script("arguments[0].click();", button)
                time.sleep(3)  # 페이지 로딩 대기
                return True
        
        return False
    except Exception as e:
        print(f"❌ 페이지 이동 실패: {e}")
        return False

def main():
    """메인 크롤링 함수"""
    print("=" * 60)
    print("⚾ KBO 투수 기록 크롤링 시작")
    print("=" * 60)
    
    url = "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx?sort=GAME_CN"
    
    driver = None
    all_data = []
    
    try:
        # 드라이버 초기화 (디버그 모드: headless=False로 브라우저 보기)
        driver = setup_driver(headless=False)  # 디버깅용: 브라우저 창 표시
        driver.get(url)
        print(f"✅ 페이지 로드 완료: {url}\n")
        
        # 초기 로딩 대기 (JavaScript 로딩 시간 확보)
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
        
        # 데이터 폴더 생성 (없으면)
        os.makedirs('backend/data', exist_ok=True)
        
        # CSV 저장
        output_csv = 'backend/data/kbo_pitchers_top150.csv'
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print("=" * 60)
        print(f"✅ CSV 저장 완료: {output_csv}")
        print(f"📊 총 {len(all_data)}명의 투수 데이터 수집")
        print("=" * 60)
        
        # 엑셀 저장
        output_excel = 'backend/data/kbo_pitchers_top150.xlsx'
        df.to_excel(output_excel, index=False, engine='openpyxl')
        print(f"✅ Excel 저장 완료: {output_excel}")
        print("=" * 60)
        
        # 데이터 미리보기
        print("\n📋 수집된 데이터 미리보기:")
        print(df.head(10).to_string(index=False))
        print("\n...")
        print(df.tail(5).to_string(index=False))
        
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


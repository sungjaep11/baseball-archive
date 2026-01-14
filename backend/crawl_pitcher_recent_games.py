"""
KBO 투수 2025 성적 크롤링 스크립트
https://www.koreabaseball.com/Record/Player/PitcherDetail/Basic.aspx?playerId={id}
각 선수의 상세 페이지에서 "2025 성적" 테이블을 크롤링하여 DB에 저장
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pymysql
from pymysql.cursors import DictCursor
import time
from config.db_config import DB_CONFIG

# 선수 상세 페이지 URL 패턴
PITCHER_DETAIL_URL = "https://www.koreabaseball.com/Record/Player/PitcherDetail/Basic.aspx?playerId={id}"

def setup_driver(headless=True):
    """Chrome 드라이버 설정"""
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

def get_players_from_db():
    """
    kbo_pitchers_top150 테이블에서 선수명과 player_id를 가져옵니다.
    player_id가 있는 선수만 조회합니다.
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(DictCursor)
        
        # 선수명과 player_id 조회 (player_id가 NULL이 아닌 경우만)
        query = """
            SELECT DISTINCT `선수명`, `player_id`, `팀명`
            FROM `kbo_pitchers_top150`
            WHERE `player_id` IS NOT NULL AND `player_id` != ''
            ORDER BY `선수명`
        """
        cursor.execute(query)
        players = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print(f"✅ DB에서 {len(players)}명의 선수 조회 완료")
        return players
        
    except Exception as e:
        print(f"❌ DB 조회 오류: {e}")
        import traceback
        traceback.print_exc()
        return []

def crawl_recent_10_games(driver, player_id, player_name):
    """
    선수 상세 페이지에서 "최근 10경기" 테이블을 크롤링합니다.
    
    Args:
        driver: Selenium WebDriver
        player_id: 선수 ID (예: "76232")
        player_name: 선수명 (예: "류현진")
    
    Returns:
        list: 최근 10경기 기록 리스트 (각 경기는 딕셔너리)
    """
    try:
        # 1. 선수 상세 페이지로 이동
        detail_url = PITCHER_DETAIL_URL.format(id=player_id)
        driver.get(detail_url)
        print(f"  📄 {player_name} (ID: {player_id}) 상세 페이지 로딩 중...")
        time.sleep(2)  # 페이지 로딩 대기
        
        # 2. "최근 10경기" 테이블 찾기
        wait = WebDriverWait(driver, 10)
        
        # 여러 셀렉터 시도
        table_selectors = [
            "table.tData",
            "table[summary*='최근']",
            "table[summary*='10경기']",
            "div.record_result table",
            "table.table_basic",
            "//table[contains(., '최근 10경기')]",
            "//table[contains(., '일자')]"
        ]
        
        table = None
        for selector in table_selectors:
            try:
                if selector.startswith("//"):
                    # XPath 사용
                    table = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                else:
                    # CSS 셀렉터 사용
                    table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                
                # 테이블에 "최근 10경기" 또는 "일자" 컬럼이 있는지 확인
                table_text = table.text
                if '일자' in table_text or '최근' in table_text:
                    print(f"  ✓ 테이블 발견: {selector}")
                    break
            except Exception:
                continue
        
        if not table:
            print(f"  ⚠️ {player_name}: 최근 10경기 테이블을 찾을 수 없습니다.")
            return []
        
        # 3. 테이블 데이터 파싱
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        
        recent_games = []
        for row in rows:
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                
                # 최근 10경기 테이블 구조 (투수):
                # 일자, 상대, 결과, ERA, TBF, IP, H, HR, BB, HBP, SO, R, ER, AVG
                if len(cols) >= 10:  # 최소 컬럼 개수 확인
                    game_data = {
                        'player_id': player_id,
                        '선수명': player_name,
                        '일자': cols[0].text.strip() if len(cols) > 0 else '',
                        '상대': cols[1].text.strip() if len(cols) > 1 else '',
                        '결과': cols[2].text.strip() if len(cols) > 2 else '',
                        'ERA': cols[3].text.strip() if len(cols) > 3 else '',
                        'TBF': cols[4].text.strip() if len(cols) > 4 else '',
                        'IP': cols[5].text.strip() if len(cols) > 5 else '',
                        'H': cols[6].text.strip() if len(cols) > 6 else '',
                        'HR': cols[7].text.strip() if len(cols) > 7 else '',
                        'BB': cols[8].text.strip() if len(cols) > 8 else '',
                        'HBP': cols[9].text.strip() if len(cols) > 9 else '',
                        'SO': cols[10].text.strip() if len(cols) > 10 else '',
                        'R': cols[11].text.strip() if len(cols) > 11 else '',
                        'ER': cols[12].text.strip() if len(cols) > 12 else '',
                        'AVG': cols[13].text.strip() if len(cols) > 13 else '',
                    }
                    
                    # "합계" 행은 제외
                    if game_data['일자'] != '합계' and game_data['일자']:
                        recent_games.append(game_data)
                
            except Exception as e:
                print(f"  ⚠️ 행 파싱 실패: {e}")
                continue
        
        print(f"  ✅ {player_name}: {len(recent_games)}경기 데이터 수집 완료")
        return recent_games
        
    except Exception as e:
        print(f"  ❌ {player_name} (ID: {player_id}) 크롤링 오류: {e}")
        import traceback
        traceback.print_exc()
        return []

def create_pitcher_log_table(cursor, conn):
    """
    투수로그 테이블을 생성합니다.
    기존 테이블이 있으면 삭제하고 새로 생성합니다.
    """
    try:
        # 기존 테이블 삭제
        cursor.execute("DROP TABLE IF EXISTS `pitcher_recent_games_log`")
        conn.commit()
        print("✅ 기존 테이블 삭제 완료")
        
        # 새 테이블 생성
        create_table_query = """
        CREATE TABLE `pitcher_recent_games_log` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `player_id` VARCHAR(20) NOT NULL,
            `선수명` VARCHAR(50) NOT NULL,
            `일자` VARCHAR(20),
            `상대` VARCHAR(20),
            `결과` VARCHAR(20),
            `ERA` VARCHAR(10),
            `TBF` VARCHAR(10),
            `IP` VARCHAR(10),
            `H` VARCHAR(10),
            `HR` VARCHAR(10),
            `BB` VARCHAR(10),
            `HBP` VARCHAR(10),
            `SO` VARCHAR(10),
            `R` VARCHAR(10),
            `ER` VARCHAR(10),
            `AVG` VARCHAR(10),
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX `idx_player_id` (`player_id`),
            INDEX `idx_선수명` (`선수명`),
            INDEX `idx_일자` (`일자`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ 투수로그 테이블 생성 완료")
        
    except Exception as e:
        print(f"❌ 테이블 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        raise

def crawl_2025_score(driver, player_id, player_name, debug=False):
    """
    선수 상세 페이지에서 "2025 성적" 테이블을 크롤링합니다.
    
    Args:
        driver: Selenium WebDriver
        player_id: 선수 ID (예: "76232")
        player_name: 선수명 (예: "류현진")
        debug: 디버그 모드 (테이블 구조 출력)
    
    Returns:
        dict: 2025 성적 데이터 (딕셔너리)
    """
    try:
        # 1. 선수 상세 페이지로 이동
        detail_url = PITCHER_DETAIL_URL.format(id=player_id)
        driver.get(detail_url)
        print(f"  📄 {player_name} (ID: {player_id}) 2025 성적 크롤링 중...")
        time.sleep(2)  # 페이지 로딩 대기
        
        # 2. 페이지 로딩 대기 (테이블이 동적으로 로드될 수 있음)
        time.sleep(3)
        
        # 3. 모든 테이블 찾기 및 분석
        all_tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"  🔍 페이지에서 발견된 테이블 수: {len(all_tables)}")
        
        if debug and all_tables:
            for i, t in enumerate(all_tables):
                try:
                    table_text = t.text[:300]  # 처음 300자
                    summary = t.get_attribute('summary') or ''
                    class_name = t.get_attribute('class') or ''
                    print(f"    테이블 {i+1}:")
                    print(f"      - 클래스: {class_name}")
                    print(f"      - summary: {summary}")
                    print(f"      - 텍스트 일부: {table_text[:150]}...")
                except Exception as e:
                    print(f"    테이블 {i+1}: 정보 가져오기 실패 - {e}")
        
        # 4. "2025 성적" 테이블 찾기 - 모든 테이블을 직접 검사
        table = None
        
        # 방법 1: 모든 테이블을 순회하며 조건에 맞는 테이블 찾기
        for t in all_tables:
            try:
                table_text = t.text
                summary = t.get_attribute('summary') or ''
                class_name = t.get_attribute('class') or ''
                
                # 조건: "2025" 또는 "성적"이 포함되고, 투수 성적 관련 키워드가 있는 테이블
                has_year_or_score = '2025' in table_text or '성적' in table_text or '2025' in summary or '성적' in summary
                has_pitcher_stats = any(keyword in table_text for keyword in ['G', '경기', 'ERA', '평균자책점', 'IP', '이닝', 'W', '승', 'L', '패', 'SV', '세이브', 'SO', '삼진'])
                
                if has_year_or_score and has_pitcher_stats:
                    # 추가 확인: 헤더나 데이터 행이 있는지 확인
                    rows = t.find_elements(By.CSS_SELECTOR, "tbody tr, tr")
                    if len(rows) > 0:
                        table = t
                        print("  ✓ 2025 성적 테이블 발견! (텍스트 기반 검색)")
                        print(f"    - 클래스: {class_name}")
                        print(f"    - summary: {summary}")
                        print(f"    - 행 수: {len(rows)}")
                        break
            except Exception as e:
                if debug:
                    print(f"  ⚠️ 테이블 검사 중 오류: {e}")
                continue
        
        # 방법 2: 셀렉터 기반 검색 (방법 1이 실패한 경우)
        if not table:
            table_selectors = [
                "//table[contains(@summary, '2025')]",
                "//table[contains(@summary, '성적')]",
                "//table[contains(., '2025')]",
                "//table[contains(., '성적')]",
                "table[summary*='2025']",
                "table[summary*='성적']",
                "table.tData",
                "div.record_result table",
                "table.table_basic",
            ]
            
            for selector in table_selectors:
                try:
                    if selector.startswith("//"):
                        tables = driver.find_elements(By.XPATH, selector)
                    else:
                        tables = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for t in tables:
                        table_text = t.text
                        if any(keyword in table_text for keyword in ['G', '경기', 'ERA', '평균자책점', 'IP', '이닝', 'W', '승']):
                            rows = t.find_elements(By.CSS_SELECTOR, "tbody tr, tr")
                            if len(rows) > 0:
                                table = t
                                print(f"  ✓ 2025 성적 테이블 발견! (셀렉터: {selector})")
                                break
                    if table:
                        break
                except Exception as e:
                    if debug:
                        print(f"  ⚠️ 셀렉터 {selector} 시도 실패: {e}")
                    continue
        
        if not table:
            print(f"  ⚠️ {player_name}: 2025 성적 테이블을 찾을 수 없습니다.")
            print(f"  📝 페이지 제목: {driver.title}")
            print(f"  📝 현재 URL: {driver.current_url}")
            
            # 페이지 소스에서 "2025" 또는 "성적" 검색
            page_source = driver.page_source
            if '2025' in page_source or '성적' in page_source:
                print("  ✓ 페이지 소스에 '2025' 또는 '성적' 키워드가 포함되어 있습니다.")
                # 테이블 관련 HTML 일부 출력
                import re
                table_matches = re.findall(r'<table[^>]*>.*?</table>', page_source, re.DOTALL | re.IGNORECASE)
                print(f"  📊 발견된 <table> 태그 수: {len(table_matches)}")
                if table_matches:
                    for i, match in enumerate(table_matches[:3]):  # 처음 3개만
                        if '2025' in match or '성적' in match:
                            print(f"    테이블 {i+1} (일부): {match[:500]}...")
            else:
                print("  ⚠️ 페이지 소스에 '2025' 또는 '성적' 키워드가 없습니다.")
            
            if debug:
                # 페이지 소스 일부 저장
                with open(f'debug_page_pitcher_{player_id}.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print(f"  💾 디버그 파일 저장: debug_page_pitcher_{player_id}.html")
            
            return None
        
        # 5. 테이블 헤더 확인 (디버깅용)
        if debug:
            try:
                headers = table.find_elements(By.CSS_SELECTOR, "thead tr th, thead tr td")
                if headers:
                    header_texts = [h.text.strip() for h in headers]
                    print(f"  📋 테이블 헤더: {header_texts}")
                else:
                    # tbody의 첫 번째 행이 헤더일 수도 있음
                    first_row = table.find_elements(By.CSS_SELECTOR, "tbody tr")[0] if table.find_elements(By.CSS_SELECTOR, "tbody tr") else None
                    if first_row:
                        first_cols = first_row.find_elements(By.TAG_NAME, "th, td")
                        header_texts = [c.text.strip() for c in first_cols]
                        print(f"  📋 첫 번째 행 (헤더로 추정): {header_texts}")
            except Exception as e:
                print(f"  ⚠️ 헤더 확인 실패: {e}")
        
        # 6. 테이블 데이터 파싱
        # 2025 성적 테이블은 두 행으로 나뉘어져 있음:
        # 첫 번째 행: 팀명 | ERA | G | CG | SHO | W | L | SV | HLD | WPCT | TBF | NP | IP | H | 2B | 3B | HR
        # 두 번째 행: SAC | SF | BB | IBB | SO | WP | BK | R | ER | BSV | WHIP | AVG | QS
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        
        if debug:
            print(f"  📊 발견된 행 수: {len(rows)}")
            for i, row in enumerate(rows[:5]):  # 처음 5행만 출력
                cols = row.find_elements(By.TAG_NAME, "td, th")
                row_data = [c.text.strip() for c in cols]
                print(f"    행 {i+1}: {row_data}")
        
        # 데이터 행 찾기 (두 행을 합쳐서 파싱)
        score_data = None
        first_data_row = None
        second_data_row = None
        
        # 첫 번째 데이터 행 찾기 (팀명, ERA, G, CG, SHO, W, L, SV, HLD, WPCT, TBF, NP, IP, H, 2B, 3B, HR 포함)
        # 첫 번째 행 특징: 팀명으로 시작하고, 두 번째 컬럼이 ERA 값 (소수점 포함)
        for i, row in enumerate(rows):
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) < 15:  # 첫 번째 행은 최소 15개 컬럼
                    continue
                
                first_col_text = cols[0].text.strip() if len(cols) > 0 else ''
                second_col_text = cols[1].text.strip() if len(cols) > 1 else ''
                
                # 첫 번째 행 조건:
                # 1. 팀명으로 시작 (두산, KIA, 롯데, LG, SSG, 키움, NC, KT, 삼성, 한화)
                # 2. 두 번째 컬럼이 ERA 값 (소수점 포함 숫자, 예: "3.23")
                is_team_name = first_col_text in ['두산', 'KIA', '롯데', 'LG', 'SSG', '키움', 'NC', 'KT', '삼성', '한화']
                is_era_value = '.' in second_col_text and any(c.isdigit() for c in second_col_text.replace('.', ''))
                
                if is_team_name and is_era_value:
                    first_data_row = row
                    if debug:
                        print(f"  ✓ 첫 번째 데이터 행 발견 (행 {i+1}, 컬럼 수: {len(cols)})")
                        print(f"    첫 번째 컬럼: '{first_col_text}', 두 번째 컬럼: '{second_col_text}'")
                        print(f"    전체 데이터: {[c.text.strip() for c in cols[:10]]}")
                    break
            except Exception as e:
                if debug:
                    print(f"  ⚠️ 행 {i+1} 검사 중 오류: {e}")
                continue
        
        # 두 번째 데이터 행 찾기 (첫 번째 행 다음 행: SAC, SF, BB, IBB, SO, WP, BK, R, ER, BSV, WHIP, AVG, QS 포함)
        # 두 번째 행 특징: 첫 번째 컬럼이 숫자이고, 컬럼 수가 10개 이상 (보통 13개)
        if first_data_row:
            first_row_idx = rows.index(first_data_row)
            if debug:
                print(f"  🔍 첫 번째 행 인덱스: {first_row_idx}, 전체 행 수: {len(rows)}")
            
            # 첫 번째 행 다음부터 검색 (헤더 행이 있을 수 있으므로)
            for j in range(first_row_idx + 1, len(rows)):
                try:
                    second_row = rows[j]
                    cols = second_row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cols) < 10:  # 두 번째 행은 최소 10개 컬럼
                        continue
                    
                    first_col_text = cols[0].text.strip() if len(cols) > 0 else ''
                    
                    # 두 번째 행 조건:
                    # 1. 첫 번째 컬럼이 숫자 (SAC 값, 예: "5")
                    # 2. 컬럼 수가 10개 이상
                    is_first_col_numeric = first_col_text.isdigit() if first_col_text else False
                    has_enough_columns = len(cols) >= 10
                    
                    if is_first_col_numeric and has_enough_columns:
                        second_data_row = second_row
                        if debug:
                            print(f"  ✓ 두 번째 데이터 행 발견 (행 {j+1}, 컬럼 수: {len(cols)})")
                            print(f"    첫 번째 컬럼: '{first_col_text}', 두 번째 컬럼: '{cols[1].text.strip() if len(cols) > 1 else ''}'")
                            print(f"    전체 데이터: {[c.text.strip() for c in cols]}")
                        break
                except Exception as e:
                    if debug:
                        print(f"  ⚠️ 행 {j+1} 검사 중 오류: {e}")
                    continue
            
            if not second_data_row:
                if debug:
                    print(f"  ⚠️ 두 번째 데이터 행을 찾을 수 없습니다. (첫 번째 행 인덱스: {first_row_idx})")
                    # 모든 행 출력하여 디버깅
                    for k in range(first_row_idx + 1, min(first_row_idx + 5, len(rows))):
                        try:
                            test_row = rows[k]
                            test_cols = test_row.find_elements(By.TAG_NAME, "td")
                            print(f"    후보 행 {k+1}: 컬럼 수={len(test_cols)}, 첫 컬럼='{test_cols[0].text.strip() if len(test_cols) > 0 else ''}'")
                        except Exception:
                            pass
        else:
            if debug:
                print("  ⚠️ 첫 번째 데이터 행을 찾을 수 없어 두 번째 행을 찾을 수 없습니다.")
        
        # 두 행의 데이터를 합쳐서 score_data 생성
        if first_data_row:
            first_cols = first_data_row.find_elements(By.TAG_NAME, "td")
            second_cols = second_data_row.find_elements(By.TAG_NAME, "td") if second_data_row else []
            
            if debug:
                print(f"  📋 첫 번째 행 컬럼 수: {len(first_cols)}")
                print(f"  📋 두 번째 행 컬럼 수: {len(second_cols)}")
                if first_cols:
                    print(f"  📋 첫 번째 행 데이터: {[c.text.strip() for c in first_cols]}")
                if second_cols:
                    print(f"  📋 두 번째 행 데이터: {[c.text.strip() for c in second_cols]}")
            
            # 첫 번째 행 구조: 팀명(0) | ERA(1) | G(2) | CG(3) | SHO(4) | W(5) | L(6) | SV(7) | HLD(8) | WPCT(9) | TBF(10) | NP(11) | IP(12) | H(13) | 2B(14) | 3B(15) | HR(16)
            # 두 번째 행 구조: SAC(0) | SF(1) | BB(2) | IBB(3) | SO(4) | WP(5) | BK(6) | R(7) | ER(8) | BSV(9) | WHIP(10) | AVG(11) | QS(12)
            
            score_data = {
                'player_id': player_id,
                '선수명': player_name,
            }
            
            # 첫 번째 행에서 데이터 추출
            # 첫 번째 행 구조: 팀명(0) | ERA(1) | G(2) | CG(3) | SHO(4) | W(5) | L(6) | SV(7) | HLD(8) | WPCT(9) | TBF(10) | NP(11) | IP(12) | H(13) | 2B(14) | 3B(15) | HR(16)
            if len(first_cols) >= 17:
                score_data['ERA'] = first_cols[1].text.strip() if len(first_cols) > 1 else ''  # ERA는 두 번째 컬럼
                score_data['G'] = first_cols[2].text.strip() if len(first_cols) > 2 else ''
                score_data['CG'] = first_cols[3].text.strip() if len(first_cols) > 3 else ''
                score_data['SHO'] = first_cols[4].text.strip() if len(first_cols) > 4 else ''
                score_data['W'] = first_cols[5].text.strip() if len(first_cols) > 5 else ''
                score_data['L'] = first_cols[6].text.strip() if len(first_cols) > 6 else ''
                score_data['SV'] = first_cols[7].text.strip() if len(first_cols) > 7 else ''
                score_data['HLD'] = first_cols[8].text.strip() if len(first_cols) > 8 else ''
                score_data['WPCT'] = first_cols[9].text.strip() if len(first_cols) > 9 else ''
                score_data['TBF'] = first_cols[10].text.strip() if len(first_cols) > 10 else ''
                score_data['NP'] = first_cols[11].text.strip() if len(first_cols) > 11 else ''
                score_data['IP'] = first_cols[12].text.strip() if len(first_cols) > 12 else ''
                score_data['H'] = first_cols[13].text.strip() if len(first_cols) > 13 else ''
                score_data['2B'] = first_cols[14].text.strip() if len(first_cols) > 14 else ''
                score_data['3B'] = first_cols[15].text.strip() if len(first_cols) > 15 else ''
                score_data['HR'] = first_cols[16].text.strip() if len(first_cols) > 16 else ''
            elif len(first_cols) >= 10:
                # 컬럼 수가 적은 경우 (헤더 행이 포함되어 있을 수 있음)
                # ERA를 찾아서 인덱스 조정
                era_idx = None
                for idx, col in enumerate(first_cols):
                    if 'ERA' in col.text or ('.' in col.text.strip() and idx > 0):
                        era_idx = idx
                        break
                
                if era_idx is not None:
                    score_data['ERA'] = first_cols[era_idx].text.strip()
                    score_data['G'] = first_cols[era_idx + 1].text.strip() if len(first_cols) > era_idx + 1 else ''
                    score_data['CG'] = first_cols[era_idx + 2].text.strip() if len(first_cols) > era_idx + 2 else ''
                    score_data['SHO'] = first_cols[era_idx + 3].text.strip() if len(first_cols) > era_idx + 3 else ''
                    score_data['W'] = first_cols[era_idx + 4].text.strip() if len(first_cols) > era_idx + 4 else ''
                    score_data['L'] = first_cols[era_idx + 5].text.strip() if len(first_cols) > era_idx + 5 else ''
                    score_data['SV'] = first_cols[era_idx + 6].text.strip() if len(first_cols) > era_idx + 6 else ''
                    score_data['HLD'] = first_cols[era_idx + 7].text.strip() if len(first_cols) > era_idx + 7 else ''
                    score_data['WPCT'] = first_cols[era_idx + 8].text.strip() if len(first_cols) > era_idx + 8 else ''
                    score_data['TBF'] = first_cols[era_idx + 9].text.strip() if len(first_cols) > era_idx + 9 else ''
                    score_data['NP'] = first_cols[era_idx + 10].text.strip() if len(first_cols) > era_idx + 10 else ''
                    score_data['IP'] = first_cols[era_idx + 11].text.strip() if len(first_cols) > era_idx + 11 else ''
                    score_data['H'] = first_cols[era_idx + 12].text.strip() if len(first_cols) > era_idx + 12 else ''
                    score_data['2B'] = first_cols[era_idx + 13].text.strip() if len(first_cols) > era_idx + 13 else ''
                    score_data['3B'] = first_cols[era_idx + 14].text.strip() if len(first_cols) > era_idx + 14 else ''
                    score_data['HR'] = first_cols[era_idx + 15].text.strip() if len(first_cols) > era_idx + 15 else ''
            
            # 두 번째 행에서 데이터 추출
            # 두 번째 행 구조: SAC(0) | SF(1) | BB(2) | IBB(3) | SO(4) | WP(5) | BK(6) | R(7) | ER(8) | BSV(9) | WHIP(10) | AVG(11) | QS(12)
            # 두 번째 행이 있으면 무조건 추출 시도 (컬럼 수에 관계없이)
            if second_data_row and second_cols:
                if debug:
                    print(f"  🔍 두 번째 행 데이터 추출 시작 (컬럼 수: {len(second_cols)})")
                if len(second_cols) >= 13:
                    # 모든 컬럼이 있는 경우
                    score_data['SAC'] = second_cols[0].text.strip() if len(second_cols) > 0 else ''
                    score_data['SF'] = second_cols[1].text.strip() if len(second_cols) > 1 else ''
                    score_data['BB'] = second_cols[2].text.strip() if len(second_cols) > 2 else ''
                    score_data['IBB'] = second_cols[3].text.strip() if len(second_cols) > 3 else ''
                    score_data['SO'] = second_cols[4].text.strip() if len(second_cols) > 4 else ''
                    score_data['WP'] = second_cols[5].text.strip() if len(second_cols) > 5 else ''
                    score_data['BK'] = second_cols[6].text.strip() if len(second_cols) > 6 else ''
                    score_data['R'] = second_cols[7].text.strip() if len(second_cols) > 7 else ''
                    score_data['ER'] = second_cols[8].text.strip() if len(second_cols) > 8 else ''
                    score_data['BSV'] = second_cols[9].text.strip() if len(second_cols) > 9 else ''
                    score_data['WHIP'] = second_cols[10].text.strip() if len(second_cols) > 10 else ''
                    score_data['AVG'] = second_cols[11].text.strip() if len(second_cols) > 11 else ''
                    score_data['QS'] = second_cols[12].text.strip() if len(second_cols) > 12 else ''
                elif len(second_cols) >= 10:
                    # 컬럼 수가 10개 이상이지만 13개 미만인 경우 (일부 컬럼만 추출)
                    score_data['SAC'] = second_cols[0].text.strip() if len(second_cols) > 0 else ''
                    score_data['SF'] = second_cols[1].text.strip() if len(second_cols) > 1 else ''
                    score_data['BB'] = second_cols[2].text.strip() if len(second_cols) > 2 else ''
                    score_data['IBB'] = second_cols[3].text.strip() if len(second_cols) > 3 else ''
                    score_data['SO'] = second_cols[4].text.strip() if len(second_cols) > 4 else ''
                    if len(second_cols) > 5:
                        score_data['WP'] = second_cols[5].text.strip()
                    if len(second_cols) > 6:
                        score_data['BK'] = second_cols[6].text.strip()
                    if len(second_cols) > 7:
                        score_data['R'] = second_cols[7].text.strip()
                    if len(second_cols) > 8:
                        score_data['ER'] = second_cols[8].text.strip()
                    if len(second_cols) > 9:
                        score_data['BSV'] = second_cols[9].text.strip()
                    if len(second_cols) > 10:
                        score_data['WHIP'] = second_cols[10].text.strip()
                    if len(second_cols) > 11:
                        score_data['AVG'] = second_cols[11].text.strip()
                    if len(second_cols) > 12:
                        score_data['QS'] = second_cols[12].text.strip()
                elif len(second_cols) >= 5:
                    # 최소한 주요 데이터는 추출
                    if len(second_cols) > 0:
                        score_data['SAC'] = second_cols[0].text.strip()
                    if len(second_cols) > 1:
                        score_data['SF'] = second_cols[1].text.strip()
                    if len(second_cols) > 2:
                        score_data['BB'] = second_cols[2].text.strip()
                    if len(second_cols) > 3:
                        score_data['IBB'] = second_cols[3].text.strip()
                    if len(second_cols) > 4:
                        score_data['SO'] = second_cols[4].text.strip()
                    if len(second_cols) > 5:
                        score_data['WP'] = second_cols[5].text.strip()
                    if len(second_cols) > 6:
                        score_data['BK'] = second_cols[6].text.strip()
                    if len(second_cols) > 7:
                        score_data['R'] = second_cols[7].text.strip()
                    if len(second_cols) > 8:
                        score_data['ER'] = second_cols[8].text.strip()
                    if len(second_cols) > 9:
                        score_data['BSV'] = second_cols[9].text.strip()
                    if len(second_cols) > 10:
                        score_data['WHIP'] = second_cols[10].text.strip()
                    if len(second_cols) > 11:
                        score_data['AVG'] = second_cols[11].text.strip()
                    if len(second_cols) > 12:
                        score_data['QS'] = second_cols[12].text.strip()
                else:
                    # 컬럼 수가 5개 미만이어도 가능한 것만 추출
                    if len(second_cols) > 0:
                        score_data['SAC'] = second_cols[0].text.strip()
                    if len(second_cols) > 1:
                        score_data['SF'] = second_cols[1].text.strip()
                    if len(second_cols) > 2:
                        score_data['BB'] = second_cols[2].text.strip()
                    if len(second_cols) > 3:
                        score_data['IBB'] = second_cols[3].text.strip()
                    if len(second_cols) > 4:
                        score_data['SO'] = second_cols[4].text.strip()
                
                if debug:
                    print("  📊 두 번째 행에서 추출된 데이터:")
                    print(f"    SAC={score_data.get('SAC', 'N/A')}, SF={score_data.get('SF', 'N/A')}, BB={score_data.get('BB', 'N/A')}, IBB={score_data.get('IBB', 'N/A')}")
                    print(f"    SO={score_data.get('SO', 'N/A')}, WP={score_data.get('WP', 'N/A')}, BK={score_data.get('BK', 'N/A')}")
                    print(f"    R={score_data.get('R', 'N/A')}, ER={score_data.get('ER', 'N/A')}, BSV={score_data.get('BSV', 'N/A')}")
                    print(f"    WHIP={score_data.get('WHIP', 'N/A')}, AVG={score_data.get('AVG', 'N/A')}, QS={score_data.get('QS', 'N/A')}")
            elif second_data_row and not second_cols:
                if debug:
                    print("  ⚠️ 두 번째 행은 찾았지만 컬럼을 추출할 수 없습니다.")
            else:
                if debug:
                    print("  ⚠️ 두 번째 행을 찾을 수 없습니다.")
        
        if score_data:
            if debug:
                print("  ✅ 수집된 데이터 (전체):")
                for key, value in score_data.items():
                    if key not in ['player_id', '선수명']:
                        print(f"    {key}: {value}")
            print(f"  ✅ {player_name}: 2025 성적 데이터 수집 완료")
        else:
            print(f"  ⚠️ {player_name}: 2025 성적 데이터를 찾을 수 없습니다.")
        
        return score_data
        
    except Exception as e:
        print(f"  ❌ {player_name} (ID: {player_id}) 2025 성적 크롤링 오류: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_2025_score_pitcher_table(cursor, conn):
    """
    2025 성적 투수 테이블을 생성합니다.
    기존 테이블이 있으면 삭제하고 새로 생성합니다.
    """
    try:
        # 기존 테이블 삭제
        cursor.execute("DROP TABLE IF EXISTS `2025_score_pitchers`")
        conn.commit()
        print("✅ 기존 2025 성적 테이블 삭제 완료")
        
        # 새 테이블 생성
        create_table_query = """
        CREATE TABLE `2025_score_pitchers` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `player_id` VARCHAR(20) NOT NULL,
            `선수명` VARCHAR(50) NOT NULL,
            `ERA` VARCHAR(10),
            `G` VARCHAR(10),
            `CG` VARCHAR(10),
            `SHO` VARCHAR(10),
            `W` VARCHAR(10),
            `L` VARCHAR(10),
            `SV` VARCHAR(10),
            `HLD` VARCHAR(10),
            `WPCT` VARCHAR(10),
            `TBF` VARCHAR(10),
            `NP` VARCHAR(10),
            `IP` VARCHAR(10),
            `H` VARCHAR(10),
            `2B` VARCHAR(10),
            `3B` VARCHAR(10),
            `HR` VARCHAR(10),
            `SAC` VARCHAR(10),
            `SF` VARCHAR(10),
            `BB` VARCHAR(10),
            `IBB` VARCHAR(10),
            `SO` VARCHAR(10),
            `WP` VARCHAR(10),
            `BK` VARCHAR(10),
            `R` VARCHAR(10),
            `ER` VARCHAR(10),
            `BSV` VARCHAR(10),
            `WHIP` VARCHAR(10),
            `AVG` VARCHAR(10),
            `QS` VARCHAR(10),
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX `idx_player_id` (`player_id`),
            INDEX `idx_선수명` (`선수명`),
            UNIQUE KEY `unique_player` (`player_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ 2025 성적 투수 테이블 생성 완료")
        
    except Exception as e:
        print(f"❌ 테이블 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        raise

def save_2025_score_to_db(cursor, conn, score_data):
    """
    크롤링한 2025 성적 데이터를 DB에 저장합니다.
    
    Args:
        cursor: DB 커서
        conn: DB 연결
        score_data: 2025 성적 데이터 (딕셔너리)
    """
    if not score_data:
        return
    
    try:
        # UPSERT 쿼리 (기존 데이터가 있으면 업데이트, 없으면 삽입)
        insert_query = """
        INSERT INTO `2025_score_pitchers` 
        (`player_id`, `선수명`, `ERA`, `G`, `CG`, `SHO`, `W`, `L`, `SV`, `HLD`, `WPCT`, `TBF`, `NP`, `IP`, `H`, `2B`, `3B`, `HR`, `SAC`, `SF`, `BB`, `IBB`, `SO`, `WP`, `BK`, `R`, `ER`, `BSV`, `WHIP`, `AVG`, `QS`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            `선수명` = VALUES(`선수명`),
            `ERA` = VALUES(`ERA`),
            `G` = VALUES(`G`),
            `CG` = VALUES(`CG`),
            `SHO` = VALUES(`SHO`),
            `W` = VALUES(`W`),
            `L` = VALUES(`L`),
            `SV` = VALUES(`SV`),
            `HLD` = VALUES(`HLD`),
            `WPCT` = VALUES(`WPCT`),
            `TBF` = VALUES(`TBF`),
            `NP` = VALUES(`NP`),
            `IP` = VALUES(`IP`),
            `H` = VALUES(`H`),
            `2B` = VALUES(`2B`),
            `3B` = VALUES(`3B`),
            `HR` = VALUES(`HR`),
            `SAC` = VALUES(`SAC`),
            `SF` = VALUES(`SF`),
            `BB` = VALUES(`BB`),
            `IBB` = VALUES(`IBB`),
            `SO` = VALUES(`SO`),
            `WP` = VALUES(`WP`),
            `BK` = VALUES(`BK`),
            `R` = VALUES(`R`),
            `ER` = VALUES(`ER`),
            `BSV` = VALUES(`BSV`),
            `WHIP` = VALUES(`WHIP`),
            `AVG` = VALUES(`AVG`),
            `QS` = VALUES(`QS`),
            `updated_at` = CURRENT_TIMESTAMP
        """
        
        cursor.execute(insert_query, (
            score_data['player_id'],
            score_data['선수명'],
            score_data.get('ERA', ''),
            score_data.get('G', ''),
            score_data.get('CG', ''),
            score_data.get('SHO', ''),
            score_data.get('W', ''),
            score_data.get('L', ''),
            score_data.get('SV', ''),
            score_data.get('HLD', ''),
            score_data.get('WPCT', ''),
            score_data.get('TBF', ''),
            score_data.get('NP', ''),
            score_data.get('IP', ''),
            score_data.get('H', ''),
            score_data.get('2B', ''),
            score_data.get('3B', ''),
            score_data.get('HR', ''),
            score_data.get('SAC', ''),
            score_data.get('SF', ''),
            score_data.get('BB', ''),
            score_data.get('IBB', ''),
            score_data.get('SO', ''),
            score_data.get('WP', ''),
            score_data.get('BK', ''),
            score_data.get('R', ''),
            score_data.get('ER', ''),
            score_data.get('BSV', ''),
            score_data.get('WHIP', ''),
            score_data.get('AVG', ''),
            score_data.get('QS', ''),
        ))
        
        conn.commit()
        print(f"  💾 {score_data['선수명']}의 2025 성적 데이터 저장 완료")
        
    except Exception as e:
        print(f"  ❌ DB 저장 오류: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()

def main():
    """메인 크롤링 함수"""
    import sys
    
    # 디버그 모드 확인 (명령줄 인자로 --debug 전달 시)
    debug_mode = '--debug' in sys.argv
    
    print("=" * 80)
    print("🏆 KBO 투수 2025 성적 크롤링 시작")
    if debug_mode:
        print("🔍 디버그 모드 활성화")
    print("=" * 80)
    
    driver = None
    conn = None
    
    try:
        # 1. DB 연결
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(DictCursor)
        
        # 2. 2025 성적 테이블 생성
        create_2025_score_pitcher_table(cursor, conn)
        
        # 3. DB에서 선수 목록 가져오기
        players = get_players_from_db()
        
        if not players:
            print("⚠️ 크롤링할 선수가 없습니다.")
            return
        
        # 4. Selenium 드라이버 초기화
        driver = setup_driver(headless=not debug_mode)  # 디버그 모드면 headless 비활성화
        
        # 5. 각 선수의 2025 성적 데이터 크롤링
        score_success_count = 0
        score_fail_count = 0
        
        for idx, player in enumerate(players, 1):
            player_name = player['선수명']
            player_id = player['player_id']
            team_name = player.get('팀명', '')
            
            print(f"\n[{idx}/{len(players)}] {player_name} ({team_name}) - ID: {player_id}")
            
            try:
                # 2025 성적 데이터 크롤링
                score_data = crawl_2025_score(driver, player_id, player_name, debug=debug_mode)
                
                if score_data:
                    # DB에 저장
                    save_2025_score_to_db(cursor, conn, score_data)
                    score_success_count += 1
                else:
                    print(f"  ⚠️ {player_name}: 2025 성적 데이터가 없습니다.")
                    score_fail_count += 1
                
                # 요청 간격 (서버 부하 방지)
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ {player_name} 처리 중 오류: {e}")
                score_fail_count += 1
                if debug_mode:
                    import traceback
                    traceback.print_exc()
                continue
        
        # 6. 결과 출력
        print("\n" + "=" * 80)
        print("📊 크롤링 결과")
        print("=" * 80)
        print(f"✅ 2025 성적 성공: {score_success_count}명")
        print(f"❌ 2025 성적 실패: {score_fail_count}명")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 크롤링 오류: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("\n✅ 브라우저 종료")
        if conn:
            conn.close()
            print("✅ DB 연결 종료")

if __name__ == "__main__":
    main()


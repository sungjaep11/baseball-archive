"""
KBO 타자 2025 성적 크롤링 스크립트
https://www.koreabaseball.com/Record/Player/HitterDetail/Basic.aspx?playerId=76232
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
HITTER_DETAIL_URL = "https://www.koreabaseball.com/Record/Player/HitterDetail/Basic.aspx?playerId={id}"

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
    kbo_hitters_top150 테이블에서 선수명과 player_id를 가져옵니다.
    player_id가 있는 선수만 조회합니다.
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(DictCursor)
        
        # 선수명과 player_id 조회 (player_id가 NULL이 아닌 경우만)
        query = """
            SELECT DISTINCT `선수명`, `player_id`, `팀명`
            FROM `kbo_hitters_top150`
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
        player_name: 선수명 (예: "양의지")
    
    Returns:
        list: 최근 10경기 기록 리스트 (각 경기는 딕셔너리)
    """
    try:
        # 1. 선수 상세 페이지로 이동
        detail_url = HITTER_DETAIL_URL.format(id=player_id)
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
                
                # 최근 10경기 테이블 구조:
                # 일자, 상대, AVG, PA, AB, R, H, 2B, 3B, HR, RBI, SB, CS, BB, HBP, SO, GDP
                if len(cols) >= 10:  # 최소 컬럼 개수 확인
                    game_data = {
                        'player_id': player_id,
                        '선수명': player_name,
                        '일자': cols[0].text.strip() if len(cols) > 0 else '',
                        '상대': cols[1].text.strip() if len(cols) > 1 else '',
                        'AVG': cols[2].text.strip() if len(cols) > 2 else '',
                        'PA': cols[3].text.strip() if len(cols) > 3 else '',
                        'AB': cols[4].text.strip() if len(cols) > 4 else '',
                        'R': cols[5].text.strip() if len(cols) > 5 else '',
                        'H': cols[6].text.strip() if len(cols) > 6 else '',
                        '2B': cols[7].text.strip() if len(cols) > 7 else '',
                        '3B': cols[8].text.strip() if len(cols) > 8 else '',
                        'HR': cols[9].text.strip() if len(cols) > 9 else '',
                        'RBI': cols[10].text.strip() if len(cols) > 10 else '',
                        'SB': cols[11].text.strip() if len(cols) > 11 else '',
                        'CS': cols[12].text.strip() if len(cols) > 12 else '',
                        'BB': cols[13].text.strip() if len(cols) > 13 else '',
                        'HBP': cols[14].text.strip() if len(cols) > 14 else '',
                        'SO': cols[15].text.strip() if len(cols) > 15 else '',
                        'GDP': cols[16].text.strip() if len(cols) > 16 else '',
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

def create_hitter_log_table(cursor, conn):
    """
    타자로그 테이블을 생성합니다.
    기존 테이블이 있으면 삭제하고 새로 생성합니다.
    """
    try:
        # 기존 테이블 삭제
        cursor.execute("DROP TABLE IF EXISTS `hitter_recent_games_log`")
        conn.commit()
        print("✅ 기존 테이블 삭제 완료")
        
        # 새 테이블 생성
        create_table_query = """
        CREATE TABLE `hitter_recent_games_log` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `player_id` VARCHAR(20) NOT NULL,
            `선수명` VARCHAR(50) NOT NULL,
            `일자` VARCHAR(20),
            `상대` VARCHAR(20),
            `AVG` VARCHAR(10),
            `PA` VARCHAR(10),
            `AB` VARCHAR(10),
            `R` VARCHAR(10),
            `H` VARCHAR(10),
            `2B` VARCHAR(10),
            `3B` VARCHAR(10),
            `HR` VARCHAR(10),
            `RBI` VARCHAR(10),
            `SB` VARCHAR(10),
            `CS` VARCHAR(10),
            `BB` VARCHAR(10),
            `HBP` VARCHAR(10),
            `SO` VARCHAR(10),
            `GDP` VARCHAR(10),
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX `idx_player_id` (`player_id`),
            INDEX `idx_선수명` (`선수명`),
            INDEX `idx_일자` (`일자`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ 타자로그 테이블 생성 완료")
        
    except Exception as e:
        print(f"❌ 테이블 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        raise

def save_games_to_db(cursor, conn, games_data):
    """
    크롤링한 경기 데이터를 DB에 저장합니다.
    
    Args:
        cursor: DB 커서
        conn: DB 연결
        games_data: 경기 데이터 리스트
    """
    if not games_data:
        return
    
    try:
        insert_query = """
        INSERT INTO `hitter_recent_games_log` 
        (`player_id`, `선수명`, `일자`, `상대`, `AVG`, `PA`, `AB`, `R`, `H`, `2B`, `3B`, `HR`, `RBI`, `SB`, `CS`, `BB`, `HBP`, `SO`, `GDP`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for game in games_data:
            cursor.execute(insert_query, (
                game['player_id'],
                game['선수명'],
                game['일자'],
                game['상대'],
                game['AVG'],
                game['PA'],
                game['AB'],
                game['R'],
                game['H'],
                game['2B'],
                game['3B'],
                game['HR'],
                game['RBI'],
                game['SB'],
                game['CS'],
                game['BB'],
                game['HBP'],
                game['SO'],
                game['GDP']
            ))
        
        conn.commit()
        print(f"  💾 {len(games_data)}경기 데이터 저장 완료")
        
    except Exception as e:
        print(f"  ❌ DB 저장 오류: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()

def crawl_2025_score(driver, player_id, player_name, debug=False):
    """
    선수 상세 페이지에서 "2025 성적" 테이블을 크롤링합니다.
    (수정됨: 단일 행 파싱 로직 적용)
    """
    try:
        # 1. 선수 상세 페이지로 이동
        detail_url = HITTER_DETAIL_URL.format(id=player_id)
        driver.get(detail_url)
        # ... (기존 대기 로직 유지) ...
        time.sleep(2)
        
        # 2. 2025 성적 테이블 찾기 (기존 로직 활용하되 범위 좁힘)
        # KBO 페이지 구조상 '정규시즌 성적' 테이블이 가장 위에 있고 큽니다.
        target_row = None
        
        # 테이블의 모든 행을 순회하며 '2025'가 있는 행을 찾습니다.
        # table.tData 클래스가 주로 데이터 테이블입니다.
        rows = driver.find_elements(By.CSS_SELECTOR, "table.tData tbody tr")
        
        for row in rows:
            text = row.text
            # '2025'년 데이터인지 확인 (혹은 2025 성적만 있는 페이지라면 첫 줄)
            # 보통 첫 컬럼이나 두번째 컬럼에 연도가 나옵니다.
            if '2025' in text:
                target_row = row
                break
        
        if not target_row:
            print(f"  ⚠️ {player_name}: 2025년 기록 행을 찾을 수 없습니다.")
            return None

        # 3. 데이터 파싱 (단일 행에서 모든 데이터 추출)
        cols = target_row.find_elements(By.TAG_NAME, "td")
        
        # KBO Basic 페이지의 컬럼 순서 (2024~2025 기준, 변동 가능성 있음)
        # 0: 연도, 1: 팀명, 2: 타율(AVG), 3: 경기(G), 4: 타석(PA), 5: 타수(AB), 
        # 6: 득점(R), 7: 안타(H), 8: 2루타(2B), 9: 3루타(3B), 10: 홈런(HR), 
        # 11: 루타(TB), 12: 타점(RBI), 13: 도루(SB), 14: 도실(CS), 15: 희타(SAC), 
        # 16: 희비(SF), 17: 볼넷(BB), 18: 고의4구(IBB), 19: 사구(HBP), 20: 삼진(SO), 
        # 21: 병살(GDP), 22: 장타율(SLG), 23: 출루율(OBP), 24: OPS, ...
        
        if len(cols) < 20:
            print(f"  ⚠️ 컬럼 수가 부족합니다. (발견된 컬럼 수: {len(cols)})")
            return None

        score_data = {
            'player_id': player_id,
            '선수명': player_name,
            # 인덱스는 실제 페이지 소스를 보고 미세 조정이 필요할 수 있습니다.
            # 아래는 일반적인 KBO 기록실 순서입니다.
            'AVG': cols[2].text.strip(),
            'G':   cols[3].text.strip(),
            'PA':  cols[4].text.strip(),
            'AB':  cols[5].text.strip(),
            'R':   cols[6].text.strip(),
            'H':   cols[7].text.strip(),
            '2B':  cols[8].text.strip(),
            '3B':  cols[9].text.strip(),
            'HR':  cols[10].text.strip(),
            'TB':  cols[11].text.strip(),
            'RBI': cols[12].text.strip(),
            'SB':  cols[13].text.strip(),
            'CS':  cols[14].text.strip(),
            'SAC': cols[15].text.strip(),
            'SF':  cols[16].text.strip(),
            'BB':  cols[17].text.strip(), # 여기가 문제였던 부분 (같은 줄에 있음)
            'IBB': cols[18].text.strip(),
            'HBP': cols[19].text.strip(),
            'SO':  cols[20].text.strip(),
            'GDP': cols[21].text.strip(),
            'SLG': cols[22].text.strip(),
            'OBP': cols[23].text.strip(),
            'OPS': cols[24].text.strip() if len(cols) > 24 else ''
        }
        
        print(f"  ✅ {player_name}: 2025 성적 데이터 수집 완료 (BB: {score_data['BB']}, SO: {score_data['SO']})")
        return score_data

    except Exception as e:
        print(f"  ❌ {player_name} (ID: {player_id}) 크롤링 오류: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return None

def create_2025_score_hitter_table(cursor, conn):
    """
    2025 성적 타자 테이블 생성 (SAC, SF 포함)
    """
    try:
        cursor.execute("DROP TABLE IF EXISTS `2025_score_hitter`")
        conn.commit()
        
        query = """
        CREATE TABLE `2025_score_hitter` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `player_id` VARCHAR(20) NOT NULL,
            `선수명` VARCHAR(50) NOT NULL,
            `G` VARCHAR(10),
            `PA` VARCHAR(10),
            `AB` VARCHAR(10),
            `R` VARCHAR(10),
            `H` VARCHAR(10),
            `2B` VARCHAR(10),
            `3B` VARCHAR(10),
            `HR` VARCHAR(10),
            `TB` VARCHAR(10),
            `RBI` VARCHAR(10),
            `SAC` VARCHAR(10),      -- 희생번트 (확인됨)
            `SF` VARCHAR(10),       -- 희생플라이 (확인됨)
            `SB` VARCHAR(10),
            `CS` VARCHAR(10),
            `BB` VARCHAR(10),
            `HBP` VARCHAR(10),
            `SO` VARCHAR(10),
            `GDP` VARCHAR(10),
            `AVG` VARCHAR(10),
            `OBP` VARCHAR(10),
            `SLG` VARCHAR(10),
            `OPS` VARCHAR(10),
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX `idx_player_id` (`player_id`),
            UNIQUE KEY `unique_player` (`player_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(query)
        conn.commit()
        print("✅ 2025 성적 테이블 생성 완료 (SAC, SF 포함)")
        
    except Exception as e:
        print(f"❌ 테이블 생성 오류: {e}")
        raise

def save_2025_score_to_db(cursor, conn, score_data):
    """
    2025 성적 데이터 저장 (수정된 딕셔너리 키 반영)
    """
    if not score_data:
        return
    
    try:
        # INSERT 쿼리 (모든 컬럼 명시)
        insert_query = """
        INSERT INTO `2025_score_hitter` 
        (`player_id`, `선수명`, `G`, `PA`, `AB`, `R`, `H`, `2B`, `3B`, `HR`, `TB`, `RBI`, 
         `SAC`, `SF`, `SB`, `CS`, `BB`, `HBP`, `SO`, `GDP`, `AVG`, `OBP`, `SLG`, `OPS`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            `선수명` = VALUES(`선수명`),
            `G` = VALUES(`G`),
            `PA` = VALUES(`PA`),
            `AB` = VALUES(`AB`),
            `R` = VALUES(`R`),
            `H` = VALUES(`H`),
            `2B` = VALUES(`2B`),
            `3B` = VALUES(`3B`),
            `HR` = VALUES(`HR`),
            `TB` = VALUES(`TB`),
            `RBI` = VALUES(`RBI`),
            `SAC` = VALUES(`SAC`),
            `SF` = VALUES(`SF`),
            `SB` = VALUES(`SB`),
            `CS` = VALUES(`CS`),
            `BB` = VALUES(`BB`),
            `HBP` = VALUES(`HBP`),
            `SO` = VALUES(`SO`),
            `GDP` = VALUES(`GDP`),
            `AVG` = VALUES(`AVG`),
            `OBP` = VALUES(`OBP`),
            `SLG` = VALUES(`SLG`),
            `OPS` = VALUES(`OPS`)
        """
        
        # 딕셔너리에서 안전하게 값 추출 (.get 사용)
        cursor.execute(insert_query, (
            score_data['player_id'],
            score_data['선수명'],
            score_data.get('G', ''),
            score_data.get('PA', ''),
            score_data.get('AB', ''),
            score_data.get('R', ''),
            score_data.get('H', ''),
            score_data.get('2B', ''),
            score_data.get('3B', ''),
            score_data.get('HR', ''),
            score_data.get('TB', ''),
            score_data.get('RBI', ''),
            score_data.get('SAC', ''),  # 추가됨
            score_data.get('SF', ''),   # 추가됨
            score_data.get('SB', ''),
            score_data.get('CS', ''),
            score_data.get('BB', ''),
            score_data.get('HBP', ''),
            score_data.get('SO', ''),
            score_data.get('GDP', ''),
            score_data.get('AVG', ''),
            score_data.get('OBP', ''),
            score_data.get('SLG', ''),
            score_data.get('OPS', ''),
        ))
        
        conn.commit()
        print(f"  💾 {score_data['선수명']} 데이터 저장 완료")
        
    except Exception as e:
        print(f"  ❌ DB 저장 오류 ({score_data['선수명']}): {e}")
        conn.rollback()

def main():
    """메인 크롤링 함수"""
    import sys
    
    # 디버그 모드 확인 (명령줄 인자로 --debug 전달 시)
    debug_mode = '--debug' in sys.argv
    
    print("=" * 80)
    print("🏆 KBO 타자 2025 성적 크롤링 시작")
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
        create_2025_score_hitter_table(cursor, conn)
        
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


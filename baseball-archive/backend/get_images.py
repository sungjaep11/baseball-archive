import os
import re
import time
import json
import urllib.parse
import urllib3

import requests
import pymysql
from pymysql.cursors import DictCursor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config.db_config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

# SSL 인증서 경고 비활성화 (일부 사이트의 인증서 문제 대응)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def clean_search_term(name):
    """선수명 끝의 영문자 제거"""
    return re.sub(r'[A-Z]$', '', name)

def setup_driver(headless=True):
    """Chrome 드라이버 설정"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    # 봇 탐지 방지용 User-Agent 설정
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver_path = ChromeDriverManager().install()
        # 리눅스 환경 등에서 권한 문제 발생 시 대비
        if os.name != 'nt':
            os.chmod(driver_path, 0o755)
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ ChromeDriver 설정 오류: {e}")
        raise

def download_image_from_url(url, save_path):
    """URL에서 이미지 다운로드 (SSL 인증서 오류 처리 포함)"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bing.com/'
        }
        # SSL 인증서 검증 비활성화 (일부 사이트의 인증서 문제 대응)
        # 주의: 보안상 verify=False는 신뢰할 수 있는 사이트에만 사용
        response = requests.get(url, headers=headers, timeout=15, stream=True, verify=False)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except requests.exceptions.SSLError as e:
        print(f"  ⚠️ SSL 인증서 오류 ({url[:30]}...): {e}")
        return False
    except Exception as e:
        print(f"  ⚠️ 다운로드 실패 ({url[:30]}...): {e}")
        return False

def crawl_bing_images_selenium(driver, keyword, max_num=3):
    """
    Bing 이미지 검색에서 'm' 속성의 JSON 데이터를 파싱하여 고화질 원본 URL 추출
    """
    image_urls = []
    
    try:
        encoded_keyword = urllib.parse.quote_plus(keyword)
        # 1. URL 수정: &qft=+filterui:photo-photo 추가 (사진만 검색)
        search_url = f"https://www.bing.com/images/search?q={encoded_keyword}&form=HDRSC3&first=1&qft=+filterui:photo-photo"
        
        print("  🔍 검색 URL 접속 중...")
        driver.get(search_url)
        
        wait = WebDriverWait(driver, 10)
        
        # 2. 이미지 카드 요소(.iusc)가 로드될 때까지 대기
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "iusc")))
        except Exception:
            print("  ⚠️ 이미지 로딩 시간 초과 또는 결과 없음")
            return image_urls

        # 스크롤을 살짝 내려서 이미지를 더 로딩 (필요시)
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(1.5)

        # 3. 모든 이미지 요소 찾기
        # Bing의 이미지 카드는 'iusc' 클래스를 가진 <a> 태그로 구성됨
        elements = driver.find_elements(By.CLASS_NAME, "iusc")
        
        print(f"  ✓ 검색된 이미지 요소: {len(elements)}개")

        for element in elements:
            if len(image_urls) >= max_num:
                break
                
            try:
                # 4. 핵심: 'm' 속성에서 JSON 데이터 추출
                m_attr = element.get_attribute("m")
                
                if m_attr:
                    # JSON 문자열을 딕셔너리로 변환
                    data = json.loads(m_attr)
                    
                    # 'murl' 키가 진짜 고화질 원본 주소임
                    real_url = data.get("murl")
                    
                    if real_url and real_url.startswith("http"):
                        # 중복 체크
                        if real_url not in image_urls:
                            image_urls.append(real_url)
                            print(f"  📸 원본 주소 추출 성공: {real_url[:60]}...")
            except json.JSONDecodeError:
                continue
            except Exception:
                # 개별 요소 파싱 에러는 무시하고 다음으로 진행
                continue
        
        print(f"  ✅ 최종 추출된 URL: {len(image_urls)}개")
        
    except Exception as e:
        print(f"  ❌ 크롤링 중 치명적 오류: {e}")
    
    return image_urls

def get_players_from_db():
    """
    DB에서 선수 정보 가져오기 (타자 + 투수)
    - 타자: kbo_hitters_top150 + kbo_defense_positions JOIN
    - 투수: kbo_pitchers_top150 (포지션은 "투수"로 설정)
    """
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=int(DB_PORT),
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        cursor = conn.cursor()
        
        result = []
        
        # 1. 타자 선수 정보 가져오기 (기존 로직)
        try:
            hitter_query = """
                SELECT DISTINCT
                    h.`선수명` AS `name`,
                    h.`팀명` AS `team`,
                    d.`POS` AS `position`
                FROM `kbo_hitters_top150` h
                INNER JOIN `kbo_defense_positions` d 
                    ON h.`선수명` = d.`선수명` 
                    AND h.`팀명` = d.`팀명`
                ORDER BY h.`선수명`
            """
            cursor.execute(hitter_query)
            hitters = cursor.fetchall()
            
            for player in hitters:
                result.append({
                    'name': player['name'],
                    'team': player['team'],
                    'position': player['position']
                })
            
            print(f"✅ 타자 {len(hitters)}명 조회 완료")
        except Exception as e:
            print(f"⚠️ 타자 데이터 조회 중 오류: {e}")
        
        # 2. 투수 선수 정보 가져오기
        try:
            pitcher_query = """
                SELECT DISTINCT
                    `선수명` AS `name`,
                    `팀명` AS `team`,
                    '투수' AS `position`
                FROM `kbo_pitchers_top150`
                ORDER BY `선수명`
            """
            cursor.execute(pitcher_query)
            pitchers = cursor.fetchall()
            
            for player in pitchers:
                result.append({
                    'name': player['name'],
                    'team': player['team'],
                    'position': player['position']  # '투수'
                })
            
            print(f"✅ 투수 {len(pitchers)}명 조회 완료")
        except Exception as e:
            print(f"⚠️ 투수 데이터 조회 중 오류: {e}")
        
        cursor.close()
        conn.close()
        
        # 중복 제거 (타자와 투수에 동일한 선수가 있을 수 있음)
        seen = set()
        unique_result = []
        for player in result:
            key = (player['name'], player['team'])
            if key not in seen:
                seen.add(key)
                unique_result.append(player)
        
        print(f"✅ 총 {len(unique_result)}명의 선수 정보를 가져왔습니다. (타자 + 투수, 중복 제거)")
        return unique_result
        
    except Exception as e:
        print(f"❌ DB 연결 오류: {e}")
        import traceback
        traceback.print_exc()
        return []

def download_kbo_images(player_list):
    """
    선수 이미지 다운로드 실행
    """
    base_dir = 'player_images'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    print(f"총 {len(player_list)}명의 선수 이미지를 수집합니다 (고화질/사진필터 적용)...")
    
    driver = None
    try:
        driver = setup_driver(headless=True)
        print("✅ 브라우저 준비 완료\n")
        
        for player_idx, player in enumerate(player_list, 1):
            player_name = clean_search_term(player['name'])
            team_name = player['team']
            position = player.get('position', '')
            
            # 검색어 조합 (예: 한화 투수 류현진)
            search_keyword = f"{team_name} {position} {player_name}"
            
            print(f"[{player_idx}/{len(player_list)}] {player_name} ({team_name}) 검색: '{search_keyword}'")

            # 기존 파일 확인: 선수에 대한 이미지 3장이 모두 있는지 확인
            existing_files = []
            for idx in range(1, 4):  # 1, 2, 3
                for ext in ['.jpg', '.png', '.jpeg', '.gif', '.webp']:
                    check_path = os.path.join(base_dir, f"{player_name}_{idx}{ext}")
                    if os.path.exists(check_path):
                        existing_files.append(check_path)
                        break  # 하나라도 찾으면 다음 번호로
            
            # 3장이 모두 있으면 건너뛰기
            if len(existing_files) >= 3:
                print(f"  ⏭️  이미지 3장이 모두 존재하여 건너뜁니다: {[os.path.basename(f) for f in existing_files]}")
                continue

            # 기존 파일 개수만큼 성공 카운트에 추가
            success_count = len(existing_files)
            downloaded_files = existing_files.copy()
            
            if success_count > 0:
                print(f"  ℹ️  기존 파일 {success_count}장 발견, {3 - success_count}장 추가 다운로드 필요")

            # 3개 이미지가 모두 성공할 때까지 재시도
            target_count = 3
            max_retries = 10  # 최대 재시도 횟수
            retry_count = 0
            
            while success_count < target_count and retry_count < max_retries:
                retry_count += 1
                
                if retry_count > 1:
                    print(f"  🔄 재시도 {retry_count-1}회차: {success_count}/{target_count}장 성공, 추가 이미지 검색 중...")
                    time.sleep(2)  # 재시도 전 대기
                
                # 이미지 URL 추출 (최대 3개, 또는 부족한 개수만큼)
                needed_count = target_count - success_count
                image_urls = crawl_bing_images_selenium(driver, search_keyword, max_num=needed_count + 2)  # 여유있게 더 가져오기
                
                if not image_urls:
                    if retry_count >= max_retries:
                        print(f"  ⚠️ 검색 결과가 없어 건너뜁니다. (성공: {success_count}/{target_count}장)")
                    continue

                # 다운로드 로직
                for img_url in image_urls:
                    if success_count >= target_count:
                        break
                    
                    # 이미 시도한 URL인지 확인 (중복 방지)
                    # URL의 일부를 해시하여 이미 다운로드 시도한 URL인지 확인
                    url_hash = hash(img_url) % 10000
                    if url_hash in [hash(f) % 10000 for f in downloaded_files]:
                        continue
                    
                    try:
                        # 확장자 결정 (URL에서 추출하거나 기본값 jpg)
                        ext = '.jpg'
                        if '.png' in img_url.lower():
                            ext = '.png'
                        elif '.gif' in img_url.lower():
                            ext = '.gif'
                        elif '.webp' in img_url.lower():
                            ext = '.webp'
                        elif '.jpeg' in img_url.lower():
                            ext = '.jpg'

                        idx = success_count + 1
                        final_filename = f"{player_name}_{idx}{ext}"
                        dst_path = os.path.join(base_dir, final_filename)
                        
                        # 파일이 이미 존재하는지 확인
                        if os.path.exists(dst_path):
                            success_count += 1
                            downloaded_files.append(dst_path)
                            print(f"  ✓ 이미 존재: {final_filename}")
                            continue
                        
                        if download_image_from_url(img_url, dst_path):
                            success_count += 1
                            downloaded_files.append(dst_path)
                            print(f"  💾 저장 완료 ({success_count}/{target_count}): {final_filename}")
                        else:
                            # 다운로드 실패한 경우 파일이 생성되었을 수 있으므로 삭제
                            if os.path.exists(dst_path):
                                try:
                                    os.remove(dst_path)
                                except Exception:
                                    pass
                    
                    except Exception as e:
                        print(f"  ❌ 저장 실패: {e}")
                        continue
                
                # 3개 모두 성공했는지 확인
                if success_count >= target_count:
                    print(f"  ✅ 목표 달성: {success_count}/{target_count}장 저장 완료!")
                    break
                elif retry_count < max_retries:
                    print(f"  ⚠️ 현재 {success_count}/{target_count}장만 성공, 재시도 예정...")
            
            if success_count < target_count:
                print(f"  ⚠️ 최종 결과: {success_count}/{target_count}장만 저장됨 (재시도 {retry_count}회)")
            else:
                print(f"  ✅ 최종 결과: {success_count}/{target_count}장 모두 저장 완료!")
            
            time.sleep(1)  # 차단 방지를 위한 짧은 대기

    except Exception as e:
        print(f"❌ 프로세스 중단: {e}")
    finally:
        if driver:
            driver.quit()
            print("\n✅ 작업 종료")

if __name__ == "__main__":
    players = get_players_from_db()
    
    if not players:
        print("⚠️ DB 데이터 없음. 테스트 데이터를 사용합니다.")
        players = [
            {'name': '류현진', 'team': '한화', 'position': '투수'},
            {'name': '김도영', 'team': 'KIA', 'position': '내야수'}
        ]
    
    download_kbo_images(players)
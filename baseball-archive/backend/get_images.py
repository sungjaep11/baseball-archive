import os
import re

from icrawler.builtin import BingImageCrawler

# 선수 명단
players = [
    "서건창", "윤도현", "김도영", "한준수", "박정우", "소크라테스", "나성범", "김두현", 
    "문상철", "박경수", "황재균", "강현우", "김병준", "김민혁A", "로하스A", "신본기", 
    "오스틴", "신민재", "최명경", "이주헌", "박해민", "문성주", "홍창기", "구본혁", 
    "데이비슨", "박민우", "서호철", "안중열", "최정원", "박영빈", "박건우", "김한별", 
    "오태곤", "정준재", "최정", "이지영", "최지훈", "에레디아", "하재훈", "박성한", 
    "홍성호", "여동건", "허경민", "류현준", "정수빈", "전다민", "제러드", "김재호", 
    "나승엽", "이호준B", "손호영", "정보근", "이인한", "김민석", "레이예스", "이학주", 
    "맥키넌", "류지혁", "김영웅", "강민호", "김지찬", "구자욱", "카데나스", "이재현", 
    "최주환", "김혜성", "송성문", "김건희", "이용규", "도슨", "이주형A", "김휘집", 
    "채은성", "황영묵", "노시환", "박상언", "장진혁", "최인호", "김태연", "하주석",
    "네일", "쿠에바스", "손주영", "하트", "김광현", "곽빈", "반즈", "원태인", "후라도", "류현진"
]

def clean_search_term(name):
    return re.sub(r'[A-Z]$', '', name)

def download_kbo_images(player_list):
    save_dir = 'player_images'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    print(f"총 {len(player_list)}명의 선수 이미지를 각각 3장씩 다운로드합니다 (Bing)...")

    for player_name in player_list:
        search_keyword = clean_search_term(player_name) + " 야구선수 KBO"
        
        crawler = BingImageCrawler(
            storage={'root_dir': save_dir},
            log_level='CRITICAL'
        )

        print(f"[{player_name}] 이미지 3장 수집 중...")

        crawler.crawl(
            keyword=search_keyword,
            max_num=3,    # 3장으로 변경
            file_idx_offset=0, # 매 선수마다 000001번부터 파일명 시작하도록 강제 초기화
            filters=dict(type='photo'),
            overwrite=True
        )

        # 3장의 파일을 순회하며 이름 변경 (000001 -> 선수_1, 000002 -> 선수_2...)
        count = 0
        for i in range(1, 4): # 1, 2, 3
            # 확장자가 jpg, jpeg, png 중 무엇일지 모르니 확인
            for ext in ['.jpg', '.jpeg', '.png']:
                src_file_name = f"{i:06d}{ext}" # 예: 000001.jpg
                src_path = os.path.join(save_dir, src_file_name)
                
                target_file_name = f"{player_name}_{i}{ext}" # 예: 류현진_1.jpg
                target_path = os.path.join(save_dir, target_file_name)

                if os.path.exists(src_path):
                    # 기존에 같은 이름 파일 있으면 삭제
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    
                    os.rename(src_path, target_path)
                    count += 1
                    break # 확장자를 찾았으니 다음 번호로 넘어감
        
        print(f"  -> {count}장 저장 완료")

if __name__ == "__main__":
    download_kbo_images(players)
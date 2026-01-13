#!/usr/bin/env python3
"""
ChromeDriver 캐시 삭제 및 재설치 스크립트
"""

import os
import shutil
from pathlib import Path
from webdriver_manager.chrome import ChromeDriverManager

def clear_chromedriver_cache():
    """ChromeDriver 캐시 삭제"""
    cache_dir = Path.home() / ".wdm" / "drivers" / "chromedriver"
    
    if cache_dir.exists():
        try:
            print(f"🗑️  ChromeDriver 캐시 삭제 중: {cache_dir}")
            shutil.rmtree(cache_dir)
            print("✅ ChromeDriver 캐시 삭제 완료")
            return True
        except PermissionError as e:
            print(f"❌ 권한 오류: {e}")
            print(f"💡 수동으로 삭제해주세요: rm -rf {cache_dir}")
            return False
        except Exception as e:
            print(f"❌ 삭제 실패: {e}")
            return False
    else:
        print("ℹ️  ChromeDriver 캐시 폴더가 없습니다.")
        return True

def reinstall_chromedriver():
    """ChromeDriver 재설치"""
    try:
        print("\n📥 ChromeDriver 재설치 중...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver 설치 완료: {driver_path}")
        
        # 실행 권한 부여
        os.chmod(driver_path, 0o755)
        print(f"✅ 실행 권한 부여 완료")
        
        return driver_path
    except Exception as e:
        print(f"❌ ChromeDriver 설치 실패: {e}")
        return None

def main():
    print("=" * 60)
    print("🔧 ChromeDriver 캐시 삭제 및 재설치")
    print("=" * 60)
    
    # 1. 캐시 삭제
    if not clear_chromedriver_cache():
        print("\n⚠️  캐시 삭제에 실패했습니다. 수동으로 삭제해주세요.")
        return
    
    # 2. 재설치
    driver_path = reinstall_chromedriver()
    
    if driver_path:
        print("\n" + "=" * 60)
        print("🎉 ChromeDriver 재설치 완료!")
        print("=" * 60)
        print(f"\n📍 설치 경로: {driver_path}")
        print("\n이제 크롤링 스크립트를 다시 실행해보세요.")
    else:
        print("\n❌ ChromeDriver 재설치에 실패했습니다.")

if __name__ == "__main__":
    main()


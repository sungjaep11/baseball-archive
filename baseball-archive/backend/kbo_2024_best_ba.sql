-- SQLite import script
DROP TABLE IF EXISTS kbo_2024_best_ba;
CREATE TABLE kbo_2024_best_ba (
  season INTEGER NOT NULL,
  team TEXT NOT NULL,
  position TEXT NOT NULL,
  name TEXT NOT NULL,
  batting_avg REAL NOT NULL,
  rbi INTEGER NOT NULL,
  hr INTEGER NOT NULL,
  sb INTEGER NOT NULL,
  pa INTEGER NOT NULL
);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'KIA', '1B', '이우성', 0.288221, 54, 9, 7, 449);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'KIA', '2B', '김선빈', 0.328605, 57, 9, 5, 466);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'KIA', '3B', '김도영', 0.347426, 109, 38, 40, 625);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'KIA', 'CF', '최원준', 0.292237, 56, 9, 21, 508);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'KIA', 'LF', '소크라테스', 0.309783, 97, 26, 13, 602);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'KIA', 'SS', '박찬호', 0.306796, 61, 5, 20, 577);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'KT', '3B', '황재균', 0.259635, 58, 13, 4, 536);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'KT', 'C', '장성우', 0.267943, 81, 19, 5, 489);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'KT', 'CF', '배정대', 0.274752, 59, 7, 9, 473);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'KT', 'RF', '로하스A', 0.328671, 112, 32, 2, 670);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'LG', '1B', '오스틴', 0.318786, 132, 32, 12, 604);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'LG', '2B', '신민재', 0.297158, 40, 0, 32, 474);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'LG', '3B', '문보경', 0.300578, 101, 22, 7, 602);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'LG', 'C', '박동원', 0.271889, 80, 20, 1, 498);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'LG', 'CF', '박해민', 0.263485, 56, 6, 43, 553);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'LG', 'LF', '김현수', 0.294004, 69, 8, 6, 583);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'LG', 'RF', '홍창기', 0.335878, 73, 5, 10, 637);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'NC', '1B', '데이비슨', 0.305556, 119, 46, 0, 567);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'NC', '2B', '박민우', 0.328228, 50, 8, 32, 528);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'NC', '3B', '서호철', 0.285156, 61, 10, 1, 567);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'NC', 'LF', '권희동', 0.300481, 77, 13, 4, 511);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'NC', 'SS', '김주원', 0.251948, 49, 9, 16, 475);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'SSG', '3B', '최정', 0.290598, 107, 37, 5, 550);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'SSG', 'CF', '최지훈', 0.275362, 49, 11, 32, 543);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'SSG', 'LF', '에레디아', 0.360444, 118, 21, 4, 591);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'SSG', 'RF', '한유섬', 0.234914, 87, 24, 0, 523);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, 'SSG', 'SS', '박성한', 0.300613, 67, 10, 13, 564);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '두산', '1B', '양석환', 0.245779, 107, 34, 5, 593);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '두산', '2B', '강승호', 0.280230, 81, 18, 16, 566);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '두산', '3B', '허경민', 0.309353, 61, 7, 5, 477);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '두산', 'C', '양의지', 0.313953, 94, 17, 2, 485);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '두산', 'CF', '정수빈', 0.284314, 47, 4, 52, 608);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '롯데', '1B', '나승엽', 0.312039, 66, 7, 1, 489);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '롯데', '2B', '고승민', 0.307692, 87, 14, 5, 532);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '롯데', 'CF', '윤동희', 0.293233, 85, 14, 7, 613);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '롯데', 'RF', '레이예스', 0.351916, 111, 15, 5, 632);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '롯데', 'SS', '박승욱', 0.261728, 53, 7, 4, 468);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '삼성', '3B', '김영웅', 0.252193, 79, 28, 9, 509);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '삼성', 'C', '강민호', 0.302730, 77, 19, 3, 452);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '삼성', 'CF', '김지찬', 0.315673, 36, 3, 42, 535);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '삼성', 'LF', '구자욱', 0.342799, 115, 33, 13, 568);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '삼성', 'SS', '이재현', 0.259640, 66, 14, 2, 458);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '키움', '1B', '최주환', 0.257261, 84, 13, 0, 544);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '키움', '2B', '김혜성', 0.326130, 75, 11, 30, 567);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '키움', '3B', '송성문', 0.339658, 104, 19, 21, 602);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '키움', 'RF', '이주형A', 0.266385, 60, 13, 6, 537);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '한화', '1B', '채은성', 0.270642, 83, 20, 1, 498);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '한화', '3B', '노시환', 0.271863, 89, 24, 6, 601);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '한화', 'LF', '페라자', 0.274725, 70, 24, 7, 522);
INSERT INTO kbo_2024_best_ba (season, team, position, name, batting_avg, rbi, hr, sb, pa) VALUES (2024, '한화', 'RF', '김태연', 0.290557, 61, 12, 5, 472);
CREATE INDEX IF NOT EXISTS idx_kbo_2024_team_pos ON kbo_2024_best_ba(team, position);

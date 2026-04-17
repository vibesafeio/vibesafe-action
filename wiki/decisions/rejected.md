---
title: Rejected Decisions
type: decision
confidence: high
created: 2026-03-19
updated: 2026-04-17
sources: [docs/vc-response.md]
---

## TLDR
고려했지만 선택하지 않은 것들과 그 이유.

## Content

### 2026-04-17: Twitter/LinkedIn 단독 launch 포스트 → 기각
**왜 안 했나:** 0-audience 상태에서 follower-based 플랫폼은 impression 50-200/post. 0.4% 전환 가정 시 install 0~1. 콘텐츠 질 문제가 아니라 **distribution 메커니즘이 follower-기반**이어서 구조적으로 실패. OKKY 772뷰가 된 이유는 OKKY가 feed/board 기반이었기 때문 (Reddit/HN 같은 공식).
**대신 한 것:** (1) per-repo SEO 페이지 (compound 자산), (2) GitHub Marketplace, (3) 계획: Awesome Lists PR + Show HN + Reddit r/selfhosted
**재고 조건:** 팔로워 1K+ 확보 후

### 2026-04-17: Next.js web/ scaffold 전면 삭제 (41 tracked files) → 부분 삭제만
**왜 안 했나:** `web/src/app/api/scans/`, `web/src/app/api/auth/`, `prisma/schema.prisma`에 실제 구현된 영속화/인증 설계가 있음. 현재 배포되진 않지만 "미래 마이그레이션 자료로 유지할 가치 > 삭제 단순성". 전면 삭제는 정보 손실.
**대신 한 것:** `package.json` + `package-lock.json` 2개만 삭제 → Dependabot 28 vulns 소멸 + src/prisma는 git에 유지
**재고 조건:** src/prisma 설계 사용 안 하기로 최종 결정 시

### 2026-04-17: 중복 "Scan your own repo" 하단 입력창 → 제거
**왜 넣었다 뺐나:** SEO 방문자가 "남의 리포트" 본 상태에서 "자기 repo 스캔" CTA 필요할 거라 가정 → 하단에 별도 입력창 추가. 실제로는 상단 입력창이 이미 존재 → **중복** → 유저 혼란.
**대신 한 것:** 하단은 Install from Marketplace 하나만. "다른 repo 스캔하려면 ↑" 작은 링크로 상단 입력창 clear + focus + scroll-to-top.
**재고 조건:** 재고 안 함



### VibeCost 즉시 개발 → 보류
**왜 안 했나:** 비용 공포가 실제 사용자 행동을 바꾸는지 미검증. VibeSafe 사용자 0명인 상태에서 두 번째 프로덕트 시작은 리소스 분산.
**재고 조건:** VibeSafe 사용자 100+ 확보 후

### 엔터프라이즈 타겟 → 제외
**왜 안 했나:** 사용자 0명에서 엔터프라이즈 영업 불가. Snyk/Wiz가 이미 장악.
**재고 조건:** B2C 또는 B2B2C로 사용자 기반 확보 후

### 유료 기능 즉시 출시 → 보류
**왜 안 했나:** 바이브 코더는 보안에 돈 안 냄 (지불 의향 ≈ 0). 무료로 사용자 확보 선행.
**재고 조건:** 사용자 1000+, 명확한 premium 수요 확인 시

### Wall of Shame 리더보드 → 거부
**왜 안 했나:** 타인 repo를 공개적으로 까는 건 법적 리스크 + 커뮤니티 반감
**재고 조건:** 재고하지 않음

### B2C 구독 ($9/month) → 보류
**왜 안 했나:** 바이브 코더가 보안에 월 구독 할 동기 없음. Private repo 스캔이 전환 트리거가 될 수 있으나 미검증.
**재고 조건:** 웹 스캐너에서 private repo 요청이 반복될 때

## Related
- [[decisions/log.md]]
- [[product/roadmap.md]]

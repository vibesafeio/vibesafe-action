---
title: Accessibility Expansion
type: future
confidence: medium
created: 2026-03-22
updated: 2026-04-12
sources: []
---

## TLDR
img alt, label, lang 등 접근성 규칙. light 모드에 포함됨.
ADA 소송 4,000+건/년 = 실제 리스크. "Security" → "Safety" 확장의 핵심.

## Content

### 현재 구현된 접근성 규칙
- `<img>` without alt attribute
- `<input>` without label
- Missing `lang` attribute on `<html>`
- 기타 WCAG 2.1 기본 항목

### 확장 계획
- 색상 대비 검사 (contrast ratio)
- 키보드 네비게이션 검증
- ARIA 속성 검증
- 폼 접근성 (fieldset, legend)

### 비즈니스 근거
- ADA 소송 4,000+건/년 (미국)
- 64% of ADA lawsuits target small businesses
- 바이브 코더가 만든 앱 = 접근성 고려 0 = 소송 리스크

## Open Questions
- 접근성 규칙을 full mode에서만 돌릴 것인가?
- 접근성 점수를 보안 점수와 분리할 것인가?

## Related
- [[product/positioning.md]]
- [[product/features.md]]

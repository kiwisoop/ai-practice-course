#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor

# 색상 정의
COLOR_PRIMARY = RGBColor(46, 117, 182)
COLOR_SECONDARY = RGBColor(248, 165, 55)
COLOR_ACCENT = RGBColor(112, 173, 71)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_BLACK = RGBColor(0, 0, 0)

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    return prs

def add_title_slide(prs):
    """개선된 타이틀 슬라이드"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_PRIMARY

    # 제목 (크기 감소, 위치 조정)
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.8), Inches(9), Inches(1.0))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    title_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    p = title_frame.paragraphs[0]
    p.text = "AI 기반 강의 노트 복습 도우미"
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

    # 부제 (위치 조정, 간격 확대)
    subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.0), Inches(9), Inches(0.8))
    subtitle_frame = subtitle_box.text_frame
    subtitle_frame.vertical_anchor = MSO_ANCHOR.TOP
    p = subtitle_frame.paragraphs[0]
    p.text = "Study Buddy AI"
    p.font.size = Pt(36)
    p.font.color.rgb = COLOR_SECONDARY
    p.alignment = PP_ALIGN.CENTER

    # 설명
    desc_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.0), Inches(9), Inches(1.2))
    desc_frame = desc_box.text_frame
    desc_frame.word_wrap = True
    p = desc_frame.paragraphs[0]
    p.text = "AI가 당신의 복습을 똑똑하게 도와줍니다"
    p.font.size = Pt(24)
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

    # 하단 정보
    info_box = slide.shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(9), Inches(0.8))
    info_frame = info_box.text_frame
    p = info_frame.paragraphs[0]
    p.text = "2026년 11월 20일"
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(200, 200, 200)
    p.alignment = PP_ALIGN.CENTER

def add_content_slide(prs, title, content_items, slide_number):
    """개선된 콘텐츠 슬라이드"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_WHITE

    # 배경 바
    top_bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(0.9))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_PRIMARY
    top_bar.line.color.rgb = COLOR_PRIMARY

    # 제목
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.15), Inches(8.5), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE

    # 슬라이드 번호
    num_box = slide.shapes.add_textbox(Inches(9.2), Inches(0.15), Inches(0.7), Inches(0.6))
    num_frame = num_box.text_frame
    p = num_frame.paragraphs[0]
    p.text = f"{slide_number}"
    p.font.size = Pt(20)
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

    # 구분선
    separator = slide.shapes.add_shape(1, Inches(0.5), Inches(1.05), Inches(9), Inches(0.02))
    separator.fill.solid()
    separator.fill.fore_color.rgb = COLOR_SECONDARY

    # 콘텐츠
    content_top = Inches(1.3)
    current_y = content_top

    for item in content_items:
        if isinstance(item, dict):
            # 섹션 헤더
            if 'section' in item:
                section_box = slide.shapes.add_textbox(Inches(0.7), current_y, Inches(8.6), Inches(0.35))
                section_frame = section_box.text_frame
                section_frame.word_wrap = True
                p = section_frame.paragraphs[0]
                p.text = item['section']
                p.font.size = Pt(19)
                p.font.bold = True
                p.font.color.rgb = COLOR_PRIMARY
                current_y += Inches(0.42)

            # 불릿 포인트
            if 'bullets' in item:
                for bullet in item['bullets']:
                    bullet_box = slide.shapes.add_textbox(Inches(1.0), current_y, Inches(8.5), Inches(0.4))
                    bullet_frame = bullet_box.text_frame
                    bullet_frame.word_wrap = True
                    p = bullet_frame.paragraphs[0]
                    p.text = "• " + bullet
                    p.font.size = Pt(17)
                    p.font.color.rgb = COLOR_BLACK
                    current_y += Inches(0.42)

def add_two_column_slide(prs, title, left_title, left_items, right_title, right_items, slide_number):
    """개선된 2열 슬라이드"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_WHITE

    # 배경 바
    top_bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(0.9))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_PRIMARY
    top_bar.line.color.rgb = COLOR_PRIMARY

    # 제목
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.15), Inches(8.5), Inches(0.6))
    title_frame = title_box.text_frame
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE

    # 슬라이드 번호
    num_box = slide.shapes.add_textbox(Inches(9.2), Inches(0.15), Inches(0.7), Inches(0.6))
    num_frame = num_box.text_frame
    p = num_frame.paragraphs[0]
    p.text = f"{slide_number}"
    p.font.size = Pt(20)
    p.font.color.rgb = COLOR_WHITE

    # 구분선
    separator = slide.shapes.add_shape(1, Inches(0.5), Inches(1.05), Inches(9), Inches(0.02))
    separator.fill.solid()
    separator.fill.fore_color.rgb = COLOR_SECONDARY

    # 좌측 열
    left_top = Inches(1.35)
    left_title_box = slide.shapes.add_textbox(Inches(0.7), left_top, Inches(4.3), Inches(0.35))
    left_title_frame = left_title_box.text_frame
    p = left_title_frame.paragraphs[0]
    p.text = left_title
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY

    left_current_y = left_top + Inches(0.42)
    for item in left_items:
        item_box = slide.shapes.add_textbox(Inches(1.0), left_current_y, Inches(3.8), Inches(0.38))
        item_frame = item_box.text_frame
        item_frame.word_wrap = True
        p = item_frame.paragraphs[0]
        p.text = "• " + item
        p.font.size = Pt(15)
        p.font.color.rgb = COLOR_BLACK
        left_current_y += Inches(0.42)

    # 우측 열
    right_top = Inches(1.35)
    right_title_box = slide.shapes.add_textbox(Inches(5.3), right_top, Inches(4.3), Inches(0.35))
    right_title_frame = right_title_box.text_frame
    p = right_title_frame.paragraphs[0]
    p.text = right_title
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY

    right_current_y = right_top + Inches(0.42)
    for item in right_items:
        item_box = slide.shapes.add_textbox(Inches(5.6), right_current_y, Inches(3.8), Inches(0.38))
        item_frame = item_box.text_frame
        item_frame.word_wrap = True
        p = item_frame.paragraphs[0]
        p.text = "• " + item
        p.font.size = Pt(15)
        p.font.color.rgb = COLOR_BLACK
        right_current_y += Inches(0.42)

def create_pptx():
    prs = create_presentation()

    add_title_slide(prs)

    add_content_slide(prs, "문제 정의 및 필요성", [
        {"section": "❌ 현재 대학생들의 불편함"},
        {"bullets": [
            "시간 부족: 한 과목만 복습해도 1-2시간 필요",
            "비효율적 복습: 모든 내용을 다시 읽음",
            "복습 동기 부족: 혼자서 반복학습은 지루함"
        ]},
        {"section": "✅ 해결 방법"},
        {"bullets": [
            "AI 활용 자동 요약 + 대화형 복습 시스템",
            "1단계: 강의 노트 자동 요약",
            "2단계: 핵심 개념 추출 및 질문 생성",
            "3단계: AI 튜터와 대화하며 복습"
        ]}
    ], 2)

    add_two_column_slide(prs, "대상 사용자",
        "주요 사용자 페르소나",
        [
            "이름: 김 대학생",
            "나이: 20대 (2학년 이상)",
            "상황: 시험 1주일 전",
            "목표: 복습 시간 50% 단축"
        ],
        "추가 사용자 그룹",
        [
            "공무원 시험 준비생",
            "온라인 강의 수강자",
            "자격증 준비자"
        ], 3)

    add_content_slide(prs, "핵심 기능 (5가지)", [
        {"bullets": [
            "🔹 자동 텍스트 요약: 70-80% 길이로 축약",
            "🔹 핵심 개념 추출: 중요한 개념을 불릿 포인트로",
            "🔹 자동 질문 생성: 강의 내용 기반 10개 질문",
            "🔹 AI 튜터 대화: 답변에 대한 피드백 제공",
            "🔹 복습 일정 추천: Spaced Repetition 적용"
        ]}
    ], 4)

    add_content_slide(prs, "AI 활용 전략", [
        {"section": "사용 AI 도구"},
        {"bullets": [
            "Claude (Primary): 텍스트 이해, 한국어 처리 우수",
            "ChatGPT (Backup): 필요 시 활용"
        ]},
        {"section": "AI 활용 단계"},
        {"bullets": [
            "1단계: 텍스트 요약 (Claude)",
            "2단계: 개념 추출 (Claude)",
            "3단계: 질문 생성 (Claude)",
            "4단계: 대화형 복습 (Claude)"
        ]}
    ], 5)

    add_content_slide(prs, "AI 협업 과정 및 개선", [
        {"section": "사례 1: 요약 프롬프트 개선"},
        {"bullets": [
            "초기: 짧고 불완전한 요약",
            "개선: 요약 비율, 형식 명시 → 체계적 요약 완성"
        ]},
        {"section": "사례 2: 질문 생성 품질 개선"},
        {"bullets": [
            "초기: 쉬운 질문만 생성",
            "개선: 난이도별 형식 명시 → 다양한 질문 완성"
        ]},
        {"section": "사례 3: AI 피드백 개선"},
        {"bullets": [
            "초기: 단순 맞/틀림 피드백",
            "개선: 상세 평가 기준 → 교육적 피드백 완성"
        ]}
    ], 6)

    add_content_slide(prs, "최종 결과물 시연", [
        {"section": "사용 흐름"},
        {"bullets": [
            "입력: 강의 노트 텍스트 입력 또는 파일 업로드",
            "처리: AI가 분석 (로딩 화면)",
            "대시보드: 요약본, 개념, 질문 10개 각각 제시",
            "복습 모드: 질문 → 답변 입력 → AI 피드백",
            "완료: 개인화된 복습 일정 추천"
        ]},
        {"section": "주요 기능"},
        {"bullets": [
            "메인 페이지, 대시보드, 요약 보기",
            "개념 목록, 복습 모드, 복습 일정"
        ]}
    ], 7)

    add_content_slide(prs, "마무리 및 창의성", [
        {"section": "핵심 창의성"},
        {"bullets": [
            "1️⃣ 단순 요약 → 완전한 학습 플랫폼으로 확장",
            "2️⃣ 일방적 AI 생성 → 튜터링 상호작용 제공",
            "3️⃣ 사용자 복습 일정 → 과학적 복습 시기 추천"
        ]},
        {"section": "기대 효과"},
        {"bullets": [
            "복습 시간: 50% 감소",
            "학습 효율: 30% 증가",
            "학습 동기: 대화형 상호작용으로 증가"
        ]}
    ], 8)

    output_path = "/Users/sooin/Documents/kiwi brain/생성형AI활용/텀프로젝트/AI_강의노트_복습도우미_발표_v2.pptx"
    prs.save(output_path)
    print(f"✓ PPTX v2 파일 생성 완료: {output_path}")
    return output_path

if __name__ == "__main__":
    create_pptx()

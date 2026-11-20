#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pptx import Presentation
from pptx.util import Inches, Pt
import os

def validate_layout_v2():
    """PPTX v2 레이아웃 고급 검증"""
    file_path = "/Users/sooin/Documents/kiwi brain/생성형AI활용/텀프로젝트/AI_강의노트_복습도우미_발표_v2.pptx"

    print("=" * 70)
    print("PPTX v2 레이아웃 고급 검증")
    print("=" * 70)

    if not os.path.exists(file_path):
        print("❌ 파일이 존재하지 않습니다")
        return False

    try:
        prs = Presentation(file_path)
        print("✓ PPTX 파일 로드 성공\n")
    except Exception as e:
        print(f"❌ PPTX 로드 실패: {e}")
        return False

    # 슬라이드별 상세 검증
    for slide_num, slide in enumerate(prs.slides):
        print(f"\n{'=' * 70}")
        print(f"슬라이드 {slide_num + 1} 검증")
        print('=' * 70)

        # 모든 텍스트 박스 추출
        text_boxes = []
        for shape in slide.shapes:
            if hasattr(shape, "text_frame"):
                text_frame = shape.text_frame
                if text_frame.text.strip():
                    left = shape.left / 914400  # EMU to inches
                    top = shape.top / 914400
                    width = shape.width / 914400
                    height = shape.height / 914400
                    text = text_frame.text.strip()

                    text_boxes.append({
                        'text': text,
                        'left': left,
                        'top': top,
                        'right': left + width,
                        'bottom': top + height,
                        'width': width,
                        'height': height
                    })

        if not text_boxes:
            print("⚠️  텍스트 박스 없음")
            continue

        # 위치순 정렬
        text_boxes.sort(key=lambda x: (x['top'], x['left']))

        # 각 텍스트 박스 출력
        print(f"\n📍 텍스트 박스 위치 및 크기:")
        for idx, box in enumerate(text_boxes):
            print(f"\n  [{idx+1}] {box['text'][:40]}{'...' if len(box['text']) > 40 else ''}")
            print(f"      위치: ({box['left']:.2f}\", {box['top']:.2f}\") " +
                  f"→ ({box['right']:.2f}\", {box['bottom']:.2f}\")")
            print(f"      크기: {box['width']:.2f}\" × {box['height']:.2f}\"")
            print(f"      텍스트 길이: {len(box['text'])}자")

        # 겹침 감지
        print(f"\n🔍 겹침 감지:")
        overlaps = []
        for i in range(len(text_boxes)):
            for j in range(i+1, len(text_boxes)):
                box1 = text_boxes[i]
                box2 = text_boxes[j]

                # 겹침 판정 (상하 겹침)
                if box1['bottom'] > box2['top']:
                    overlap_amount = box1['bottom'] - box2['top']
                    if overlap_amount > 0.05:  # 0.05인치 이상 겹침
                        overlaps.append({
                            'box1': box1['text'][:30],
                            'box2': box2['text'][:30],
                            'overlap': overlap_amount
                        })

        if overlaps:
            print("  ⚠️  겹침 발견:")
            for overlap in overlaps:
                print(f"    - '{overlap['box1']}...' 과 '{overlap['box2']}...' " +
                      f"({overlap['overlap']:.3f}\" 겹침)")
        else:
            print("  ✓ 겹침 없음")

        # 공간 활용도
        print(f"\n📊 슬라이드 공간 활용:")
        if text_boxes:
            min_top = min(b['top'] for b in text_boxes)
            max_bottom = max(b['bottom'] for b in text_boxes)
            used_height = max_bottom - min_top
            total_height = 7.5  # 표준 슬라이드 높이
            usage_percent = (used_height / total_height) * 100

            print(f"  사용 높이: {used_height:.2f}\" ({usage_percent:.1f}%)")
            print(f"  미사용 하단: {(7.5 - max_bottom):.2f}\"")

            if usage_percent < 60:
                print(f"  ⚠️  공간 활용도 낮음 (60% 미만)")
            else:
                print(f"  ✓ 공간 활용도 양호")

    print("\n" + "=" * 70)
    print("검증 완료")
    print("=" * 70)
    return True

if __name__ == "__main__":
    validate_layout_v2()

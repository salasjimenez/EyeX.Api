#!/usr/bin/env python3
"""Extend the existing four-backend HTTP parity suite without replacing it.

Usage: python3 tests/parity_extended.py --wait 120
       python3 tests/parity_extended.py --list-cases
"""
from __future__ import annotations

import sys
import parity as legacy
from parity import Case

_ORIGINAL_CASES = legacy.cases
DISCLAIMER = 'Resultado orientativo. No es un diagnóstico médico.'


def answer_case(name: str, flags: dict[str, bool], suggested: str, severity: str,
                high_contrast: bool) -> Case:
    answers = {
        'reds_look_darker': False,
        'green_brown_confusion': False,
        'blue_yellow_confusion': False,
        'colors_look_gray': False,
        **flags,
    }
    return Case(name, 'POST', '/api/v1/test/suggest', {'answers': answers},
                expected_json={
                    'suggested_type': suggested,
                    'severity': severity,
                    'high_contrast': high_contrast,
                    'disclaimer': DISCLAIMER,
                })


def extended_cases() -> list[Case]:
    return [
        answer_case('suggest-red-green-indicator', {'red_green_confusion': True},
                    'deuteranopia', 'mild', False),
        answer_case('suggest-red-black-indicator', {'red_black_confusion': True},
                    'protanopia', 'mild', False),
        answer_case('suggest-blue-green-indicator', {'blue_green_confusion': True},
                    'tritanopia', 'mild', False),
        answer_case('suggest-yellow-pink-indicator', {'yellow_pink_confusion': True},
                    'tritanopia', 'mild', False),
        answer_case('suggest-low-saturation-indicator', {'low_saturation_confusion': True},
                    'achromatopsia', 'severe', True),
        answer_case('suggest-gray-indicator', {'colors_look_gray': True},
                    'achromatopsia', 'severe', True),
        answer_case('suggest-all-disabled', {}, 'normal', 'mild', False),
        Case('feedback-valid-normal', 'POST', '/api/v1/feedback',
             {'suggested_type': 'normal', 'helpful': True},
             expected_json={'status': 'recorded'}),
        Case('feedback-missing-helpful', 'POST', '/api/v1/feedback',
             {'suggested_type': 'protanopia'}, 400,
             {'error': 'invalid_feedback', 'message': 'Feedback inválido'}),
        Case('feedback-nonboolean-helpful', 'POST', '/api/v1/feedback',
             {'suggested_type': 'tritanopia', 'helpful': 'yes'}, 400,
             {'error': 'invalid_feedback', 'message': 'Feedback inválido'}),
        Case('negative-severity', 'POST', '/api/v1/simulate',
             {'hex': '#ABCDEF', 'type': 'protanopia', 'severity': -0.1}, 400,
             {'error': 'invalid_parameter', 'message': 'severity debe estar entre 0 y 1'}),
        Case('batch-over-limit', 'POST', '/api/v1/simulate/batch',
             {'colors': ['#123456'] * 257, 'type': 'deuteranopia', 'severity': 0.5}, 400,
             {'error': 'invalid_request', 'message': 'colors debe contener entre 1 y 256 colores'}),
    ]


def all_cases() -> list[Case]:
    checks = _ORIGINAL_CASES() + extended_cases()
    names = [case.name for case in checks]
    if len(names) != len(set(names)):
        raise RuntimeError('Duplicate HTTP parity case names')
    return checks


legacy.cases = all_cases

if __name__ == '__main__':
    if '--list-cases' in sys.argv:
        for case in all_cases():
            print(case.name)
        print(f'PARITY_CASES={len(all_cases())}')
    else:
        raise SystemExit(legacy.main())

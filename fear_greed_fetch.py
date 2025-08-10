# -*- coding: utf-8 -*-
from datetime import datetime
from utils.logger_util import LoggerUtil


class FearGreedFetcher:
    """CNN Fear & Greed Index 수집기 (간결 버전)

    fear-and-greed 라이브러리의 공식 사용 예시를 따릅니다.
    """

    def __init__(self):
        self.logger = LoggerUtil().get_logger()

    def classify_fgi(self, value):
        """FGI 값(0~100) 분류

        - 0 ~ 24 → 극단적 공포 (Extreme Fear)
        - 25 ~ 44 → 공포 (Fear)
        - 45 ~ 55 → 중립 (Neutral)
        - 56 ~ 75 → 탐욕 (Greed)
        - 76 ~ 100 → 극단적 탐욕 (Extreme Greed)
        """
        if value is None:
            return None, None

        if 0 <= value <= 24:
            return "극단적 공포", "Extreme Fear"
        if 25 <= value <= 44:
            return "공포", "Fear"
        if 45 <= value <= 55:
            return "중립", "Neutral"
        if 56 <= value <= 75:
            return "탐욕", "Greed"
        return "극단적 탐욕", "Extreme Greed"

    def get_latest_fgi(self):
        """최신 Fear & Greed Index 반환

        Returns:
            dict | None: { value, status_kr, status_en, timestamp }
        """
        try:
            import fear_and_greed

            fgi = fear_and_greed.get()
            # fgi: FearGreedIndex(value: float, description: str, last_update: datetime)
            value_now = fgi.value
            desc_en = fgi.description  # e.g., 'fear', 'extreme greed'
            last_update = fgi.last_update

            # 값 정규화 및 상태 매핑
            value_int = int(round(value_now)) if isinstance(value_now, (int, float)) else None
            status_kr, status_en_by_value = self.classify_fgi(value_int)

            # 라이브러리의 description이 제공되면 영어 상태에 우선 반영
            status_en = (desc_en or status_en_by_value or "").strip().title() if desc_en else status_en_by_value

            result = {
                "value": value_int,
                "status_kr": status_kr,
                "status_en": status_en,
                "timestamp": (last_update or datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S"),
            }

            self.logger.info(
                f"Fear & Greed Index: {result['value']} ({result['status_kr']} / {result['status_en']}), 업데이트: {result['timestamp']}"
            )
            return result
        except Exception as exc:
            self.logger.error(f"Fear & Greed Index 수집 중 오류: {str(exc)}")
            return None

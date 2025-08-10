import yfinance as yf
from datetime import datetime, timedelta
from utils.logger_util import LoggerUtil


class VIXAnalyzer:
    """VIX(변동성 지수) 분석기

    - 야후파이낸스 `^VIX` 종가를 조회
    - 종가에 따른 상태 분류 반환
    """

    def __init__(self):
        self.logger = LoggerUtil().get_logger()
        self.symbol = "^VIX"

    def get_vix_data(self, days: int = 60):
        """VIX 데이터 조회

        Args:
            days: 조회 기간(일)

        Returns:
            pandas.DataFrame | None
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            self.logger.info(
                f"{self.symbol} 데이터 수집 시작 ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})"
            )

            ticker = yf.Ticker(self.symbol)
            data = ticker.history(start=start_date, end=end_date)

            if data is None or data.empty:
                self.logger.error("VIX 데이터를 가져올 수 없습니다.")
                return None

            self.logger.info(f"VIX 데이터 수집 성공: {len(data)}개 레코드")
            return data

        except Exception as exc:
            self.logger.error(f"VIX 데이터 수집 중 오류: {str(exc)}")
            return None

    def classify_vix(self, close_value: float):
        """VIX 종가에 따른 상태 분류

        구간:
        - 0 ~ 15 : 매우 안정
        - 15 ~ 20 : 안정
        - 20 ~ 30 : 경계
        - 30 ~ 40 : 불안
        - 40 이상 : 위기
        """
        # 하한 포함, 상한 미포함 구간 처리 (마지막 구간은 상한 없음)
        if close_value < 15:
            return "매우 안정"
        if close_value < 20:
            return "안정"
        if close_value < 30:
            return "경계"
        if close_value < 40:
            return "불안"
        return "위기"

    def get_latest_vix(self):
        """최신 VIX 정보 반환

        Returns:
            dict | None: { symbol, close, status, timestamp }
        """
        try:
            data = self.get_vix_data(days=60)
            if data is None or data.empty:
                return None

            close_value = float(round(data["Close"].iloc[-1], 2))
            status = self.classify_vix(close_value)

            result = {
                "symbol": self.symbol,
                "close": close_value,
                "status": status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            self.logger.info(
                f"VIX 최신 종가: {close_value} (상태: {status})"
            )
            return result

        except Exception as exc:
            self.logger.error(f"VIX 분석 중 오류: {str(exc)}")
            return None

    def format_vix_section(self, vix_info):
        """텔레그램 메시지용 VIX 섹션 생성"""
        if not vix_info:
            return "🌪 <b>VIX 변동성 지표</b>\n   데이터를 가져올 수 없습니다.\n\n"

        status_emoji = {
            "매우 안정": "🟢",
            "안정": "🟢",
            "경계": "🟡",
            "불안": "🟠",
            "위기": "🔴",
        }.get(vix_info.get("status", "경계"), "🟡")

        section = "🌪 <b>VIX 변동성 지표</b>\n"
        section += f"   VIX 종가: {vix_info['close']}\n"
        section += f"   상태: {status_emoji} {vix_info['status']}\n\n"
        return section



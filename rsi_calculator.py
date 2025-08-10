import yfinance as yf
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils.logger_util import LoggerUtil
import ta

load_dotenv()

class RSICalculator:
    def __init__(self):
        self.logger = LoggerUtil().get_logger()
        self.rsi_period = int(os.getenv('RSI_PERIOD', 14))
        self.oversold_threshold = float(os.getenv('RSI_OVERSOLD_THRESHOLD', 30))
        self.overbought_threshold = float(os.getenv('RSI_OVERBOUGHT_THRESHOLD', 70))
        
    def calculate_rsi(self, prices, period=None):
        """
        RSI(Relative Strength Index) 계산 - 표준 Wilder's Smoothing Method
        
        Args:
            prices: 주가 데이터 (pandas Series)
            period: RSI 계산 기간 (기본값: 환경변수에서 설정)
        
        Returns:
            RSI 값 (float)
        """
        if period is None:
            period = self.rsi_period
            
        if len(prices) < period + 1:
            self.logger.warning(f"RSI 계산을 위한 데이터가 부족합니다. 필요: {period + 1}, 현재: {len(prices)}")
            return None
        
        try:
            # 가격 변화량 계산
            delta = prices.diff()[1:]  # 첫 번째 NaN 제거
            
            # 상승분과 하락분 분리
            gain = pd.Series(index=delta.index, dtype=float)
            loss = pd.Series(index=delta.index, dtype=float)
            
            gain = delta.where(delta > 0, 0.0)
            loss = (-delta).where(delta < 0, 0.0)
            
            # 첫 번째 평균값 계산 (단순 평균)
            avg_gain = gain.iloc[:period].mean()
            avg_loss = loss.iloc[:period].mean()
            
            # Wilder's smoothing으로 나머지 값들 계산
            gains = [avg_gain]
            losses = [avg_loss]
            
            for i in range(period, len(gain)):
                avg_gain = (avg_gain * (period - 1) + gain.iloc[i]) / period
                avg_loss = (avg_loss * (period - 1) + loss.iloc[i]) / period
                gains.append(avg_gain)
                losses.append(avg_loss)
            
            # RSI 계산
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi)
            
        except Exception as e:
            self.logger.error(f"RSI 계산 중 오류: {str(e)}")
            return None
    
    def calculate_rsi_ta(self, prices, period=None):
        """
        ta 라이브러리를 사용한 RSI 계산 (검증용)
        
        Args:
            prices: 주가 데이터 (pandas Series)
            period: RSI 계산 기간 (기본값: 환경변수에서 설정)
        
        Returns:
            RSI 값 (float)
        """
        if period is None:
            period = self.rsi_period
            
        try:
            rsi = ta.momentum.RSIIndicator(close=prices, window=period)
            rsi_value = rsi.rsi().iloc[-1]
            return float(rsi_value)
        except Exception as e:
            self.logger.error(f"ta 라이브러리 RSI 계산 중 오류: {str(e)}")
            return None
    
    def get_stock_data(self, symbol, days=60):
        """
        주식 데이터 가져오기
        
        Args:
            symbol: 주식 심볼 (예: 'SPY', 'QQQ', 'DIA')
            days: 가져올 일수 (기본값: 60일)
        
        Returns:
            pandas DataFrame: 주식 데이터
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            self.logger.info(f"{symbol} 주식 데이터 수집 시작 ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})")
            
            stock = yf.Ticker(symbol)
            data = stock.history(start=start_date, end=end_date)
            
            if data.empty:
                self.logger.error(f"{symbol} 데이터를 가져올 수 없습니다.")
                return None
                
            self.logger.info(f"{symbol} 데이터 수집 성공: {len(data)}개 레코드")
            return data
            
        except Exception as e:
            self.logger.error(f"{symbol} 데이터 수집 중 오류 발생: {str(e)}")
            return None
    
    def get_rsi_for_symbol(self, symbol):
        """
        특정 심볼의 RSI 계산
        
        Args:
            symbol: 주식 심볼
        
        Returns:
            dict: RSI 정보 (rsi_value, current_price, symbol, status)
        """
        try:
            # 주식 데이터 가져오기
            data = self.get_stock_data(symbol)
            
            if data is None or data.empty:
                return None
                
            # RSI 계산 (ta 라이브러리 사용)
            rsi_value = self.calculate_rsi_ta(data['Close'])
            
            if rsi_value is None:
                return None
                
            # 현재 가격
            current_price = data['Close'].iloc[-1]
            
            # RSI 상태 판단
            status = "정상"
            if rsi_value <= self.oversold_threshold:
                status = "과매도"
            elif rsi_value >= self.overbought_threshold:
                status = "과매수"
            
            result = {
                'symbol': symbol,
                'rsi_value': round(rsi_value, 2),
                'current_price': round(current_price, 2),
                'status': status,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.logger.info(f"{symbol} RSI 계산 완료: {rsi_value:.2f} ({status})")
            return result
            
        except Exception as e:
            self.logger.error(f"{symbol} RSI 계산 중 오류 발생: {str(e)}")
            return None
    
    def get_rsi_for_symbols(self, symbols=['SPY', 'QQQ', 'DIA']):
        """
        여러 심볼의 RSI 계산
        
        Args:
            symbols: 주식 심볼 리스트
        
        Returns:
            list: RSI 정보 리스트
        """
        results = []
        
        for symbol in symbols:
            result = self.get_rsi_for_symbol(symbol)
            if result:
                results.append(result)
                
        return results
    
    # 메시지 포맷팅은 main.py로 이동

# 테스트용 메인 함수
if __name__ == "__main__":
    calculator = RSICalculator()
    
    # RSI 계산 방법 비교 테스트
    print("=== RSI 계산 방법 비교 ===")
    symbols = ['SPY', 'QQQ', 'DIA']
    
    for symbol in symbols:
        data = calculator.get_stock_data(symbol)
        if data is not None:
            manual_rsi = calculator.calculate_rsi(data['Close'])
            ta_rsi = calculator.calculate_rsi_ta(data['Close'])
            
            print(f"{symbol}:")
            print(f"  Manual RSI: {manual_rsi:.2f}")
            print(f"  TA Library RSI: {ta_rsi:.2f}")
            print(f"  Current Price: ${data['Close'].iloc[-1]:.2f}")
            print()
    
    # 여러 심볼 테스트 (ta 라이브러리 사용)
    print("=== 여러 심볼 RSI 테스트 (TA Library) ===")
    results = calculator.get_rsi_for_symbols(symbols)
    
    for result in results:
        print(result)
    
    # 포맷팅 테스트는 main.py의 format_market_message를 사용하세요.
# -*- coding: utf-8 -*-
import sys
from dotenv import load_dotenv
from utils.logger_util import LoggerUtil
from utils.telegram_util import TelegramUtil
from rsi_calculator import RSICalculator

# 환경변수 로드
load_dotenv()

def main():
    """메인 실행 함수"""
    logger = LoggerUtil().get_logger()
    
    try:
        logger.info("RSI 트래커 프로그램 시작")
        
        # RSI 계산기 초기화
        rsi_calc = RSICalculator()
        logger.info("RSI 계산기 초기화 완료")
        
        # 텔레그램 유틸 초기화
        telegram = TelegramUtil()
        logger.info("텔레그램 유틸 초기화 완료")
        
        # 추적할 주식 심볼들
        symbols = ['SPY', 'QQQ', 'DIA']
        logger.info(f"추적 대상 심볼: {symbols}")
        
        # RSI 계산
        logger.info("RSI 계산 시작")
        rsi_results = rsi_calc.get_rsi_for_symbols(symbols)
        
        if not rsi_results:
            error_msg = "RSI 데이터를 가져올 수 없습니다."
            logger.error(error_msg)
            telegram.send_message(f"❌ 오류: {error_msg}")
            return
        
        logger.info(f"RSI 계산 완료: {len(rsi_results)}개 심볼")
        
        # 알림이 필요한 심볼들 확인
        alert_symbols = []
        for result in rsi_results:
            if result['status'] in ['과매도', '과매수']:
                alert_symbols.append(result)
        
        # 텔레그램 메시지 전송
        message = rsi_calc.format_rsi_message(rsi_results)
        
        if alert_symbols:
            # 알림이 필요한 경우
            alert_message = f"🚨 <b>RSI 알림</b>\n\n"
            for symbol_data in alert_symbols:
                status_emoji = "🔴" if symbol_data['status'] == "과매도" else "🟢"
                alert_message += f"{status_emoji} {symbol_data['symbol']}: RSI {symbol_data['rsi_value']} ({symbol_data['status']})\n"
            alert_message += f"\n{message}"
            
            telegram.send_message(alert_message)
            logger.info(f"RSI 알림 전송 완료: {len(alert_symbols)}개 심볼에서 임계값 도달")
        else:
            # 일반 상황 보고
            telegram.send_message(message)
            logger.info("RSI 현황 보고 전송 완료: 모든 심볼 정상 범위")
        
        # 개별 심볼 상세 로그
        for result in rsi_results:
            logger.info(f"{result['symbol']}: RSI={result['rsi_value']}, 가격=${result['current_price']}, 상태={result['status']}")
        
        logger.info("RSI 트래커 프로그램 정상 종료")
        
    except Exception as e:
        error_msg = f"프로그램 실행 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        
        try:
            telegram = TelegramUtil()
            telegram.send_message(f"❌ RSI 트래커 오류\n\n{error_msg}")
        except:
            logger.error("텔레그램 오류 메시지 전송 실패")
        
        sys.exit(1)

def test_mode():
    """테스트 모드 실행"""
    logger = LoggerUtil().get_logger()
    
    try:
        logger.info("RSI 트래커 테스트 모드 시작")
        
        # RSI 계산기 테스트
        rsi_calc = RSICalculator()
        
        # 텔레그램 테스트
        telegram = TelegramUtil()
        
        # 테스트 메시지 전송
        test_message = "🧪 <b>RSI 트래커 테스트</b>\n\n테스트 메시지가 정상적으로 전송되었습니다."
        telegram.send_test_message(test_message)
        logger.info("테스트 메시지 전송 완료")
        
        # RSI 계산 테스트
        symbols = ['SPY']  # 테스트용 1개 심볼만
        results = rsi_calc.get_rsi_for_symbols(symbols)
        
        if results:
            message = rsi_calc.format_rsi_message(results)
            telegram.send_test_message(f"📊 테스트 결과:\n\n{message}")
            logger.info("RSI 계산 테스트 완료")
        else:
            logger.error("RSI 계산 테스트 실패")
        
    except Exception as e:
        logger.error(f"테스트 모드 실행 중 오류: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # 명령행 인수 확인
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_mode()
    else:
        main()
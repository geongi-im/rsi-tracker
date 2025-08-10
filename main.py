# -*- coding: utf-8 -*-
import sys
from dotenv import load_dotenv
from utils.logger_util import LoggerUtil
from utils.telegram_util import TelegramUtil
from rsi_calculator import RSICalculator
from vix_analysis import VIXAnalyzer

# 텔레그램 메시지 포맷팅을 이 파일에서 처리
def format_market_message(rsi_data_list, vix_info):
    if not rsi_data_list:
        return "RSI 데이터를 가져올 수 없습니다."

    # 지수 설명 매핑
    index_descriptions = {
        'SPY': 'S&P500',
        'QQQ': 'Nasdaq',
        'DIA': 'Dow-Jones'
    }

    message = "📊 <b>미국 시장 현황 분석</b>\n\n"

    # VIX 섹션
    if vix_info is not None:
        vix_status_emoji = {
            "매우 안정": "🟢",
            "안정": "🟢",
            "경계": "🟡",
            "불안": "🟠",
            "위기": "🔴",
        }.get(vix_info.get("status", "경계"), "🟡")
        message += "🌪 <b>VIX 변동성 지표</b>\n"
        message += f"   VIX 종가: {vix_info.get('close', 'N/A')}\n"
        message += f"   상태: {vix_status_emoji} {vix_info.get('status', 'N/A')}\n\n"

    # 주요 지수 RSI 섹션
    for data in rsi_data_list:
        status_emoji = "🔴" if data['status'] == "과매도" else "🟢" if data['status'] == "과매수" else "🔵"

        symbol_display = data['symbol']
        if symbol_display in index_descriptions:
            symbol_display = f"{data['symbol']} ({index_descriptions[data['symbol']]})"

        message += f"{status_emoji} <b>{symbol_display}</b>\n"
        message += f"   RSI: {data['rsi_value']}\n"
        message += f"   현재가: ${data['current_price']}\n"
        message += f"   상태: {data['status']}\n\n"

    message += f"⏰ 업데이트: {rsi_data_list[0]['timestamp']}\n"

    return message

# 환경변수 로드
load_dotenv()

def main():
    """메인 실행 함수"""
    logger = LoggerUtil().get_logger()
    
    try:
        logger.info("미국 시장 현황 분석 프로그램 시작")
        
        # RSI 계산기 초기화
        rsi_calc = RSICalculator()
        logger.info("RSI 계산기 초기화 완료")
        
        # 텔레그램 유틸 초기화
        telegram = TelegramUtil()
        logger.info("텔레그램 유틸 초기화 완료")

        # VIX 분석기 초기화
        vix = VIXAnalyzer()
        logger.info("VIX 분석기 초기화 완료")
        
        # 추적할 주식 심볼들
        symbols = ['SPY', 'QQQ', 'DIA']
        logger.info(f"추적 대상 심볼: {symbols}")
        
        # RSI 계산
        logger.info("데이터 계산 시작 (RSI, VIX)")
        rsi_results = rsi_calc.get_rsi_for_symbols(symbols)
        vix_info = vix.get_latest_vix()
        
        if not rsi_results:
            error_msg = "RSI 데이터를 가져올 수 없습니다."
            logger.error(error_msg)
            telegram.send_message(f"❌ 오류: {error_msg}")
            return
        
        logger.info(f"RSI 계산 완료: {len(rsi_results)}개 심볼, VIX 수집: {'성공' if vix_info else '실패'}")
        
        # 알림이 필요한 심볼들 확인
        alert_symbols = []
        for result in rsi_results:
            if result['status'] in ['과매도', '과매수']:
                alert_symbols.append(result)
        
        # 텔레그램 메시지 전송
        message = format_market_message(rsi_results, vix_info)
        
        if alert_symbols:
            # 지수 설명 매핑
            index_descriptions = {
                'SPY': 'S&P500',
                'QQQ': 'Nasdaq', 
                'DIA': 'Dow-Jones'
            }
            
            # 알림이 필요한 경우
            alert_message = f"🚨 <b>미국 시장 현황 분석 - 알림</b>\n\n"
            for symbol_data in alert_symbols:
                status_emoji = "🔴" if symbol_data['status'] == "과매도" else "🟢"
                
                # 지수 설명 추가
                symbol_display = symbol_data['symbol']
                if symbol_display in index_descriptions:
                    symbol_display = f"{symbol_data['symbol']} ({index_descriptions[symbol_data['symbol']]})"
                
                alert_message += f"{status_emoji} {symbol_display}: RSI {symbol_data['rsi_value']} ({symbol_data['status']})\n"
            alert_message += f"\n{message}"
            
            telegram.send_message(alert_message)
            logger.info(f"RSI 알림 전송 완료: {len(alert_symbols)}개 심볼에서 임계값 도달")
        else:
            # 일반 상황 보고
            telegram.send_message(message)
            logger.info("미국 시장 현황 보고 전송 완료: 모든 심볼 정상 범위")
        
        # 개별 심볼 상세 로그
        for result in rsi_results:
            logger.info(f"{result['symbol']}: RSI={result['rsi_value']}, 가격=${result['current_price']}, 상태={result['status']}")
        
        logger.info("미국 시장 현황 분석 프로그램 정상 종료")
        
    except Exception as e:
        error_msg = f"프로그램 실행 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        
        try:
            telegram = TelegramUtil()
            telegram.send_message(f"❌ 미국 시장 현황 분석 오류\n\n{error_msg}")
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

        # VIX 분석기 테스트
        vix = VIXAnalyzer()
        
        # 테스트 메시지 전송
        test_message = "🧪 <b>미국 시장 현황 분석 - 테스트</b>\n\n테스트 메시지가 정상적으로 전송되었습니다."
        telegram.send_test_message(test_message)
        logger.info("테스트 메시지 전송 완료")
        
        # RSI 계산 테스트
        symbols = ['SPY']  # 테스트용 1개 심볼만
        results = rsi_calc.get_rsi_for_symbols(symbols)
        vix_info = vix.get_latest_vix()
        
        if results:
            message = format_market_message(results, vix_info)
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
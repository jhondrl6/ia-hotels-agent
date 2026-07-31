"""Comparativa financiera: datos reales (Tier A) vs ejecucion actual (Tier B)"""
import sys
sys.path.insert(0, '.')

from modules.financial_engine.scenario_calculator import ScenarioCalculator, HotelFinancialData, ScenarioType

# --- DATOS REALES (Tier A, confidence 0.95) ---
real = HotelFinancialData(
    rooms=34,
    adr_cop=290000,
    occupancy_rate=0.7843,
    direct_channel_percentage=0.40,
    ota_commission_rate=0.15,
    adr_source='onboarding_confirmado',
    occupancy_source='onboarding_confirmado',
    channel_source='onboarding_confirmado',
)

# --- DATOS USADOS en ejecucion actual (Tier B) ---
usado = HotelFinancialData(
    rooms=10,
    adr_cop=420000,
    occupancy_rate=0.512,
    direct_channel_percentage=0.20,
    ota_commission_rate=0.15,
    adr_source='regional_v410',
    occupancy_source='regional',
    channel_source='default',
)

calc = ScenarioCalculator()

bd_real = calc.calculate_breakdown(real)
bd_usado = calc.calculate_breakdown(usado)

sc_real = calc.calculate_scenarios(real)
sc_usado = calc.calculate_scenarios(usado)

print('='*70)
print('COMPARATIVA: DATOS REALES (Tier A) vs EJECUCION ACTUAL (Tier B)')
print('='*70)

print()
print('--- INPUT DATA ---')
print(f'  REAL:  rooms=34  adr=290K  occ=78.4%  direct=40%  source=onboarding')
print(f'  USADO: rooms=10  adr=420K  occ=51.2%  direct=20%  source=regional')

print()
print('--- CAPA 1: Comision OTA (verificable) ---')
r_ota = int(bd_real.monthly_ota_commission_cop)
u_ota = int(bd_usado.monthly_ota_commission_cop)
print(f'  REAL:  {r_ota:,} COP = {bd_real.ota_commission_basis}')
print(f'  USADO: {u_ota:,} COP = {bd_usado.ota_commission_basis}')
print(f'  DELTA: {r_ota - u_ota:,} COP (real es {r_ota/u_ota:.1f}x mayor)')

print()
print('--- CAPA 2A: Shift OTA->Directo ---')
print(f'  REAL:  {int(bd_real.shift_savings_cop):,} COP ({bd_real.shift_percentage*100:.0f}% shift)')
print(f'  USADO: {int(bd_usado.shift_savings_cop):,} COP ({bd_usado.shift_percentage*100:.0f}% shift)')

print()
print('--- CAPA 2B: Boost IA ---')
print(f'  REAL:  {int(bd_real.ia_revenue_cop):,} COP')
print(f'  USADO: {int(bd_usado.ia_revenue_cop):,} COP')

print()
print('--- EVIDENCE TIER ---')
print(f'  REAL:  {bd_real.evidence_tier}')
print(f'  USADO: {bd_usado.evidence_tier}')

print()
print('--- ESCENARIOS (monthly_loss_cop) ---')
print(f'  CONSERVADOR: REAL={int(sc_real[ScenarioType.CONSERVATIVE].monthly_loss_cop):,} | USADO={int(sc_usado[ScenarioType.CONSERVATIVE].monthly_loss_cop):,}')
print(f'  REALISTA:    REAL={int(sc_real[ScenarioType.REALISTIC].monthly_loss_cop):,} | USADO={int(sc_usado[ScenarioType.REALISTIC].monthly_loss_cop):,}')
print(f'  OPTIMISTA:   REAL={int(sc_real[ScenarioType.OPTIMISTIC].monthly_loss_cop):,} | USADO={int(sc_usado[ScenarioType.OPTIMISTIC].monthly_loss_cop):,}')

print()
print('--- IMPACTO 6 MESES (pain_ratio 20% x recovery 35%) ---')
real_6m = sc_real[ScenarioType.REALISTIC].monthly_loss_cop * 6
usado_6m = sc_usado[ScenarioType.REALISTIC].monthly_loss_cop * 6
r_rec = int(real_6m * 0.20 * 0.35)
u_rec = int(usado_6m * 0.20 * 0.35)
print(f'  REAL:  Fuga 6m={int(real_6m):,} | Recovery={r_rec:,} | ROICR={r_rec/2400000:.1f}x')
print(f'  USADO: Fuga 6m={int(usado_6m):,} | Recovery={u_rec:,} | ROICR={u_rec/2400000:.1f}x')

print()
print('--- PRICING IMPACT ---')
real_pain = 400000 / bd_real.monthly_ota_commission_cop
usado_pain = 400000 / bd_usado.monthly_ota_commission_cop
print(f'  REAL:  pain_ratio={real_pain:.4f} ({real_pain*100:.1f}%) - fee es solo {real_pain*100:.1f}% de la fuga real')
print(f'  USADO: pain_ratio={usado_pain:.4f} ({usado_pain*100:.1f}%) - fee parece mas significativo')

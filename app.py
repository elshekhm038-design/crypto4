import requests
import pandas as pd

# -------------------------------
# 1. جلب بيانات التداول
# -------------------------------
def get_binance_4h_volume():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)
    data = response.json()
    
    # نحول البيانات ل DataFrame
    df = pd.DataFrame(data)
    df = df[['symbol', 'quoteVolume']]  # quoteVolume بالـ USDT غالباً
    df['quoteVolume'] = df['quoteVolume'].astype(float)
    
    return df

# -------------------------------
# 2. افتراض بيانات سابقة (4 ساعات قبل)
# -------------------------------
# في الواقع، تحب تجيبها من API أو تخزن البيانات كل فترة
previous_df = get_binance_4h_volume()  # افتراضياً نكرر البيانات
# لاحقاً يمكن تحديثها كل 4 ساعات أو تخزينها

# -------------------------------
# 3. البيانات الحالية
# -------------------------------
current_df = get_binance_4h_volume()

# -------------------------------
# 4. دمج البيانات وحساب التغير
# -------------------------------
merged_df = pd.merge(current_df, previous_df, on='symbol', suffixes=('_current', '_previous'))

# التغير النسبي في السيولة
merged_df['liquidity_change_pct'] = ((merged_df['quoteVolume_current'] - merged_df['quoteVolume_previous'])
                                    / merged_df['quoteVolume_previous'].replace(0, 1)) * 100

# السيولة الجديدة
merged_df['new_liquidity'] = merged_df['quoteVolume_current'] - merged_df['quoteVolume_previous']

# -------------------------------
# 5. ترتيب العملات حسب التغير %
# -------------------------------
top_movers = merged_df.sort_values(by='liquidity_change_pct', ascending=False).head(30)

# -------------------------------
# 6. عرض النتائج
# -------------------------------
print(top_movers[['symbol', 'quoteVolume_previous', 'quoteVolume_current', 'new_liquidity', 'liquidity_change_pct']])

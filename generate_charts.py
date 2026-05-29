import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set a dark theme for a premium corporate look
plt.style.use('dark_background')
sns.set_theme(style="darkgrid", rc={"axes.facecolor": "#121212", "figure.facecolor": "#121212", "grid.color": "#333333", "text.color": "white", "axes.labelcolor": "white", "xtick.color": "white", "ytick.color": "white"})

df = pd.read_csv('benchmarks.csv')

fig, axs = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('RAG-NPU-Liquid Performance Scaling on AMD Strix Halo (Radeon 8060S)', fontsize=16, fontweight='bold', color='#00d2ff')

# Chart 1: Time To First Token
axs[0].plot(df['context_length_k'], df['ttft_avg_s'], marker='o', linewidth=2.5, color='#ff5252', label='Avg TTFT')
axs[0].set_title('Time-to-First-Token (TTFT)', fontsize=14)
axs[0].set_xlabel('Context Length (K Tokens)', fontsize=12)
axs[0].set_ylabel('Time (Seconds)', fontsize=12)
axs[0].set_xticks(df['context_length_k'])

# Chart 2: Prefill Speed
axs[1].plot(df['context_length_k'], df['prefill_avg_toks_per_s'], marker='s', linewidth=2.5, color='#00e676', label='Prefill Speed')
axs[1].set_title('Prefill Phase Speed', fontsize=14)
axs[1].set_xlabel('Context Length (K Tokens)', fontsize=12)
axs[1].set_ylabel('Tokens / Second', fontsize=12)
axs[1].set_xticks(df['context_length_k'])

# Chart 3: Decoding Speed
axs[2].plot(df['context_length_k'], df['decoding_avg_toks_per_s'], marker='^', linewidth=2.5, color='#2979ff', label='Decoding Speed')
axs[2].set_title('Decoding Phase Speed', fontsize=14)
axs[2].set_xlabel('Context Length (K Tokens)', fontsize=12)
axs[2].set_ylabel('Tokens / Second', fontsize=12)
axs[2].set_xticks(df['context_length_k'])
axs[2].set_ylim(bottom=0, top=70)

plt.tight_layout()

# Create assets folder if not exists
os.makedirs('assets', exist_ok=True)
plt.savefig('assets/benchmark_dashboard.png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
print("Dashboard generated successfully.")

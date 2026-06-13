#!/usr/bin/env python3
"""Conferência 7049: 09, 14, 25, 44, 67"""
import json
import os

RESULTADO = [9, 14, 25, 44, 67]

def main():
    print("=" * 50)
    print("CONFERÊNCIA 7049: 09, 14, 25, 44, 67")
    print("=" * 50)

    for opt, qtd in [(1, 56), (2, 70)]:
        fname = f"memory/quina_{qtd}_games_latest.json"
        if os.path.exists(fname):
            with open(fname) as f:
                data = json.load(f)
            games = [g['numbers'] for g in data.get('portfolio', [])]

            acertos = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0}
            for g in games:
                m = len(set(g) & set(RESULTADO))
                acertos[m] += 1

            print(f"\nOPÇÃO {opt} ({len(games)} jogos):")
            for i in [5, 4, 3, 2, 1]:
                if acertos[i] > 0:
                    print(f"  {i} acertos: {acertos[i]}")
            print(f"  0 acertos: {acertos[0]}")

if __name__ == "__main__":
    main()
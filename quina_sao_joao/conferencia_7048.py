#!/usr/bin/env python3
"""Conferência do concurso 7048 - 09, 25, 34, 56, 70"""
import json
import os

RESULTADO_7048 = [9, 25, 34, 56, 70]

def main():
    print("=" * 50)
    print("CONFERÊNCIA 7048: 09, 25, 34, 56, 70")
    print("=" * 50)

    # Carregar jogos
    for opt in [1, 2]:
        fname = f"memory/quina_{56 if opt==1 else 70}_games_latest.json"
        if os.path.exists(fname):
            with open(fname) as f:
                data = json.load(f)
            games = [g['numbers'] for g in data.get('portfolio', [])]

            acertos = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0}
            for g in games:
                m = len(set(g) & set(RESULTADO_7048))
                acertos[m] += 1

            print(f"\nOPÇÃO {opt}: {len(games)} jogos")
            print(f"  5 acertos: {acertos[5]}")
            print(f"  4 acertos: {acertos[4]}")
            print(f"  3 acertos: {acertos[3]}")
            print(f"  2 acertos: {acertos[2]}")
            print(f"  1 acerto:  {acertos[1]}")
            print(f"  0 acertos: {acertos[0]}")
        else:
            print(f"Arquivo {fname} não encontrado")

if __name__ == "__main__":
    main()
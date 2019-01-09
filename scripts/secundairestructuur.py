"""
Created on Wednesday 09 Janary 2018
Last update: -

@author: Michiel Stock
michielfmstock@gmail.com

Basic python module for project secondary protein structure.
"""

from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

P22eiwit = "MTDITANVVVSNPRPIFTESRSFKAVANGKIYIGQIDTDPVNPANQIPVYIENEDGSHVQITQPLIINAAGKIVYNGQLVKIVTVQGHSMAIYDANGSQVDYIANVLKYDPDQYSIEADKKFKYSVKLSDYPTLQDAASAAVDGLLIDRDYNFYGGETVDFGGKVLTIECKAKFIGDGNLIFTKLGKGSRIAGVFMESTTTPWVIKPWTDDNQWLTDAAAVVATLKQSKTDGYQPTVSDYVKFPGIETLLPPNAKGQNITSTLEIRECIGVEVHRASGLMAGFLFRGCHFCKMVDANNPSGGKDGIITFENLSGDWGKGNYVIGGRTSYGSVSSAQFLRNNGGFERDGGVIGFTSYRAGESGVKTWQGTVGSTTSRNYNLQFRDSVVIYPVWDGFDLGADTDMNPELDRPGDYPITQYPLHQLPLNHLIDNLLVRGALGVGFGMDGKGMYVSNITVEDCAGSGAYLLTHESVFTNIAIIDTNTKDFQANQIYISGACRVNGLRLIGIRSTDGQGLTIDAPNSTVSGITGMVDPSRINVANLAEEGLGNIRANSFGYDSAAIKLRIHKLSKTLDSGALYSHINGGAGSGSAYTQLTAISGSTPDAVSLKVNHKDCRGAEIPFVPDIASDDFIKDSSCFLPYWENNSTSLKALVKKPNGELVRLTLATL"

beta_platen = ["SRSF", "KIYIGQ", "VYIE", "HVQI", "QPLII", "IVY", "IVTVQ",
                "SMAIY", "QVDYIA", "SVK", "YPT", "VDGLLI", "TVD", "TIEC",
                "AKFI", "DGNLIFT", "RIAG", "FME", "WVI", "KTDGY", "STLEIRE",
                "EVHR", "SGLMAGFLFRG", "KMVD", "NNPSG", "IITFE", "LSGD", "YVIG",
                 "RTSY", "SAQFLRNN", "GVIG", "TSYR", "GVKT", "GTV", "NYN",
                 "QFRDSVVIY", "GFDL", "DMN", "LIDNLLVR", "LGVGFGMDGKG",
                 "YVSNITVED", "AGSGAYLLTHE", "VFTNIAIID", "QIYI", "RVNGLRL",
                 "TIDAPNSTVSGITG", "INVANL", "NIRANS", "GYDSAAIKL", "KTL",
                 "SGALYSHI", "AYTQLTAIS", "TPDAVSLKVN", "GAE", "VPD",
                 "DSSCFLPYWE", "SLKALVK", "LVRLTLA"]
# locaties beta-platen (start, stop)
regios = []
for bp in beta_platen:
    start = P22eiwit.find(bp)
    regios.append((start, start + len(bp)))

AZ_aantal = Counter(P22eiwit)
AZ_beta_platen_aantal = Counter()
for beta_plaat in beta_platen:
    AZ_beta_platen_aantal.update(beta_plaat)

aminozuren = AZ_aantal.keys()

AZ_totaal = sum(AZ_aantal.values())
AZ_beta_platen_totaal = sum(AZ_beta_platen_aantal.values())

prior_beta = AZ_beta_platen_totaal / AZ_totaal

AZ_prob = {}
AZ_prob_beta = {}
AZ_odds = {}
for AZ in sorted(aminozuren):
    AZ_prob[AZ] = AZ_aantal[AZ] / AZ_totaal
    AZ_prob_beta[AZ] = AZ_beta_platen_aantal[AZ] / AZ_beta_platen_totaal
    AZ_odds[AZ] = AZ_prob_beta[AZ] / AZ_prob[AZ]

def glijdendvenster(sequentie, k=5):
    # FIX: kansen groter dan 1?
    # DOC
    assert k > 0  and k % 2  # lengte van het venster is oneven
    n = len(sequentie)
    w = (k - 1) // 2
    posterior_kans = np.ones(n) * prior_beta
    odds_array = np.array([AZ_odds[AZ] for AZ in sequentie])
    for i in range(w, n-w):
        AZ = sequentie[i]
        posterior_kans[i] = np.prod([odds_array[i-w:i+w+1]]) * prior_beta
    return posterior_kans

def plot_glijdend_venster(sequentie, k=5):
    # DOC
    fig, ax = plt.subplots()
    ax.set_ylim([1e-4, 4])
    for start, stop:
        ax.fill_betweenx(start, 2, stop)

if __name__ == '__main__':

    # PRINT TABEL KANSEN
    peptide = "YSIEADKK"

    print("|  AZ  | totaal aantal | $\mathbf{P(A_i)}$ | aantal in $\beta$-plaat | $\mathbf{P(A_i\mid\beta\text{-plaat})}$ | $\mathbf{\frac{P(A_i\mid \beta\text{-plaat})}{P(A_i)}}$ |")
    print("|:---|:----|:----------|:-----|:-----|:----|")
    for AZ in sorted(aminozuren):
        odds = AZ_prob_beta[AZ] / AZ_prob[AZ]
        AZ_odds[AZ] = odds
        if AZ not in peptide:
            print("| {AZ} | {n_AZ} | {p_AZ:.4f} | {n_AZ_beta} | {p_AZ_beta:.4f} | {p_odds:.4f} |".format(
                    AZ=AZ,
                    n_AZ=AZ_aantal[AZ],
                    p_AZ=AZ_prob[AZ],
                    n_AZ_beta=AZ_beta_platen_aantal[AZ],
                    p_AZ_beta=AZ_prob_beta[AZ],
                    p_odds=odds
                    ))
        else:
            print("| {AZ} | {n_AZ} | ... | {n_AZ_beta} | ... | ... |".format(
                    AZ=AZ,
                    n_AZ=AZ_aantal[AZ],
                    n_AZ_beta=AZ_beta_platen_aantal[AZ],
                    ))
    print("| **Totaal** |  **{AZ_totaal}** | - | **{AZ_beta_platen_totaal}** | -|-|".format(
                AZ_totaal=AZ_totaal,
                AZ_beta_platen_totaal=AZ_beta_platen_totaal
            ))


    kans_beta = prior_beta
    for AZ in peptide:
        kans_beta *= AZ_odds[AZ]
    print("Kans dat {peptide} een beta-plaat is: {kans_beta:.4f}".format(
                peptide=peptide,
                kans_beta=kans_beta
            ))

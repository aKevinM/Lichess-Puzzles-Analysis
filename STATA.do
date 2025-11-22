*STATA 14.2

clear*
set more off
log close _all

cd ""

import delimited "lichess_db_puzzle_sample.csv", clear
save "lichess_db_puzzle_sample.dta", replace

import delimited "lichess_db_puzzle_uncleaned_sample.csv", clear
save "lichess_db_puzzle_uncleaned_sample.dta", replace

use ".\lichess_db_puzzle_sample.dta"

append using "lichess_db_puzzle_uncleaned_sample.dta", force

rename openingtags opening

split fen, parse(" ") gen(fen_part)
gen trait = ""
replace trait = "Noirs" if fen_part2 == "w"
replace trait = "Blancs" if fen_part2 == "b"

gen demicoups = real(fen_part5)
gen nb_coups = real(fen_part6)

drop fen_part*

gen puzzle_coups = wordcount(moves) / 2
gen premier_coup = word(moves, 1)
gen dernier_coup = word(moves, puzzle_coups)

drop fen moves gameurl

split themes, parse(" ")
display "terminé"

egen athemes_2 = concat(themes1 themes2), punct(" ")

drop themes*
rename athemes_2 themes




label var rating Classement
label var ratingdeviation "Déviation de Classement"
label var popularity Popularité
label var nbplays "Nb de fois joué"
label var opening Ouverture
label var trait Trait
label var demicoups "Demi-coups"
label var nb_coups "Nb de coups"
label var puzzle_coups "Solution"
label var premier_coup "Premier coup"
label var dernier_coup "Dernier coup"
label var themes "Thème"


gen difficulty="a"
replace difficulty="Facile" if rating<=1200
replace difficulty="Moyen" if rating>1200 & rating<=2000
replace difficulty="Difficile" if rating>2000
label var difficulty Difficulté



* Table 5
preserve
    contract themes
    gen freq_pourcent = _freq / 5311149
    gsort -_freq
    list themes _freq freq_pourcent in 1/8
restore

* Table 5
preserve
    contract opening
    gen freq_pourcent = _freq / 1077989
    gsort -_freq
    list opening _freq freq_pourcent in 1/9
restore

* Table 6
preserve
    contract premier_coup
    gen freq_pourcent = _freq / 5311149
    gsort -_freq
    list premier_coup _freq freq_pourcent in 1/8
restore

* Table 6
preserve
    keep if premier_coup != dernier_coup
    contract dernier_coup
    gen freq_pourcent = _freq / 5311149
    gsort -_freq
    list dernier_coup _freq freq_pourcent in 1/8
restore



*Statistiques descriptives
* Table 2
describe

* Table 3
summarize rating ratingdeviation popularity nbplays demicoups nb_coups ///
puzzle_coups

* Figure 1
histogram rating, normal ///
    bin(30) ///
    color(ltblue) ///
    lcolor(white) ///
    title("Distribution des classements") ///
    xtitle("Classement") ///
    ytitle("Fréquence")



* Figure 2 (Le graphique a été modifié manuellement)
preserve
	* On garde seulement les 8 thèmes principaux
	keep if inlist(themes, "mate mateIn1", "advantage middlegame", ///
	"kingsideAttack mate", "advantage fork", "crushing middlegame", ///
	"advantage long", "crushing fork", "advantage discoveredAttack")

	*save "data\tab1.dta", replace

	collapse (mean) rating popularity nbplays, by(themes)
	sort rating
	list

	graph bar rating nbplays, over(themes, sort(1)) blabel(bar)
restore

* Table 4
summarize rating nbplays if opening != ""

* Figure 4
twoway (scatter nbplays popularity if popularity >= 50, ///
        msymbol(circle_hollow) mcolor(ebblue) mlwidth(vthin)) ///
    (lfit nbplays popularity if popularity >= 50, ///
        lcolor(navy) lwidth(medthick)), ///
    title("Popularité vs. nombre de parties") ///
    xtitle("Popularité du puzzle") ///
    ytitle("Nombre de parties") ///
    legend(off) 

* Figure 6
scatter ratingdeviation nbplays if nbplays < 200

* Table 12
preserve
gen l_ratingdev = ln(ratingdeviation)
gen l_nbplays   = ln(nbplays)

reg l_ratingdev l_nbplays

gen l_nbplays2 = l_nbplays^2
reg l_ratingdev l_nbplays l_nbplays2, vce(robust)
reg l_ratingdev l_nbplays l_nbplays2 if nbplays < 1000, vce(robust)
restore

* Appendix (Podium)
preserve
	collapse (mean) popularity nbplays rating, by(themes)
	keep if nbplays >= 400
	sort popularity
	list in 1/8
restore





* Figure 5
preserve
* Graph pop
contract popularity difficulty, freq(nb_puzzles)
reshape wide nb_puzzles, i(popularity) j(difficulty) string

rename nb_puzzlesFacile Facile
rename nb_puzzlesMoyen Moyen
rename nb_puzzlesDifficile Difficile
foreach var in Facile Moyen Difficile {
    replace `var' = 0 if missing(`var')
}

* Graphique pour popularité 0 à 100
twoway (line Facile popularity, lcolor(blue) lwidth(medium)) ///
       (line Moyen popularity, lcolor(green) lwidth(medium)) ///
       (line Difficile popularity, lcolor(red) lwidth(medium)) ///
       if popularity > 60, ///
    title("Distribution de la popularité (positive) par niveau de difficulté") ///
    subtitle("Popularité de 0 à 100") ///
    xtitle("Popularité") ytitle("Nombre de puzzles") ///
    legend(title("Difficulté:") order(1 "Facile" 2 "Moyen" 3 "Difficile") pos(11)) ///
    xlabel(61(3)100) ///
    ylabel(, format(%9.0fc))
restore



* Table 7
bysort difficulty: summarize puzzle_coups

* Figure 3 (A été modifié manuellement)
graph box puzzle_coups, over(difficulty) title("Longueur de la solution par difficulté")





gen is_daily = 0
replace is_daily = 1 if nbplays >= 50000 & popularity < 96
* 1482 dailys

save "lichess_db_puzzle_sample2.dta", replace

* Partie 2 : Merge avec la BDD des parties.

use "lichess_db_puzzle_sample2.dta", clear
drop puzzleid premier_coup dernier_coup themes difficulty
gen couleur = 0
replace couleur = 1 if trait == "Noirs"
drop trait
collapse (mean) rating ratingdeviation popularity nbplays couleur demicoups nb_coups puzzle_coups (count) instances_puzzle = rating, by(opening)
save "lichess_db_puzzle_avg_sample2.dta", replace


import delimited "lichess_games_analysis_sample.csv", clear

collapse (mean) whiteelo blackelo (count) instances = whiteelo, by(opening)

gen WhiteElo_avg = round(whiteelo, 0.01)
gen BlackElo_avg = round(blackelo, 0.01)

gen AvgElo = round((WhiteElo_avg + BlackElo_avg) / 2, 0.01)

drop whiteelo blackelo
rename WhiteElo_avg WhiteElo
rename BlackElo_avg BlackElo

order opening WhiteElo BlackElo AvgElo instances

save "lichess_games_analysis_avg_sample.dta", replace
use "lichess_db_puzzle_avg_sample2.dta", clear
merge m:1 opening using "lichess_games_analysis_avg_sample.dta"

drop WhiteElo BlackElo

save "data\lichess_final_sample.dta", replace
use "data\lichess_final_sample.dta", clear

keep if _merge == 3
drop _merge


*Analyses

* Figure 7
twoway (scatter AvgElo rating, ///
        msymbol(circle_hollow) mcolor(ebblue) mlwidth(vthin)), ///
    xlabel(0(500)3000) ///
    ylabel(0(500)3000) ///
    xscale(range(0 3000)) ///
    yscale(range(0 3000)) ///
    xtitle("Classement moyen des puzzles") ///
    ytitle("Élo moyen des joueurs") ///
    title("Relation entre Rating et AvgElo") ///
    legend(off)

* Table 13
reg AvgElo rating

* Table 14
reg instances instances_puzzle

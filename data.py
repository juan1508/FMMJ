"""
data.py - Base de datos del simulador MMJ World Cup
"""

UEFA_TEAMS = [
    "Switzerland","Denmark","Poland","Austria","Croatia",
    "Sweden","Serbia","Wales","Scotland","Belgium",
    "Ukraine","Czech Republic","Iceland","Greece","Turkey",
    "Norway","Netherlands","France","Spain","Portugal",
    "Italy","England","Germany","Russia",
]
CONMEBOL_TEAMS = [
    "Brazil","Argentina","Colombia","Chile","Peru",
    "Uruguay","Venezuela","Bolivia","Paraguay","Ecuador",
]
CAF_TEAMS = [
    "South Africa","Morocco","Tunisia","Ghana","Senegal",
    "Egypt","Ivory Coast","Cameroon","Nigeria","Algeria",
]
CONCACAF_TEAMS = ["Mexico","Panama","Costa Rica","USA","Canada","Jamaica"]
AFC_TEAMS = ["Korea","Saudi Arabia","Japan","Australia","Iran","Qatar"]
PLAYOFF_TEAMS = ["New Zealand"]

ALL_TEAMS = UEFA_TEAMS + CONMEBOL_TEAMS + CAF_TEAMS + CONCACAF_TEAMS + AFC_TEAMS + PLAYOFF_TEAMS
COPA_AMERICA_GUESTS_POOL = CONCACAF_TEAMS + AFC_TEAMS + CAF_TEAMS + PLAYOFF_TEAMS

PLAYERS = {
    "Switzerland": [{"name":"Y. Kobel","position":"GK"},{"name":"G. Xhaka","position":"MF"},{"name":"M. Akanji","position":"DF"},{"name":"F. Schär","position":"DF"},{"name":"R. Freuler","position":"MF"},{"name":"B. Embolo","position":"FW"},{"name":"N. Okafor","position":"FW"},{"name":"X. Shaqiri","position":"MF"}],
    "Denmark": [{"name":"K. Schmeichel","position":"GK"},{"name":"C. Eriksen","position":"MF"},{"name":"R. Højlund","position":"FW"},{"name":"M. Hjulmand","position":"MF"},{"name":"A. Christensen","position":"DF"},{"name":"P. Højbjerg","position":"MF"},{"name":"M. Damsgaard","position":"MF"}],
    "Poland": [{"name":"W. Szczęsny","position":"GK"},{"name":"R. Lewandowski","position":"FW"},{"name":"P. Zieliński","position":"MF"},{"name":"J. Bednarek","position":"DF"},{"name":"P. Frankowski","position":"DF"},{"name":"S. Szymański","position":"MF"}],
    "Austria": [{"name":"P. Pentz","position":"GK"},{"name":"D. Alaba","position":"DF"},{"name":"K. Laimer","position":"MF"},{"name":"M. Sabitzer","position":"MF"},{"name":"M. Gregoritsch","position":"FW"},{"name":"A. Arnautovic","position":"FW"}],
    "Croatia": [{"name":"D. Livaković","position":"GK"},{"name":"L. Modrić","position":"MF"},{"name":"I. Perišić","position":"FW"},{"name":"J. Gvardiol","position":"DF"},{"name":"M. Kovačić","position":"MF"},{"name":"A. Kramarić","position":"FW"}],
    "Sweden": [{"name":"R. Olsen","position":"GK"},{"name":"A. Isak","position":"FW"},{"name":"D. Kulusevski","position":"FW"},{"name":"V. Gyökeres","position":"FW"},{"name":"E. Forsberg","position":"MF"},{"name":"V. Lindelöf","position":"DF"}],
    "Serbia": [{"name":"V. Milinković-Savić","position":"GK"},{"name":"S. Milinković-Savić","position":"MF"},{"name":"D. Vlahović","position":"FW"},{"name":"N. Gudelj","position":"MF"},{"name":"A. Mitrović","position":"FW"},{"name":"F. Kostić","position":"MF"}],
    "Wales": [{"name":"W. Hennessey","position":"GK"},{"name":"D. James","position":"FW"},{"name":"E. Ampadu","position":"MF"},{"name":"B. Davies","position":"DF"},{"name":"H. Wilson","position":"MF"}],
    "Scotland": [{"name":"A. Gunn","position":"GK"},{"name":"A. Robertson","position":"DF"},{"name":"S. McTominay","position":"MF"},{"name":"L. Ferguson","position":"MF"},{"name":"B. Doak","position":"FW"}],
    "Belgium": [{"name":"T. Courtois","position":"GK"},{"name":"K. De Bruyne","position":"MF"},{"name":"R. Lukaku","position":"FW"},{"name":"L. Openda","position":"FW"},{"name":"J. Trossard","position":"MF"},{"name":"A. Doku","position":"FW"}],
    "Ukraine": [{"name":"A. Lunin","position":"GK"},{"name":"O. Zinchenko","position":"DF"},{"name":"M. Mudryk","position":"FW"},{"name":"R. Malinovskyi","position":"MF"},{"name":"V. Tsygankov","position":"MF"}],
    "Czech Republic": [{"name":"J. Staněk","position":"GK"},{"name":"P. Schick","position":"FW"},{"name":"T. Souček","position":"MF"},{"name":"A. Hlozek","position":"FW"},{"name":"V. Coufal","position":"DF"}],
    "Iceland": [{"name":"R. Rúnarsson","position":"GK"},{"name":"Å. Guðmundsson","position":"MF"},{"name":"J. Guðmundsson","position":"MF"},{"name":"A. Sigurðsson","position":"MF"}],
    "Greece": [{"name":"O. Vlachodimos","position":"GK"},{"name":"V. Pavlidis","position":"FW"},{"name":"K. Mavropanos","position":"DF"},{"name":"G. Giakoumakis","position":"FW"}],
    "Turkey": [{"name":"U. Çakır","position":"GK"},{"name":"H. Çalhanoğlu","position":"MF"},{"name":"A. Güler","position":"MF"},{"name":"E. Ünal","position":"FW"},{"name":"M. Demiral","position":"DF"}],
    "Norway": [{"name":"Ø. Nyland","position":"GK"},{"name":"E. Haaland","position":"FW"},{"name":"M. Ødegaard","position":"MF"},{"name":"A. Sørloth","position":"FW"},{"name":"F. Aursnes","position":"MF"}],
    "Netherlands": [{"name":"B. Flekken","position":"GK"},{"name":"V. van Dijk","position":"DF"},{"name":"F. de Jong","position":"MF"},{"name":"X. Simons","position":"MF"},{"name":"D. Malen","position":"FW"},{"name":"T. Reijnders","position":"MF"}],
    "France": [{"name":"M. Maignan","position":"GK"},{"name":"K. Mbappé","position":"FW"},{"name":"A. Griezmann","position":"FW"},{"name":"A. Tchouaméni","position":"MF"},{"name":"M. Camavinga","position":"MF"},{"name":"W. Saliba","position":"DF"},{"name":"N. Kanté","position":"MF"}],
    "Spain": [{"name":"U. Simón","position":"GK"},{"name":"Pedri","position":"MF"},{"name":"Rodri","position":"MF"},{"name":"Yamal","position":"FW"},{"name":"Morata","position":"FW"},{"name":"D. Olmo","position":"MF"},{"name":"Gavi","position":"MF"}],
    "Portugal": [{"name":"R. Patrício","position":"GK"},{"name":"Cristiano Ronaldo","position":"FW"},{"name":"B. Fernandes","position":"MF"},{"name":"R. Leão","position":"FW"},{"name":"J. Félix","position":"FW"},{"name":"N. Mendes","position":"DF"}],
    "Italy": [{"name":"G. Donnarumma","position":"GK"},{"name":"F. Chiesa","position":"FW"},{"name":"N. Barella","position":"MF"},{"name":"C. Immobile","position":"FW"},{"name":"A. Bastoni","position":"DF"}],
    "England": [{"name":"J. Pickford","position":"GK"},{"name":"J. Bellingham","position":"MF"},{"name":"H. Kane","position":"FW"},{"name":"B. Saka","position":"FW"},{"name":"P. Foden","position":"MF"},{"name":"D. Rice","position":"MF"}],
    "Germany": [{"name":"M. ter Stegen","position":"GK"},{"name":"F. Wirtz","position":"MF"},{"name":"J. Kimmich","position":"MF"},{"name":"K. Havertz","position":"FW"},{"name":"J. Musiala","position":"MF"},{"name":"A. Rüdiger","position":"DF"}],
    "Russia": [{"name":"M. Safonov","position":"GK"},{"name":"A. Golovin","position":"MF"},{"name":"F. Smolov","position":"FW"}],
    "Brazil": [{"name":"Alisson","position":"GK"},{"name":"Vini Jr.","position":"FW"},{"name":"Rodrygo","position":"FW"},{"name":"Casemiro","position":"MF"},{"name":"T. Silva","position":"DF"},{"name":"G. Martinelli","position":"FW"},{"name":"Endrick","position":"FW"}],
    "Argentina": [{"name":"E. Martínez","position":"GK"},{"name":"L. Messi","position":"FW"},{"name":"J. Dybala","position":"FW"},{"name":"L. Martínez","position":"FW"},{"name":"C. Romero","position":"DF"},{"name":"Á. Di María","position":"FW"},{"name":"E. Fernández","position":"MF"}],
    "Colombia": [{"name":"D. Vargas","position":"GK"},{"name":"L. Díaz","position":"FW"},{"name":"D. Muñoz","position":"DF"},{"name":"J. Quintero","position":"MF"},{"name":"L. Muriel","position":"FW"},{"name":"R. Borré","position":"FW"}],
    "Chile": [{"name":"C. Bravo","position":"GK"},{"name":"A. Sánchez","position":"FW"},{"name":"G. Maripán","position":"DF"},{"name":"A. Vidal","position":"MF"}],
    "Peru": [{"name":"P. Gallese","position":"GK"},{"name":"G. Lapadula","position":"FW"},{"name":"C. Cueva","position":"MF"},{"name":"A. Carrillo","position":"FW"}],
    "Uruguay": [{"name":"S. Rochet","position":"GK"},{"name":"L. Suárez","position":"FW"},{"name":"D. Núñez","position":"FW"},{"name":"F. Valverde","position":"MF"},{"name":"J. Giménez","position":"DF"}],
    "Venezuela": [{"name":"W. Faríñez","position":"GK"},{"name":"Y. Rincón","position":"MF"},{"name":"S. Córdova","position":"FW"}],
    "Bolivia": [{"name":"C. Lampe","position":"GK"},{"name":"H. Vaca","position":"MF"},{"name":"D. Mancilla","position":"FW"}],
    "Paraguay": [{"name":"A. Silva","position":"GK"},{"name":"M. Almirón","position":"MF"},{"name":"J. Enciso","position":"MF"},{"name":"A. Sanabria","position":"FW"}],
    "Ecuador": [{"name":"H. Galíndez","position":"GK"},{"name":"M. Caicedo","position":"MF"},{"name":"A. Hincapié","position":"DF"},{"name":"G. Plata","position":"FW"}],
    "South Africa": [{"name":"R. Williams","position":"GK"},{"name":"T. Zwane","position":"MF"},{"name":"P. Lakay","position":"FW"}],
    "Morocco": [{"name":"Y. Bono","position":"GK"},{"name":"A. Hakimi","position":"DF"},{"name":"H. Ziyech","position":"MF"},{"name":"Y. En-Nesyri","position":"FW"},{"name":"S. Amrabat","position":"MF"}],
    "Tunisia": [{"name":"A. Dahmen","position":"GK"},{"name":"E. Khazri","position":"MF"},{"name":"Y. Msakni","position":"FW"}],
    "Ghana": [{"name":"L. Zigi","position":"GK"},{"name":"T. Partey","position":"MF"},{"name":"M. Kudus","position":"MF"},{"name":"J. Ayew","position":"FW"}],
    "Senegal": [{"name":"E. Mendy","position":"GK"},{"name":"S. Mané","position":"FW"},{"name":"K. Koulibaly","position":"DF"},{"name":"N. Jackson","position":"FW"},{"name":"P. Sarr","position":"FW"}],
    "Egypt": [{"name":"M. El-Shenawy","position":"GK"},{"name":"M. Salah","position":"FW"},{"name":"O. Marmoush","position":"FW"},{"name":"A. Hassan","position":"MF"}],
    "Ivory Coast": [{"name":"Y. Fofana","position":"GK"},{"name":"S. Haller","position":"FW"},{"name":"F. Kessié","position":"MF"},{"name":"W. Zaha","position":"FW"}],
    "Cameroon": [{"name":"A. Onana","position":"GK"},{"name":"V. Aboubakar","position":"FW"},{"name":"Zambo Anguissa","position":"MF"},{"name":"B. Mbeumo","position":"FW"}],
    "Nigeria": [{"name":"F. Uzoho","position":"GK"},{"name":"V. Osimhen","position":"FW"},{"name":"A. Lookman","position":"FW"},{"name":"A. Iwobi","position":"MF"}],
    "Algeria": [{"name":"R. Mbolhi","position":"GK"},{"name":"R. Mahrez","position":"FW"},{"name":"I. Bennacer","position":"MF"},{"name":"S. Benrahma","position":"FW"}],
    "Mexico": [{"name":"G. Ochoa","position":"GK"},{"name":"H. Lozano","position":"FW"},{"name":"S. Giménez","position":"FW"},{"name":"E. Álvarez","position":"MF"}],
    "Panama": [{"name":"L. Mejía","position":"GK"},{"name":"A. Murillo","position":"DF"},{"name":"A. Carrasquilla","position":"MF"},{"name":"C. Waterman","position":"FW"}],
    "Costa Rica": [{"name":"K. Navas","position":"GK"},{"name":"B. Ruiz","position":"FW"},{"name":"J. Vargas","position":"MF"}],
    "USA": [{"name":"M. Turner","position":"GK"},{"name":"C. Pulisic","position":"MF"},{"name":"G. Reyna","position":"MF"},{"name":"T. Adams","position":"MF"},{"name":"F. Balogun","position":"FW"}],
    "Canada": [{"name":"M. Crépeau","position":"GK"},{"name":"A. Davies","position":"DF"},{"name":"J. David","position":"FW"},{"name":"T. Buchanan","position":"MF"},{"name":"S. Eustáquio","position":"MF"}],
    "Jamaica": [{"name":"A. Blake","position":"GK"},{"name":"L. Bailey","position":"FW"},{"name":"K. Roofe","position":"FW"},{"name":"S. Nicholson","position":"FW"}],
    "Korea": [{"name":"Kim Seung-gyu","position":"GK"},{"name":"H. Son","position":"FW"},{"name":"Kim Min-jae","position":"DF"},{"name":"Lee Kang-in","position":"MF"},{"name":"Hwang Hee-chan","position":"FW"}],
    "Saudi Arabia": [{"name":"M. Al-Owais","position":"GK"},{"name":"S. Al-Dawsari","position":"FW"},{"name":"A. Al-Faraj","position":"MF"},{"name":"A. Al-Buraikan","position":"FW"}],
    "Japan": [{"name":"S. Gonda","position":"GK"},{"name":"T. Kubo","position":"MF"},{"name":"H. Ito","position":"FW"},{"name":"D. Kamada","position":"MF"},{"name":"T. Minamino","position":"MF"}],
    "Australia": [{"name":"M. Ryan","position":"GK"},{"name":"M. Leckie","position":"FW"},{"name":"A. Mooy","position":"MF"},{"name":"M. Duke","position":"FW"},{"name":"J. Irvine","position":"MF"}],
    "Iran": [{"name":"A. Beiranvand","position":"GK"},{"name":"S. Azmoun","position":"FW"},{"name":"M. Taremi","position":"FW"},{"name":"A. Jahanbakhsh","position":"FW"}],
    "Qatar": [{"name":"S. Al-Sheeb","position":"GK"},{"name":"A. Afif","position":"FW"},{"name":"H. Al-Haydos","position":"FW"},{"name":"M. Abu Fani","position":"MF"}],
    "New Zealand": [{"name":"M. Pickford","position":"GK"},{"name":"C. Wood","position":"FW"},{"name":"K. Barbarouses","position":"FW"},{"name":"M. Boxall","position":"DF"},{"name":"L. Cacace","position":"DF"}],
}

INITIAL_FIFA_RANKING = {
    "France":1840,"Spain":1810,"England":1780,"Germany":1750,
    "Portugal":1720,"Italy":1690,"Netherlands":1650,"Belgium":1620,
    "Croatia":1580,"Denmark":1560,"Switzerland":1530,"Norway":1480,
    "Austria":1450,"Sweden":1420,"Poland":1390,"Serbia":1360,
    "Turkey":1330,"Ukraine":1310,"Czech Republic":1280,"Greece":1250,
    "Scotland":1220,"Wales":1200,"Iceland":1150,"Russia":1100,
    "Argentina":1870,"Brazil":1830,"Colombia":1650,"Uruguay":1620,
    "Chile":1540,"Ecuador":1510,"Paraguay":1430,"Peru":1380,
    "Bolivia":1250,"Venezuela":1230,
    "Senegal":1630,"Morocco":1600,"Tunisia":1530,"Ghana":1480,
    "Egypt":1450,"Ivory Coast":1440,"Nigeria":1420,"Cameroon":1390,
    "South Africa":1330,"Algeria":1350,
    "Mexico":1550,"USA":1530,"Canada":1490,"Costa Rica":1380,
    "Panama":1360,"Jamaica":1280,
    "Japan":1560,"Korea":1530,"Australia":1470,"Saudi Arabia":1420,
    "Iran":1440,"Qatar":1370,
    "New Zealand":1100,
}

FLAG_MAP = {
    "France":"🇫🇷","Spain":"🇪🇸","England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","Germany":"🇩🇪",
    "Portugal":"🇵🇹","Italy":"🇮🇹","Netherlands":"🇳🇱","Belgium":"🇧🇪",
    "Croatia":"🇭🇷","Denmark":"🇩🇰","Switzerland":"🇨🇭","Norway":"🇳🇴",
    "Austria":"🇦🇹","Sweden":"🇸🇪","Poland":"🇵🇱","Serbia":"🇷🇸",
    "Turkey":"🇹🇷","Ukraine":"🇺🇦","Czech Republic":"🇨🇿","Greece":"🇬🇷",
    "Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","Wales":"🏴󠁧󠁢󠁷󠁬󠁳󠁿","Iceland":"🇮🇸","Russia":"🇷🇺",
    "Argentina":"🇦🇷","Brazil":"🇧🇷","Colombia":"🇨🇴","Uruguay":"🇺🇾",
    "Chile":"🇨🇱","Ecuador":"🇪🇨","Paraguay":"🇵🇾","Peru":"🇵🇪",
    "Bolivia":"🇧🇴","Venezuela":"🇻🇪",
    "Senegal":"🇸🇳","Morocco":"🇲🇦","Tunisia":"🇹🇳","Ghana":"🇬🇭",
    "Egypt":"🇪🇬","Ivory Coast":"🇨🇮","Nigeria":"🇳🇬","Cameroon":"🇨🇲",
    "South Africa":"🇿🇦","Algeria":"🇩🇿",
    "Mexico":"🇲🇽","USA":"🇺🇸","Canada":"🇨🇦","Costa Rica":"🇨🇷",
    "Panama":"🇵🇦","Jamaica":"🇯🇲",
    "Japan":"🇯🇵","Korea":"🇰🇷","Australia":"🇦🇺","Saudi Arabia":"🇸🇦",
    "Iran":"🇮🇷","Qatar":"🇶🇦",
    "New Zealand":"🇳🇿",
}

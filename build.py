import json, uuid, sys
sys.path.insert(0,'.')
from content import T, P
T[12][1][3]="✍🏾 Essayons maintenant ensemble : je vais calculer ton cycle pour toi 👇"
U=lambda: str(uuid.uuid4())
OLD=json.load(open('v3_full.json'))
OLDF={f['name']:f['uuid'] for f in OLD['flows']}
OLDG={g['name']:g['uuid'] for g in OLD['groups']}
DANGER="frappe frappée frapper battue battre bat tape tapée viol violée violence violences violent abus abusée agression agressée attouchement attouchements inceste harcèlement harcelée harcèle menace menacée chantage forcée forcé forcer obligée touchée enceinte grossesse mourir tuer suicide danger peur secours urgence saigne saignement hémorragie évanouie"

class Flow:
    def __init__(s,name,uid=None):
        s.uuid=uid or OLDF.get(name) or U(); s.name=name; s.nodes=[]; s.ui={}
    def ref(s): return {"uuid":s.uuid,"name":s.name}
    def _pos(s,n,typ,extra=None):
        i=len(s.ui); d={"position":{"left":(i%6)*320,"top":(i//6)*420},"type":typ}
        if extra: d.update(extra)
        s.ui[n["uuid"]]=d
    def send(s,texts,actions_extra=None):
        n={"uuid":U(),"actions":[{"uuid":U(),"type":"send_msg","text":t,"quick_replies":[],"attachments":[]} for t in texts],"exits":[{"uuid":U(),"destination_uuid":None}]}
        if actions_extra: n["actions"]+=actions_extra
        s.nodes.append(n); s._pos(n,"execute_actions"); return n
    def wait(s,result,cases):
        # cases: list of (type,args,catname)
        cats={}; order=[]
        for _,_,c in cases:
            if c not in cats:
                cats[c]={"uuid":U(),"name":c,"exit_uuid":U()}; order.append(c)
        other={"uuid":U(),"name":"Other","exit_uuid":U()}
        router={"type":"switch","operand":"@input.text","default_category_uuid":other["uuid"],
                "cases":[{"uuid":U(),"type":t,"arguments":a,"category_uuid":cats[c]["uuid"]} for t,a,c in cases],
                "categories":[cats[c] for c in order]+[other],"wait":{"type":"msg"},"result_name":result}
        n={"uuid":U(),"actions":[],"router":router,"exits":[{"uuid":c["exit_uuid"],"destination_uuid":None} for c in router["categories"]]}
        n["_cat"]={c:cats[c]["exit_uuid"] for c in order}; n["_cat"]["Other"]=other["exit_uuid"]
        s.nodes.append(n); s._pos(n,"wait_for_response",{"config":{"cases":{}}}); return n
    def enter(s,flowref):
        c1={"uuid":U(),"name":"Complete","exit_uuid":U()}; c2={"uuid":U(),"name":"Expired","exit_uuid":U()}
        n={"uuid":U(),"actions":[{"uuid":U(),"type":"enter_flow","flow":flowref}],
           "router":{"type":"switch","operand":"@child.run.status","default_category_uuid":c1["uuid"],
             "cases":[{"uuid":U(),"type":"has_only_text","arguments":["completed"],"category_uuid":c1["uuid"]},
                      {"uuid":U(),"type":"has_only_text","arguments":["expired"],"category_uuid":c2["uuid"]}],
             "categories":[c1,c2]},
           "exits":[{"uuid":c1["exit_uuid"],"destination_uuid":None},{"uuid":c2["exit_uuid"],"destination_uuid":None}]}
        n["_cat"]={"Complete":c1["exit_uuid"],"Expired":c2["exit_uuid"]}
        s.nodes.append(n); s._pos(n,"split_by_subflow",{"config":{}}); return n
    def split(s,operand,cases):
        cats={}; order=[]
        for _,_,c in cases:
            if c not in cats: cats[c]={"uuid":U(),"name":c,"exit_uuid":U()}; order.append(c)
        other={"uuid":U(),"name":"Other","exit_uuid":U()}
        router={"type":"switch","operand":operand,"default_category_uuid":other["uuid"],
                "cases":[{"uuid":U(),"type":t,"arguments":a,"category_uuid":cats[c]["uuid"]} for t,a,c in cases],
                "categories":[cats[c] for c in order]+[other]}
        n={"uuid":U(),"actions":[],"router":router,"exits":[{"uuid":c["exit_uuid"],"destination_uuid":None} for c in router["categories"]]}
        n["_cat"]={c:cats[c]["exit_uuid"] for c in order}; n["_cat"]["Other"]=other["exit_uuid"]
        s.nodes.append(n); s._pos(n,"split_by_expression",{"config":{}}); return n
    @staticmethod
    def link(n,dest,cat=None):
        if cat is None: n["exits"][0]["destination_uuid"]=dest["uuid"]
        else:
            eu=n["_cat"][cat]
            for e in n["exits"]:
                if e["uuid"]==eu: e["destination_uuid"]=dest["uuid"]
    def export(s):
        nodes=[]
        for n in s.nodes:
            m=dict(n); m.pop("_cat",None); nodes.append(m)
        return {"uuid":s.uuid,"name":s.name,"spec_version":"13.1.0","language":"fra","type":"messaging","revision":1,
                "expire_after_minutes":10080,"localization":{},"nodes":nodes,"_ui":{"nodes":s.ui}}


FIELDS=[{"key":"derniere_regle","name":"Dernière règle","type":"datetime"},
        {"key":"duree_cycle","name":"Durée cycle","type":"number"},
        {"key":"prochaines_regles","name":"Prochaines règles","type":"datetime"}]
def setf(key,name,val): return {"uuid":U(),"type":"set_contact_field","field":{"key":key,"name":name},"value":val}
cyc=Flow("Mes règles")
a1=cyc.send(["📅 Quel était le PREMIER jour de tes dernières règles ?\nÉcris la date comme ceci : 15/10/2026"])
w1=cyc.wait("derniere",[("has_date_lt",["@(datetime_add(today(), -120, \"D\"))"],"Trop ancienne"),("has_date_lt",["@(datetime_add(today(), 1, \"D\"))"],"Date")])
cyc.link(a1,w1)
r1=cyc.send(["Je n'ai pas compris la date 😊 Écris-la comme ceci : 15/10/2026 (jour/mois/année)."]); cyc.link(w1,r1,"Other"); cyc.link(r1,w1)
old1=cyc.send(["🤔 Cette date est très ancienne. Vérifie l'année (par exemple 2026 et pas 2016) et réécris la date de tes DERNIÈRES règles : 15/10/2026"]); cyc.link(w1,old1,"Trop ancienne"); cyc.link(old1,w1)
a2=cyc.send(["Merci ! Et le premier jour des règles D'AVANT (le mois précédent) ?\nÉcris la date, ou 0 si tu ne sais pas."]); cyc.link(w1,a2,"Date")
w2=cyc.wait("avant",[("has_number_eq",["0"],"Je ne sais pas"),("has_date_lt",["@results.derniere.value"],"Date")])
cyc.link(a2,w2)
r2=cyc.send(["Écris une date AVANT tes dernières règles (ex. 17/09/2026), ou 0 si tu ne sais pas 😊"]); cyc.link(w2,r2,"Other"); cyc.link(r2,w2)
sp=cyc.split("@(datetime_diff(results.avant.value, results.derniere.value, \"D\"))",[("has_number_between",["15","60"],"Plausible")])
cyc.link(w2,sp,"Date")
ok=cyc.send(["🌙 Ton dernier cycle a duré @(datetime_diff(results.avant.value, results.derniere.value, \"D\")) jours.\n📅 Tes prochaines règles devraient arriver vers le @(format_date(datetime_add(results.derniere.value, datetime_diff(results.avant.value, results.derniere.value, \"D\"), \"D\"))).\n\n🎒 Pense à mettre ton kit dans ton sac quelques jours avant !\nC'est une estimation : chez les jeunes filles, le cycle change souvent. Note chaque mois tes dates avec Ma Lune pour un calcul plus précis."],
  [setf("derniere_regle","Dernière règle","@results.derniere.value"),
   setf("duree_cycle","Durée cycle","@(datetime_diff(results.avant.value, results.derniere.value, \"D\"))"),
   setf("prochaines_regles","Prochaines règles","@(datetime_add(results.derniere.value, datetime_diff(results.avant.value, results.derniere.value, \"D\"), \"D\"))")])
cyc.link(sp,ok,"Plausible")
odd=cyc.send(["Hmm, il y a @(datetime_diff(results.avant.value, results.derniere.value, \"D\")) jours entre tes deux dates. C'est inhabituel : vérifie tes dates. Si c'est bien ça plusieurs mois de suite, parles-en à un agent de santé 🩺\nEn attendant, je calcule avec un cycle moyen de 28 jours 👇"])
cyc.link(sp,odd,"Other")
dflt=cyc.send(["📅 Avec un cycle moyen de 28 jours, tes prochaines règles devraient arriver vers le @(format_date(datetime_add(results.derniere.value, 28, \"D\"))).\n\n🎒 Pense à mettre ton kit dans ton sac quelques jours avant !\nLe mois prochain, note encore le premier jour de tes règles ici : je pourrai calculer TON vrai cycle."],
  [setf("derniere_regle","Dernière règle","@results.derniere.value"),
   setf("prochaines_regles","Prochaines règles","@(datetime_add(results.derniere.value, 28, \"D\"))")])
cyc.link(w2,dflt,"Je ne sais pas"); cyc.link(odd,dflt)

urg=Flow("Urgence"); grp={"uuid":OLDG["Urgence"],"name":"Urgence"}
urg.send(["@contact.name, merci de m'avoir écrit. Ce que tu vis est important et ce n'est pas ta faute. 💛\nSi tu es en danger maintenant, va tout de suite à l'hôpital ou au centre de santé le plus proche, ou chez un adulte de confiance.\nUne personne de l'équipe Ma Lune va te répondre ici, en privé, le plus vite possible."],
         [{"uuid":U(),"type":"add_contact_groups","groups":[grp]}])

def danger_case(): return ("has_any_word",[DANGER],"Urgence")

def topic_menu_flow(name, intro, groups):
    """groups: list of (label, [keys]) ; if single group with label None -> flat list"""
    f=Flow(name)
    fb=None
    flat = len(groups)==1 and groups[0][0] is None
    if flat:
        keys=groups[0][1]
        lines=[intro]+[f"{i+1}️⃣ {(T[k][0] if k in T else k)}" for i,k in enumerate(keys)]+["","Écris le numéro."]
        menu=f.send(["\n".join(lines)])
        w=f.wait("sujet",[("has_number_eq",[str(i+1)],T[k][0][:36] if k!='9d' else "Mon corps (doux)") for i,k in enumerate(keys)]+[danger_case()])
        f.link(menu,w)
        retry=f.send(["Écris un numéro de 1 à %d 😊"%len(keys)]); f.link(w,retry,"Other"); f.link(retry,w)
        targets=[(w, keys, lambda i,k: (T[k][0][:36] if k!='9d' else "Mon corps (doux)"))]
        start=menu
    else:
        lines=[intro]+[f"{i+1}️⃣ {g[0]}" for i,g in enumerate(groups)]
        menu=f.send(["\n".join(lines)])
        w=f.wait("theme",[("has_number_eq",[str(i+1)],g[0]) for i,g in enumerate(groups)]+[danger_case()])
        f.link(menu,w)
        retry=f.send(["Écris un numéro de 1 à %d 😊"%len(groups)]); f.link(w,retry,"Other"); f.link(retry,w)
        start=menu; targets=[]; subs=[]
        for g,keys in groups:
            sl=[f"{g} 🌙"]+[f"{i+1}️⃣ {T[k][0]}" for i,k in enumerate(keys)]+["0️⃣ Retour"]
            sm=f.send(["\n".join(sl)]); f.link(w,sm,g); subs.append((g,sm))
            sw=f.wait("sujet",[("has_number_eq",[str(i+1)],f"T{k} {T[k][0]}"[:36]) for i,k in enumerate(keys)]+[("has_number_eq",["0"],"Retour"),danger_case()])
            f.link(sm,sw); f.link(sw,menu,"Retour")
            r=f.send(["Écris un numéro de 0 à %d 😊"%len(keys)]); f.link(sw,r,"Other"); f.link(r,sw)
            targets.append((sw,keys,lambda i,k: f"T{k} {T[k][0]}"[:36]))
            urgn=f.enter(urg.ref()); f.link(sw,urgn,"Urgence")
    # feedback
    q=f.send(["Ce thème t'a aidée ?\n1️⃣ 👍 Oui\n2️⃣ 👎 Non"])
    fw=f.wait("avis",[("has_number_eq",["1"],"Oui"),("has_number_eq",["2"],"Non")])
    f.link(q,fw)
    if flat:
        thanks=f.send(["Merci pour ton avis ! 💛 Choisis un autre thème ci-dessous, ou écris MENU pour le menu principal."])
        for c in ["Oui","Non","Other"]: f.link(fw,thanks,c)
        f.link(thanks,start)
    else:
        thanks=f.send(["Merci pour ton avis ! 💛 Choisis un autre sujet ci-dessous (0 pour les autres thèmes), ou écris MENU pour le menu principal."])
        for c in ["Oui","Non","Other"]: f.link(fw,thanks,c)
        sp=f.split("@results.theme",[("has_number_eq",[str(i+1)],g) for i,(g,_) in enumerate(subs)])
        f.link(thanks,sp)
        for g,sm in subs: f.link(sp,sm,g)
        f.link(sp,start,"Other")
    for wnode,keys,catname in targets:
        for i,k in enumerate(keys):
            tn=f.send(T[k][1]); f.link(wnode,tn,catname(i,k))
            if k==12:
                ce=f.enter(cyc.ref()); f.link(tn,ce); f.link(ce,q,'Complete'); f.link(ce,q,'Expired')
            else: f.link(tn,q)
    urgn=f.enter(urg.ref()); f.link(w,urgn,"Urgence")
    return f

app=topic_menu_flow("Apprendre","Que veux-tu découvrir ? 🌙",[
 ("Mes règles",[1,2,12,15]),
 ("Mon corps qui grandit",[13,14,16,19,10]),
 ("Prendre soin de moi",[4,5,7,17]),
 ("Mes émotions et ma sécurité",[6,9,18]),
 ("Pratique et santé",[3,11,8])])
jeu=topic_menu_flow("Apprendre Jeunes","Choisis un thème 🌸",[(None,[1,13,12,3,4,"9d",10])])

# Parents
par=Flow("Espace Parents")
names=[P[i][0] for i in range(1,8)]+["Voir les thèmes des filles"]
pm=par.send(["Espace parents 💛\n"+"\n".join(f"{i+1}️⃣ {n}" for i,n in enumerate(names))+"\n\nÉcrivez le numéro."])
pw=par.wait("lecon",[("has_number_eq",[str(i+1)],("P%d "%(i+1)+n)[:36]) for i,n in enumerate(names)]+[danger_case()])
par.link(pm,pw)
pr=par.send(["Écrivez un numéro de 1 à 8 😊"]); par.link(pw,pr,"Other"); par.link(pr,pw)
pend=par.send(["Merci 💛 Choisissez une autre leçon, ou écrivez MENU."]); par.link(pend,pm)
for i in range(1,8):
    n=par.send(P[i][1]); par.link(pw,n,("P%d "%i+P[i][0])[:36]); par.link(n,pend)
ef=par.enter(app.ref()); par.link(pw,ef,("P8 Voir les thèmes des filles")[:36])
pu=par.enter(urg.ref()); par.link(pw,pu,"Urgence")

# Quiz
qz=Flow("Quiz")
Q=[("Les règles, c'est du sang sale.","2","Bravo ! Le sang des règles n'est pas sale, c'est un sang normal du corps.","Pas tout à fait 😊 Le sang des règles n'est pas sale, c'est un sang normal du corps."),
("On peut se laver et prendre une douche pendant les règles.","1","Bravo ! Se laver est important pendant les règles.","Pas tout à fait 😊 Se laver pendant les règles est sûr et important."),
("Au début, c'est normal que les règles soient irrégulières.","1","Bravo ! Les 2 à 3 premières années, c'est souvent irrégulier.","Pas tout à fait 😊 Au début, c'est souvent irrégulier, et c'est normal."),
("Pendant les règles, on ne doit pas faire de sport ni aller à l'école.","2","Bravo ! Tu peux aller à l'école et faire du sport.","Pas tout à fait 😊 Les règles ne sont pas une maladie : école et sport sont possibles."),
("Avoir ses règles veut dire qu'une fille est prête pour le mariage.","2","Bravo ! Avoir ses règles veut dire que le corps grandit, pas qu'on est prête.","Pas tout à fait 😊 Avoir ses règles ne veut pas dire être prête pour le mariage.")]
intro=qz.send(["🎯 Petit quiz Ma Lune ! 5 questions, réponds 1 pour VRAI ou 2 pour FAUX. Ce n'est pas une note, c'est pour t'aider à apprendre. 😊"])
QN=[]
for i,(qq,ans,ok,ko) in enumerate(Q,1):
    qn=qz.send([f"Question {i}/5 : {qq}\n1️⃣ Vrai\n2️⃣ Faux"])
    qw=qz.wait(f"q{i}",[("has_number_eq",[ans],"Juste"),("has_number_eq",["2" if ans=="1" else "1"],"Faux")]); qz.link(qn,qw)
    r=qz.send(["Réponds 1 ou 2 😊"]); qz.link(qw,r,"Other"); qz.link(r,qw)
    okn=qz.send([ok]); kon=qz.send([ko]); qz.link(qw,okn,"Juste"); qz.link(qw,kon,"Faux")
    QN.append((qn,okn,kon))
end=qz.send(["Merci @contact.name ! 🌸 Tu as fini le quiz. Plus tu découvres les thèmes, plus tu en sauras. Écris MENU pour continuer."])
qz.link(intro,QN[0][0])
for i in range(5):
    dest=QN[i+1][0] if i<4 else end
    qz.link(QN[i][1],dest); qz.link(QN[i][2],dest)

flows=[cyc,urg,app,jeu,par,qz]
out={"version":"13","site":"https://textit.com","flows":[f.export() for f in flows],"campaigns":[],"triggers":[],
  "fields":FIELDS,"groups":[{"uuid":grp["uuid"],"name":"Urgence","query":None}]}
json.dump(out,open("ma-lune-textit-import.json","w"),ensure_ascii=False,indent=1)
# sanity checks
for f in out["flows"]:
    ids={n["uuid"] for n in f["nodes"]}
    dangling=[e for n in f["nodes"] for e in n["exits"] if e["destination_uuid"] and e["destination_uuid"] not in ids]
    unlinked=sum(1 for n in f["nodes"] for e in n["exits"] if not e["destination_uuid"])
    print(f["name"],len(f["nodes"]),"nodes; dangling",len(dangling),"; open exits",unlinked)

import csv
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier,export_text
from sklearn.model_selection import StratifiedKFold,cross_val_predict
p=Path('data/werewolf-diagnostics')
with (p/'classifier_features.csv').open(newline='') as f: rows=list(csv.reader(f))
names=rows[0][2:]; ids=[r[0] for r in rows[1:]]
x=np.array([r[2:] for r in rows[1:]],dtype=float); y=np.array([int(r[1]) for r in rows[1:]])
m=DecisionTreeClassifier(max_depth=4,class_weight='balanced',random_state=7)
m.fit(x,y)
pred=m.predict(x)
print('training positives:',[(pid,int(label)) for pid,label,flag in zip(ids,y,pred) if flag])
rule=export_text(m,feature_names=names)
print(rule)
(p/'fitted_tree_rule.txt').write_text(rule,encoding='utf-8')
with (p/'fitted_tree_candidate.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['Monster Type','P_ID']);w.writerows(('Werewolf',pid) for pid,flag in zip(ids,pred) if flag)
for seed in [7,29,103]:
 probs=cross_val_predict(m,x,y,cv=StratifiedKFold(6,shuffle=True,random_state=seed),method='predict_proba')[:,1]
 z=probs>=.5
 print('validation',seed,'TP',sum(z & (y==1)),'FP',sum(z & (y==0)))

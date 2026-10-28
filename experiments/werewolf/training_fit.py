import csv
import numpy as np
from sklearn.tree import DecisionTreeClassifier,export_text
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold,cross_val_predict
with open('data/werewolf-diagnostics/classifier_features.csv',newline='') as f:
 rows=list(csv.reader(f))
names=rows[0][2:];x=np.array([r[2:] for r in rows[1:]],dtype=float);y=np.array([int(r[1]) for r in rows[1:]])
for depth in [1,2,3,4]:
 m=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=1,class_weight='balanced',random_state=7).fit(x,y)
 p=m.predict(x)
 print('training tree',depth,'TP',sum((p==1)&(y==1)),'FP',sum((p==1)&(y==0)))
 if depth==2: print(export_text(m,feature_names=names))
print('features',len(names))

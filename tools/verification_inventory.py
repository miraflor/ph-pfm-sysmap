"""Produce full evidence review queue for all nodes and flows (not factual certification)."""
import csv
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pfmmap.model import Model
ROOT=Path(__file__).resolve().parent.parent

def build():
 m=Model(ROOT)
 with (ROOT/'audit/claim_reviews.csv').open(encoding='utf-8',newline='') as file:
  reviewed={(r['entity_type'],r['entity_id']):r for r in csv.DictReader(file)}
 rows=[]
 for typ,tablename,kid,stagecol,describe in [
  ('node','nodes','node_id','status','description'),('flow','flows','flow_id','stage','what_passes')]:
  for x in m.t[tablename]:
   ev=m.evidence(x['basis']); stage=x[stagecol] or 'not_coded'; rv=reviewed.get((typ,x[kid]));srcs=[m.ix['sources'][c] for c in ev['codes']]
   priority='high' if stage in ('in_use','in_use_part') else ('medium' if stage in ('planned','described_not_verified','not_stated') else 'low')
   if rv:priority='reviewed'
   rows.append(dict(type=typ,id=x[kid],description=x[describe][:240],claimed_status=stage,best_source_type=ev['best'],has_web_reference='yes' if any(s['url'] for s in srcs) else 'no',review_result=(rv or {}).get('result','not_individually_reviewed'),review_priority=priority,source_codes=';'.join(ev['codes']),basis=x['basis']))
 p=ROOT/'audit/verification_inventory.csv'
 p.parent.mkdir(exist_ok=True)
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 print(f'Inventory: {len(rows)} claims ({len(reviewed)} dated individual reviews), output {p}')
 return rows

if __name__=='__main__':build()

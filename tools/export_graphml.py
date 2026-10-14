"""Export a source-linked directed graph from the canonical registers.

python tools/export_graphml.py [output.graphml]

The graph retains only registered flows. 'via_id' makes two linked edges with
one shared flow ID, not two independent verified integrations.
"""
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pfmmap.model import Model

ROOT=Path(__file__).resolve().parent.parent
NS='http://graphml.graphdrawing.org/xmlns'
ET.register_namespace('',NS)
q=lambda tag:f'{{{NS}}}{tag}'

def make(path):
    m=Model(ROOT)
    root=ET.Element(q('graphml'))
    keys=[('n_name','node','name'),('n_type','node','type'),('n_status','node','status'),
          ('n_basis','node','basis'),('n_level','node','level'),('e_id','edge','flow_id'),
          ('e_stage','edge','stage'),('e_medium','edge','medium'),('e_kind','edge','kind'),
          ('e_basis','edge','basis'),('e_what','edge','what_passes'),('e_part','edge','via_part')]
    for kid,typ,field in keys:
        ET.SubElement(root,q('key'),id=kid,**{'for':typ,'attr.name':field,'attr.type':'string'})
    g=ET.SubElement(root,q('graph'),id='pfm_registered_flows',edgedefault='directed')
    def data(parent,key,value):
        ET.SubElement(parent,q('data'),key=key).text=value or ''
    for n in m.t['nodes']:
        out=ET.SubElement(g,q('node'),id=n['node_id'])
        for key,col in [('n_name','name'),('n_type','type'),('n_status','status'),('n_basis','basis'),('n_level','level')]:
            data(out,key,n[col])
    c=0
    for f in m.t['flows']:
        pairs=[(f['from_id'],f['to_id'],'direct')]
        if f['via_id']:
            pairs=[(f['from_id'],f['via_id'],'to-via'),(f['via_id'],f['to_id'],'from-via')]
        for a,b,part in pairs:
            c+=1
            e=ET.SubElement(g,q('edge'),id=f['flow_id']+('-'+part if part!='direct' else ''),source=a,target=b)
            for key,val in [('e_id',f['flow_id']),('e_stage',f['stage']),('e_medium',f['medium']),
                            ('e_kind',f['kind']),('e_basis',f['basis']),('e_what',f['what_passes']),('e_part',part)]:data(e,key,val)
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
    print(f'GraphML: {len(m.t["nodes"])} canonical nodes, {len(m.t["flows"])} registered flows, {c} directed edge segments -> {path}')

if __name__=='__main__':
    make(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'exports'/'pfm_flows.graphml')

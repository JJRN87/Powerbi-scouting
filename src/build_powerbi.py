"""Build a native PBIP/PBIR report and semantic model from the validated exports.

Opening and refreshing in Desktop is required; generation is not engine validation.
"""
import csv
import json
import re
import sqlite3
import hashlib
import shutil
import copy
from pathlib import Path
from .download import ROOT

OUT = ROOT / 'powerbi/Powerbi-scouting'
MODEL = OUT / 'Scouting.SemanticModel'
REPORT = OUT / 'Scouting.Report'
SCHEMA = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'


def uid(label):
    return hashlib.sha256(label.encode()).hexdigest()[:20]


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def lit(value):
    v = ('true' if value else 'false') if isinstance(value, bool) else (str(value)+'D' if isinstance(value,(int,float)) else "'"+value.replace("'","''")+"'")
    return {'expr': {'Literal': {'Value':v}}}


def field(table, name, measure=False):
    return {'Measure' if measure else 'Column':{'Expression':{'SourceRef':{'Entity':table}},'Property':name}}


def projection(table, name, label=None, measure=False):
    return {'field':field(table,name,measure),'queryRef':table+'.'+name,'displayName':label or name}


def main():
    db=sqlite3.connect(ROOT/'data/processed/football.sqlite'); db.row_factory=sqlite3.Row
    tables=[]
    for name in ['rankings','profiles','weights','metrics','ranking_detail','sensitivity']:
        cols=[]; types=[]
        for col in db.execute('PRAGMA table_info('+name+')'):
            n,sqltype=col['name'],col['type'].upper()
            dtype='int64' if 'INT' in sqltype else 'double' if sqltype in ['REAL','FLOAT','NUMERIC'] else 'string'
            c={'name':n,'dataType':dtype,'sourceColumn':n,'summarizeBy':'none'}
            if dtype=='double':c['formatString']='0.00'
            if n=='role_share':c['formatString']='0.0%'
            if n=='minutes':c['formatString']='#,0'
            cols.append(c); types.append('{"'+n+'", '+{'int64':'Int64.Type','double':'type number','string':'type text'}[dtype]+'}')
        expr='let\n Source = Csv.Document(File.Contents(CarpetaDatos & "/'+name+'.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),\n Typed = Table.TransformColumnTypes(Nulls, {'+', '.join(types)+'}, "en-US")\nin Typed'
        tables.append({'name':name,'columns':cols,'partitions':[{'name':name,'mode':'import','source':{'type':'m','expression':expr.splitlines()}}]})
    for i in range(1,9):
        tables.append({'name':f'Peso{i}','columns':[{'name':'Value','dataType':'int64','sourceColumn':'[Value]','type':'calculatedTableColumn','summarizeBy':'none'}], 'partitions':[{'name':f'Peso{i}','mode':'import','source':{'type':'calculated','expression':'GENERATESERIES(0, 100, 1)'}}]})
    dax=(ROOT/'powerbi/Medidas.dax').read_text(encoding='utf-8')
    measures=[]
    body=dax.split('// Crear las siguientes medidas')[1].split('\n',1)[1]
    for block in re.split(r'\n\s*\n',body.strip()):
        name,expr=block.split('=',1)
        measures.append({'name':name.strip(),'expression':expr.strip().splitlines(),'formatString':'0' if name.strip()=='Ranking interactivo' else '0.00'})
    # A blank score must not appear as a negative change in the user interface.
    next(m for m in measures if m['name']=='Cambio de puntuacion')['expression']='IF(NOT ISBLANK([Puntuacion interactiva]), [Puntuacion interactiva] - SELECTEDVALUE(rankings[score_base]))'
    measures += [
        {'name':'Candidatos visibles','expression':'DISTINCTCOUNT(rankings[candidate_id])','formatString':'0'},
        {'name':'Perfil activo','expression':'SELECTEDVALUE(profiles[profile], "Selecciona un perfil")'},
        {'name':'Puesto base','expression':'SELECTEDVALUE(rankings[rank_base])','formatString':'0'},
        {'name':'Puntuacion base','expression':'SELECTEDVALUE(rankings[score_base])','formatString':'0.00'},
        {'name':'Diferencia de puesto','expression':'IF(NOT ISBLANK([Ranking interactivo]), [Ranking interactivo] - [Puesto base])','formatString':'0'},
    ]
    for i in range(1,9):
        m=next(m for m in measures if m['name']==f'Etiqueta peso {i}')
        m['expression']=f'''VAR Perfil=SELECTEDVALUE(profiles[profile_id])
VAR Metrica=LOOKUPVALUE(weights[metric_id],weights[profile_id],Perfil,weights[slot],{i})
VAR Base=LOOKUPVALUE(weights[weight],weights[profile_id],Perfil,weights[slot],{i})
VAR Nombre=SWITCH(Metrica,
"progressive_passes_p90","Pase progresivo /90",
"key_passes_open_play_p90","Pase de tiro abierto /90",
"key_passes_set_piece_p90","Pase de tiro parado /90",
"xg_assisted_open_play_p90","xG asistido abierto /90",
"xg_assisted_set_piece_p90","xG asistido parado /90",
SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(LOOKUPVALUE(metrics[label],metrics[metric_id],Metrica)," completados","")," exitosas",""),"Recepciones y tiros en el área","Recepción/tiro en área"))
RETURN IF(ISBLANK(Metrica), "No aplica", Nombre & " (base " & FORMAT(Base,"0") & ")")'''
        m.pop('formatString',None)
    tables[0]['measures']=measures
    # Deterministic Python oracle for the actual DAX query validation, independent of UI.
    rows=[dict(r) for r in db.execute('SELECT * FROM rankings')]
    scenarios=[('Base',None,None),('Ceros',[0]*8,None),('Solo progresion',[100]+[0]*7,None),('Organizador 32 y 8',[32,15,20,2,3,5,15,8],'organizador'),('Organizador 35 y 5',[35,15,20,2,3,5,15,5],'organizador'),('Organizador xG 25',[25,15,25,2,3,5,15,10],'organizador')]
    checks=[]; queryvars=[]; queryrows=[]
    for sn,(label,custom,profile) in enumerate(scenarios):
        selected=[r for r in rows if profile is None or r['profile_id']==profile]
        scores={}
        for r in selected:
            ws=[(custom[i-1] if custom else r[f'weight_{i}']) if r[f'metric_{i}'] else 0 for i in range(1,9)]
            scores[r['candidate_id']]=round(sum(w*(r[f'percentile_{i+1}'] or 0) for i,w in enumerate(ws))/sum(ws),8) if sum(ws) else None
        for r in selected:
            s=scores[r['candidate_id']]
            order=sorted({scores[z['candidate_id']] for z in selected if z['profile_id']==r['profile_id'] and scores[z['candidate_id']] is not None},reverse=True)
            checks.append({'scenario':label,'candidate_id':r['candidate_id'],'score':s,'rank':order.index(s)+1 if s is not None else None})
        filters=[]
        if profile:filters.append('TREATAS({"'+profile+'"}, profiles[profile_id])')
        if custom:filters += [f'TREATAS({{{w}}}, Peso{i+1}[Value])' for i,w in enumerate(custom)]
        # SUMMARIZECOLUMNS reproduces a table visual's grouping; ALLSELECTED can remove its row context.
        query='SUMMARIZECOLUMNS(rankings[profile_id], rankings[candidate_id], '+(', '.join(filters)+', ' if filters else '')+'"ActualScore", [Puntuacion interactiva], "ActualRank", [Ranking interactivo], "Keep", COUNTROWS(rankings))'
        queryvars.append(f'VAR S{sn} = '+query)
        queryvars.append(f'VAR C{sn} = ADDCOLUMNS(S{sn}, "ExpectedScore", LOOKUPVALUE(qa_expected[score], qa_expected[scenario], "{label}", qa_expected[candidate_id], rankings[candidate_id]), "ExpectedRank", LOOKUPVALUE(qa_expected[rank], qa_expected[scenario], "{label}", qa_expected[candidate_id], rankings[candidate_id]))')
        mismatch='IF(ISBLANK([ActualScore]) <> ISBLANK([ExpectedScore]) || ABS([ActualScore]-[ExpectedScore]) > 0.0000001, 1, 0)'
        badrank='IF(ISBLANK([ActualRank]) <> ISBLANK([ExpectedRank]) || [ActualRank] <> [ExpectedRank], 1, 0)'
        queryrows.append(f'ROW("Escenario", "{label}", "Candidatos", COUNTROWS(C{sn}), "Esperados", {len(selected)}, "Errores cohorte", ABS(COUNTROWS(C{sn})-{len(selected)}), "Errores score", SUMX(C{sn}, {mismatch}), "Errores ranking", SUMX(C{sn}, {badrank}))')
    expected=ROOT/'data/processed/qa_expected.csv'
    with expected.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['scenario','candidate_id','score','rank']);w.writeheader();w.writerows(checks)
    tables.append({'name':'qa_expected','isHidden':True,'columns':[{'name':n,'dataType':t,'sourceColumn':n,'summarizeBy':'none'} for n,t in [('scenario','string'),('candidate_id','string'),('score','double'),('rank','int64')]],'partitions':[{'name':'qa_expected','mode':'import','source':{'type':'m','expression':['let',' S=Csv.Document(File.Contents(CarpetaDatos & "/qa_expected.csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),',' H=Table.PromoteHeaders(S,[PromoteAllScalars=true]),',' N=Table.ReplaceValue(H,"",null,Replacer.ReplaceValue,Table.ColumnNames(H)),',' T=Table.TransformColumnTypes(N,{{"scenario",type text},{"candidate_id",type text},{"score",type number},{"rank",Int64.Type}},"en-US")','in T']}}]})
    qa='\n'.join(queryvars)+'\nRETURN UNION(\n'+',\n'.join(queryrows)+'\n)'
    tables.append({'name':'QA_resultados','columns':[{'name':n,'dataType':t,'type':'calculatedTableColumn','sourceColumn':'['+n+']','summarizeBy':'none'} for n,t in [('Escenario','string'),('Candidatos','int64'),('Esperados','int64'),('Errores cohorte','int64'),('Errores score','int64'),('Errores ranking','int64')]],'partitions':[{'name':'QA_resultados','mode':'import','source':{'type':'calculated','expression':qa.splitlines()}}]})
    relationships=[]
    for f,fc,t,tc in [('rankings','profile_id','profiles','profile_id'),('ranking_detail','candidate_id','rankings','candidate_id'),('ranking_detail','metric_id','metrics','metric_id')]:
        relationships.append({'name':f+'_'+fc+'_'+t,'fromTable':f,'fromColumn':fc,'toTable':t,'toColumn':tc,'crossFilteringBehavior':'oneDirection'})
    save(MODEL/'model.bim',{'name':'Scouting','compatibilityLevel':1567,'model':{'culture':'es-ES','sourceQueryCulture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3','expressions':[{'name':'CarpetaDatos','kind':'m','expression':'"'+str(ROOT/'data/processed').replace('\\','/')+'" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'}],'tables':tables,'relationships':relationships,'annotations':[{'name':'PBI_QueryOrder','value':json.dumps([t['name'] for t in tables])}]}})
    save(MODEL/'definition.pbism',{'version':'1.0','settings':{}})
    (MODEL/'DAXQueries').mkdir(parents=True,exist_ok=True)
    (MODEL/'DAXQueries/Validacion.dax').write_text('EVALUATE\n'+qa,encoding='utf-8')
    save(OUT/'Powerbi-scouting.pbip',{'version':'1.0','artifacts':[{'report':{'path':'Scouting.Report'}}],'settings':{'enableAutoRecovery':True}})
    save(REPORT/'definition.pbir',{'version':'4.0','datasetReference':{'byPath':{'path':'../Scouting.SemanticModel'}}})
    save(REPORT/'definition/version.json',{'$schema':SCHEMA+'versionMetadata/1.0.0/schema.json','version':'2.0.0'})
    theme=REPORT/'StaticResources/SharedResources/BaseThemes/CY24SU02.json'
    theme.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/'powerbi/base-theme/CY24SU02.json',theme)
    save(REPORT/'definition/report.json',{'$schema':SCHEMA+'report/3.0.0/schema.json','themeCollection':{'baseTheme':{'name':'CY24SU02','reportVersionAtImport':{'visual':'1.8.89','report':'2.0.89','page':'1.3.89'},'type':'SharedResources'}},'resourcePackages':[{'name':'SharedResources','type':'SharedResources','items':[{'name':'CY24SU02','path':'BaseThemes/CY24SU02.json','type':'BaseTheme'}]}],'settings':{'useEnhancedTooltips':True}})
    save(REPORT/'definition/pages/pages.json',{'$schema':SCHEMA+'pagesMetadata/1.0.0/schema.json','pageOrder':[uid(p) for p in ['ranking','validacion']],'activePageName':uid('ranking')})
    def visual(page,name,vtype,x,y,w,h,projections=None,role='Values',title=None,objects=None,sort=None):
        v={'visualType':vtype,'drillFilterOtherVisuals':True}
        if projections:v['query']={'queryState':{role:{'projections':projections}}}
        if sort:v['query']['sortDefinition']={'sort':[{'field':sort,'direction':'Descending'}],'isDefaultSort':False}
        if objects:v['objects']=copy.deepcopy(objects)
        if vtype=='tableEx':
            v['objects']={'grid':[{'properties':{'textSize':lit(14)}}],'columnHeaders':[{'properties':{'fontSize':lit(14)}}],'values':[{'properties':{'fontSize':lit(14)}}],'total':[{'properties':{'totals':lit(False)}}]}
        v['visualContainerObjects']={'background':[{'properties':{'color':{'solid':{'color':lit('#FFFFFF')}},'transparency':lit(0)}}]}
        if vtype=='slicer':v['visualContainerObjects']['visualHeader']=[{'properties':{'show':lit(False)}}]
        if title:v['visualContainerObjects']['title']=[{'properties':{'show':lit(True),'text':lit(title),'fontSize':lit(12),'fontColor':{'solid':{'color':lit('#173047')}}}}]
        ident=uid(page+'/'+name)
        data={'$schema':SCHEMA+'visualContainer/2.4.0/schema.json','name':ident,'position':{'x':x,'y':y,'z':0,'height':h,'width':w,'tabOrder':0},'visual':v}
        path=REPORT/f'definition/pages/{uid(page)}/visuals/{ident}/visual.json';save(path,data);return data,path
    def text(page,name,textvalue,x,y,w,h,size=12):
        return visual(page,name,'textbox',x,y,w,h,objects={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':textvalue,'textStyle':{'fontSize':str(size)+'pt','color':'#173047','fontFamily':'Segoe UI'}}]}]}}]})
    for page,label in [('ranking','Selección por perfil'),('validacion','Validación con Python')]:
        save(REPORT/f'definition/pages/{uid(page)}/page.json',{'$schema':SCHEMA+'page/1.4.0/schema.json','name':uid(page),'displayName':label,'displayOption':'FitToPage','width':1600,'height':1000})
    text('ranking','titulo','POWERBI-SCOUTING  |  LaLiga 2015/16',24,16,1500,60,26)
    text('ranking','instrucciones','1. Elige un perfil.  2. Ajusta pesos (sin selección = valor base).  3. Al cambiar de perfil, limpia los pesos.\nPuestos entre candidatos visibles; percentiles fijos. Datos: StatsBomb Open Data. Pesos exploratorios.',24,80,1530,70,12)
    slicerobj={'header':[{'properties':{'show':lit(True)}}],'data':[{'properties':{'mode':lit('Dropdown')}}],'selection':[{'properties':{'singleSelect':lit(True),'selectAllCheckboxEnabled':lit(False)}}]}
    d,p=visual('ranking','perfil','slicer',24,162,430,88,[projection('profiles','profile','Perfil / posición')],'Values','Perfil / posición',slicerobj)
    d['visual']['objects']['general']=[{'properties':{'filter':{'filter':{'Version':2,'From':[{'Name':'p','Entity':'profiles','Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'p'}},'Property':'profile'}}],'Values':[[{'Literal':{'Value':"'Centrocampista organizador'"}}]]}}}]}}}}]
    save(p,d)
    visual('ranking','equipo','slicer',475,162,370,88,[projection('rankings','teams','Equipo')],'Values','Equipo',{'data':[{'properties':{'mode':lit('Dropdown')}}]})
    visual('ranking','candidatos','tableEx',865,162,220,88,[projection('rankings','Candidatos visibles',measure=True)],'Values','Candidatos')
    text('ranking','muestra','Muestra: ≥900 min y ≥50% en roles del perfil.\nUna puntuación no es una probabilidad.',1105,162,460,88,12)
    for i in range(1,9):
        d,p=visual('ranking',f'peso{i}','slicer',24+((i-1)%4)*390,270+((i-1)//4)*135,370,85,[projection(f'Peso{i}','Value',f'Peso {i}')],'Values',f'Peso {i}',slicerobj.copy())
        d['visual']['visualContainerObjects']['title'][0]['properties']['text']={'expr':field('rankings',f'Etiqueta peso {i}',True)}
        save(p,d)
    projs=[projection('rankings','Ranking interactivo','Puesto',True),projection('rankings','player','Jugador'),projection('rankings','teams','Equipo'),projection('rankings','minutes','Minutos'),projection('rankings','role_share','Tiempo en rol'),projection('rankings','Puntuacion interactiva','Puntuación',True),projection('rankings','Puesto base','Puesto base',True),projection('rankings','Cambio de puntuacion','Δ puntuación',True)]
    visual('ranking','tabla','tableEx',24,540,1530,380,projs,'Values','Ranking según tus pesos',sort=field('rankings','Puntuacion interactiva',True))
    text('ranking','nota','El puesto base corresponde a la cohorte completa. Al filtrar equipo, el puesto interactivo se calcula en la selección.\nCreación abierta y balón parado siguen la definición versionada de la metodología.',335,930,1230,54,11)
    text('validacion','tituloqa','COMPROBACIÓN  |  Python frente a DAX',24,20,1500,60,26)
    text('validacion','notaqa','Resultados calculados por el motor DAX al actualizar el modelo. La referencia se genera desde los datos validados de Python.\nCada fila debe tener 0 errores. Esta página comprueba fórmulas; no certifica predicción futbolística.',24,90,1500,80,14)
    visual('validacion','tablaqa','tableEx',24,190,1510,470,[projection('QA_resultados',n) for n in ['Escenario','Candidatos','Esperados','Errores cohorte','Errores score','Errores ranking']],'Values','Pruebas de regresión')
    text('validacion','explicacion','Base: 387 candidatos en siete perfiles. Ceros: puntuación y puesto vacíos. Solo progresión: puntuación igual al percentil.\nLos tres escenarios de organizador comprueban los cambios ya analizados de André Gomes, Kroos y Trashorras.\n\nLimitaciones: tasas de temporada completa, sin ajuste por posesión/rival. Pesos elegidos, no aprendidos.\nPara repetir: reconstruir datos, ejecutar python -m src.build_powerbi y pulsar Actualizar en Desktop.\nFuente: StatsBomb Open Data. Desarrollo asistido por IA; decisiones y validación documentadas.',24,700,1510,230,14)
    db.close()
    print(json.dumps({'project':str(OUT/'Powerbi-scouting.pbip'),'tables':len(tables),'measures':len(measures),'oracle_rows':len(checks),'desktop_validated':False},ensure_ascii=False))


if __name__=='__main__':main()

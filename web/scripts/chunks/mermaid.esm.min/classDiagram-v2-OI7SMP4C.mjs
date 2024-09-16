import{a as nt,b as it,c as st,d as rt,e as ot}from"./chunk-GSYCYUAJ.mjs";import{a as tt,b as _,c as et}from"./chunk-OXEAGKI4.mjs";import{a as x}from"./chunk-4BPNZXC3.mjs";import{a as F,b as X,c as Q,d as U,e as Y,f as Z,g as $}from"./chunk-HWKFJHQF.mjs";import{a as B}from"./chunk-U6LOUQAF.mjs";import{d as K}from"./chunk-FVUI2UHO.mjs";import{a as I}from"./chunk-BOP2KBYH.mjs";import{a as J}from"./chunk-6XGRHI2A.mjs";import{c as O,d as A,m as q,p as V}from"./chunk-INOGIEW4.mjs";import"./chunk-TI4EEUUG.mjs";import{Ba as P,G as k,L as M,N as z,X as p,b as s,fa as E}from"./chunk-DMXVZUOD.mjs";import"./chunk-BKDDFIKN.mjs";import"./chunk-YPUTD6PB.mjs";import"./chunk-6BY5RJGC.mjs";import{a as g}from"./chunk-GTKDMUJJ.mjs";var f={},C={},at={},lt=g(()=>{C={},at={},f={}},"clear"),G=g((e,t)=>(s.trace("In isDescendant",t," ",e," = ",C[t].includes(e)),!!C[t].includes(e)),"isDescendant"),vt=g((e,t)=>(s.info("Descendants of ",t," is ",C[t]),s.info("Edge is ",e),e.v===t||e.w===t?!1:C[t]?C[t].includes(e.v)||G(e.v,t)||G(e.w,t)||C[t].includes(e.w):(s.debug("Tilt, ",t,",not in descendants"),!1)),"edgeInCluster"),ct=g((e,t,n,o)=>{s.warn("Copying children of ",e,"root",o,"data",t.node(e),o);let i=t.children(e)||[];e!==o&&i.push(e),s.warn("Copying (nodes) clusterId",e,"nodes",i),i.forEach(r=>{if(t.children(r).length>0)ct(r,t,n,o);else{let c=t.node(r);s.info("cp ",r," to ",o," with parent ",e),n.setNode(r,c),o!==t.parent(r)&&(s.warn("Setting parent",r,t.parent(r)),n.setParent(r,t.parent(r))),e!==o&&r!==e?(s.debug("Setting parent",r,e),n.setParent(r,e)):(s.info("In copy ",e,"root",o,"data",t.node(e),o),s.debug("Not Setting parent for node=",r,"cluster!==rootId",e!==o,"node!==clusterId",r!==e));let h=t.edges(r);s.debug("Copying Edges",h),h.forEach(d=>{s.info("Edge",d);let u=t.edge(d.v,d.w,d.name);s.info("Edge data",u,o);try{vt(d,o)?(s.info("Copying as ",d.v,d.w,u,d.name),n.setEdge(d.v,d.w,u,d.name),s.info("newGraph edges ",n.edges(),n.edge(n.edges()[0]))):s.info("Skipping copy of edge ",d.v,"-->",d.w," rootId: ",o," clusterId:",e)}catch(w){s.error(w)}})}s.debug("Removing node",r),t.removeNode(r)})},"copy"),dt=g((e,t)=>{let n=t.children(e),o=[...n];for(let i of n)at[i]=e,o=[...o,...dt(i,t)];return o},"extractDescendants");var T=g((e,t)=>{s.trace("Searching",e);let n=t.children(e);if(s.trace("Searching children of id ",e,n),n.length<1)return s.trace("This is a valid node",e),e;for(let o of n){let i=T(o,t);if(i)return s.trace("Found replacement for",e," => ",i),i}},"findNonClusterChild"),R=g(e=>!f[e]||!f[e].externalConnections?e:f[e]?f[e].id:e,"getAnchorId"),ft=g((e,t)=>{if(!e||t>10){s.debug("Opting out, no graph ");return}else s.debug("Opting in, graph ");e.nodes().forEach(function(n){e.children(n).length>0&&(s.warn("Cluster identified",n," Replacement id in edges: ",T(n,e)),C[n]=dt(n,e),f[n]={id:T(n,e),clusterData:e.node(n)})}),e.nodes().forEach(function(n){let o=e.children(n),i=e.edges();o.length>0?(s.debug("Cluster identified",n,C),i.forEach(r=>{if(r.v!==n&&r.w!==n){let c=G(r.v,n),h=G(r.w,n);c^h&&(s.warn("Edge: ",r," leaves cluster ",n),s.warn("Descendants of XXX ",n,": ",C[n]),f[n].externalConnections=!0)}})):s.debug("Not a cluster ",n,C)});for(let n of Object.keys(f)){let o=f[n].id,i=e.parent(o);i!==n&&f[i]&&!f[i].externalConnections&&(f[n].id=i)}e.edges().forEach(function(n){let o=e.edge(n);s.warn("Edge "+n.v+" -> "+n.w+": "+JSON.stringify(n)),s.warn("Edge "+n.v+" -> "+n.w+": "+JSON.stringify(e.edge(n)));let i=n.v,r=n.w;if(s.warn("Fix XXX",f,"ids:",n.v,n.w,"Translating: ",f[n.v]," --- ",f[n.w]),f[n.v]&&f[n.w]&&f[n.v]===f[n.w]){s.warn("Fixing and trixing link to self - removing XXX",n.v,n.w,n.name),s.warn("Fixing and trixing - removing XXX",n.v,n.w,n.name),i=R(n.v),r=R(n.w),e.removeEdge(n.v,n.w,n.name);let c=n.w+"---"+n.v;e.setNode(c,{domId:c,id:c,labelStyle:"",labelText:o.label,padding:0,shape:"labelRect",style:""});let h=structuredClone(o),d=structuredClone(o);h.label="",h.arrowTypeEnd="none",d.label="",h.fromCluster=n.v,d.toCluster=n.v,e.setEdge(i,c,h,n.name+"-cyclic-special"),e.setEdge(c,r,d,n.name+"-cyclic-special")}else if(f[n.v]||f[n.w]){if(s.warn("Fixing and trixing - removing XXX",n.v,n.w,n.name),i=R(n.v),r=R(n.w),e.removeEdge(n.v,n.w,n.name),i!==n.v){let c=e.parent(i);f[c].externalConnections=!0,o.fromCluster=n.v}if(r!==n.w){let c=e.parent(r);f[c].externalConnections=!0,o.toCluster=n.w}s.warn("Fix Replacing with XXX",i,r,n.name),e.setEdge(i,r,o,n.name)}}),s.warn("Adjusted Graph",x(e)),ht(e,0),s.trace(f)},"adjustClustersAndEdges"),ht=g((e,t)=>{if(s.warn("extractor - ",t,x(e),e.children("D")),t>10){s.error("Bailing out");return}let n=e.nodes(),o=!1;for(let i of n){let r=e.children(i);o=o||r.length>0}if(!o){s.debug("Done, no node has children",e.nodes());return}s.debug("Nodes = ",n,t);for(let i of n)if(s.debug("Extracting node",i,f,f[i]&&!f[i].externalConnections,!e.parent(i),e.node(i),e.children("D")," Depth ",t),!f[i])s.debug("Not a cluster",i,t);else if(!f[i].externalConnections&&e.children(i)&&e.children(i).length>0){s.warn("Cluster without external connections, without a parent and with children",i,t);let c=e.graph().rankdir==="TB"?"LR":"TB";f[i]?.clusterData?.dir&&(c=f[i].clusterData.dir,s.warn("Fixing dir",f[i].clusterData.dir,c));let h=new J({multigraph:!0,compound:!0}).setGraph({rankdir:c,nodesep:50,ranksep:50,marginx:8,marginy:8}).setDefaultEdgeLabel(function(){return{}});s.warn("Old graph before copy",x(e)),ct(i,e,h,i),e.setNode(i,{clusterNode:!0,id:i,clusterData:f[i].clusterData,labelText:f[i].labelText,graph:h}),s.warn("New graph after copy node: (",i,")",x(h)),s.debug("Old graph after copy",x(e))}else s.warn("Cluster ** ",i," **not meeting the criteria !externalConnections:",!f[i].externalConnections," no parent: ",!e.parent(i)," children ",e.children(i)&&e.children(i).length>0,e.children("D"),t),s.debug(f);n=e.nodes(),s.warn("New list of nodes",n);for(let i of n){let r=e.node(i);s.warn(" Now next level",i,r),r.clusterNode&&ht(r.graph,t+1)}},"extractor"),gt=g((e,t)=>{if(t.length===0)return[];let n=Object.assign(t);return t.forEach(o=>{let i=e.children(o),r=gt(e,i);n=[...n,...r]}),n},"sorter"),ut=g(e=>gt(e,e.children()),"sortNodesByHierarchy");var Tt=g((e,t)=>{s.info("Creating subgraph rect for ",t.id,t);let n=p(),o=e.insert("g").attr("class","cluster"+(t.class?" "+t.class:"")).attr("id",t.id),i=o.insert("rect",":first-child"),r=k(n.flowchart.htmlLabels),c=o.insert("g").attr("class","cluster-label"),h=t.labelType==="markdown"?K(c,t.labelText,{style:t.labelStyle,useHtmlLabels:r},n):c.node().appendChild(F(t.labelText,t.labelStyle,void 0,!0)),d=h.getBBox();if(k(n.flowchart.htmlLabels)){let a=h.children[0],l=E(h);d=a.getBoundingClientRect(),l.attr("width",d.width),l.attr("height",d.height)}let u=0*t.padding,w=u/2,m=t.width<=d.width+u?d.width+u:t.width;t.width<=d.width+u?t.diff=(d.width-t.width)/2-t.padding/2:t.diff=-t.padding/2,s.trace("Data ",t,JSON.stringify(t)),i.attr("style",t.style).attr("rx",t.rx).attr("ry",t.ry).attr("x",t.x-m/2).attr("y",t.y-t.height/2-w).attr("width",m).attr("height",t.height+u);let{subGraphTitleTopMargin:b}=B(n);r?c.attr("transform",`translate(${t.x-d.width/2}, ${t.y-t.height/2+b})`):c.attr("transform",`translate(${t.x}, ${t.y-t.height/2+b})`);let y=i.node().getBBox();return t.width=y.width,t.height=y.height,t.intersect=function(a){return X(t,a)},o},"rect"),Dt=g((e,t)=>{let n=e.insert("g").attr("class","note-cluster").attr("id",t.id),o=n.insert("rect",":first-child"),i=0*t.padding,r=i/2;o.attr("rx",t.rx).attr("ry",t.ry).attr("x",t.x-t.width/2-r).attr("y",t.y-t.height/2-r).attr("width",t.width+i).attr("height",t.height+i).attr("fill","none");let c=o.node().getBBox();return t.width=c.width,t.height=c.height,t.intersect=function(h){return X(t,h)},n},"noteGroup"),kt=g((e,t)=>{let n=p(),o=e.insert("g").attr("class",t.classes).attr("id",t.id),i=o.insert("rect",":first-child"),r=o.insert("g").attr("class","cluster-label"),c=o.append("rect"),h=r.node().appendChild(F(t.labelText,t.labelStyle,void 0,!0)),d=h.getBBox();if(k(n.flowchart.htmlLabels)){let a=h.children[0],l=E(h);d=a.getBoundingClientRect(),l.attr("width",d.width),l.attr("height",d.height)}d=h.getBBox();let u=0*t.padding,w=u/2,m=t.width<=d.width+t.padding?d.width+t.padding:t.width;t.width<=d.width+t.padding?t.diff=(d.width+t.padding*0-t.width)/2:t.diff=-t.padding/2,i.attr("class","outer").attr("x",t.x-m/2-w).attr("y",t.y-t.height/2-w).attr("width",m+u).attr("height",t.height+u),c.attr("class","inner").attr("x",t.x-m/2-w).attr("y",t.y-t.height/2-w+d.height-1).attr("width",m+u).attr("height",t.height+u-d.height-3);let{subGraphTitleTopMargin:b}=B(n);r.attr("transform",`translate(${t.x-d.width/2}, ${t.y-t.height/2-t.padding/3+(k(n.flowchart.htmlLabels)?5:3)+b})`);let y=i.node().getBBox();return t.height=y.height,t.intersect=function(a){return X(t,a)},o},"roundedWithTitle"),Xt=g((e,t)=>{let n=e.insert("g").attr("class",t.classes).attr("id",t.id),o=n.insert("rect",":first-child"),i=0*t.padding,r=i/2;o.attr("class","divider").attr("x",t.x-t.width/2-r).attr("y",t.y-t.height/2).attr("width",t.width+i).attr("height",t.height+i);let c=o.node().getBBox();return t.width=c.width,t.height=c.height,t.diff=-t.padding/2,t.intersect=function(h){return X(t,h)},n},"divider"),Bt={rect:Tt,roundedWithTitle:kt,noteGroup:Dt,divider:Xt},pt={},mt=g((e,t)=>{s.trace("Inserting cluster");let n=t.shape||"rect";pt[t.id]=Bt[n](e,t)},"insertCluster");var wt=g(()=>{pt={}},"clear");var yt=g(async(e,t,n,o,i,r)=>{s.info("Graph in recursive render: XXX",x(t),i);let c=t.graph().rankdir;s.trace("Dir in recursive render - dir:",c);let h=e.insert("g").attr("class","root");t.nodes()?s.info("Recursive render XXX",t.nodes()):s.info("No nodes found for",t),t.edges().length>0&&s.trace("Recursive edges",t.edge(t.edges()[0]));let d=h.insert("g").attr("class","clusters"),u=h.insert("g").attr("class","edgePaths"),w=h.insert("g").attr("class","edgeLabels"),m=h.insert("g").attr("class","nodes");await Promise.all(t.nodes().map(async function(a){let l=t.node(a);if(i!==void 0){let N=JSON.parse(JSON.stringify(i.clusterData));s.info("Setting data for cluster XXX (",a,") ",N,i),t.setNode(i.id,N),t.parent(a)||(s.trace("Setting parent",a,i.id),t.setParent(a,i.id,N))}if(s.info("(Insert) Node XXX"+a+": "+JSON.stringify(t.node(a))),l?.clusterNode){s.info("Cluster identified",a,l.width,t.node(a));let{ranksep:N,nodesep:v}=t.graph();l.graph.setGraph({...l.graph.graph(),ranksep:N,nodesep:v});let L=await yt(m,l.graph,n,o,t.node(a),r),S=L.elem;Q(l,S),l.diff=L.diff||0,s.info("Node bounds (abc123)",a,l,l.width,l.x,l.y),Y(S,l),s.warn("Recursive render complete ",S,l)}else t.children(a).length>0?(s.info("Cluster - the non recursive path XXX",a,l.id,l,t),s.info(T(l.id,t)),f[l.id]={id:T(l.id,t),node:l}):(s.info("Node - the non recursive path",a,l.id,l),await U(m,t.node(a),c))})),t.edges().forEach(async function(a){let l=t.edge(a.v,a.w,a.name);s.info("Edge "+a.v+" -> "+a.w+": "+JSON.stringify(a)),s.info("Edge "+a.v+" -> "+a.w+": ",a," ",JSON.stringify(t.edge(a))),s.info("Fix",f,"ids:",a.v,a.w,"Translating: ",f[a.v],f[a.w]),await st(w,l)}),t.edges().forEach(function(a){s.info("Edge "+a.v+" -> "+a.w+": "+JSON.stringify(a))}),s.info("Graph before layout:",JSON.stringify(x(t))),s.info("#############################################"),s.info("###                Layout                 ###"),s.info("#############################################"),s.info(t),I(t),s.info("Graph after layout:",JSON.stringify(x(t)));let b=0,{subGraphTitleTotalMargin:y}=B(r);return ut(t).forEach(function(a){let l=t.node(a);s.info("Position "+a+": "+JSON.stringify(t.node(a))),s.info("Position "+a+": ("+l.x,","+l.y,") width: ",l.width," height: ",l.height),l?.clusterNode?(l.y+=y,$(l)):t.children(a).length>0?(l.height+=y,mt(d,l),f[l.id].node=l):(l.y+=y/2,$(l))}),t.edges().forEach(function(a){let l=t.edge(a);s.info("Edge "+a.v+" -> "+a.w+": "+JSON.stringify(l),l),l.points.forEach(v=>v.y+=y/2);let N=ot(u,a,l,f,n,t,o);rt(l,N)}),t.nodes().forEach(function(a){let l=t.node(a);s.info(a,l.type,l.diff),l.type==="group"&&(b=l.diff)}),{elem:h,diff:b}},"recursiveRender"),bt=g(async(e,t,n,o,i)=>{nt(e,n,o,i),Z(),it(),wt(),lt(),s.warn("Graph at first:",JSON.stringify(x(t))),ft(t),s.warn("Graph after:",JSON.stringify(x(t)));let r=p();await yt(e,t,o,i,void 0,r)},"render");var W=g(e=>M.sanitizeText(e,p()),"sanitizeText"),H={dividerMargin:10,padding:5,textHeight:10,curve:void 0},Lt=g(function(e,t,n,o){s.info("keys:",[...e.keys()]),s.info(e),e.forEach(function(i){let c={shape:"rect",id:i.id,domId:i.domId,labelText:W(i.id),labelStyle:"",style:"fill: none; stroke: black",padding:p().flowchart?.padding??p().class?.padding};t.setNode(i.id,c),Ct(i.classes,t,n,o,i.id),s.info("setNode",c)})},"addNamespaces"),Ct=g(function(e,t,n,o,i){s.info("keys:",[...e.keys()]),s.info(e),[...e.values()].filter(r=>r.parent===i).forEach(function(r){let c=r.cssClasses.join(" "),h=A(r.styles),d=r.label??r.id,u=0,m={labelStyle:h.labelStyle,shape:"class_box",labelText:W(d),classData:r,rx:u,ry:u,class:c,style:h.style,id:r.id,domId:r.domId,tooltip:o.db.getTooltip(r.id,i)||"",haveCallback:r.haveCallback,link:r.link,width:r.type==="group"?500:void 0,type:r.type,padding:p().flowchart?.padding??p().class?.padding};t.setNode(r.id,m),i&&t.setParent(r.id,i),s.info("setNode",m)})},"addClasses"),Jt=g(function(e,t,n,o){s.info(e),e.forEach(function(i,r){let c=i,h="",d={labelStyle:"",style:""},u=c.text,w=0,b={labelStyle:d.labelStyle,shape:"note",labelText:W(u),noteData:c,rx:w,ry:w,class:h,style:d.style,id:c.id,domId:c.id,tooltip:"",type:"note",padding:p().flowchart?.padding??p().class?.padding};if(t.setNode(c.id,b),s.info("setNode",b),!c.class||!o.has(c.class))return;let y=n+r,a={id:`edgeNote${y}`,classes:"relation",pattern:"dotted",arrowhead:"none",startLabelRight:"",endLabelLeft:"",arrowTypeStart:"none",arrowTypeEnd:"none",style:"fill:none",labelStyle:"",curve:O(H.curve,P)};t.setEdge(c.id,c.class,a,y)})},"addNotes"),Rt=g(function(e,t){let n=p().flowchart,o=0;e.forEach(function(i){o++;let r={classes:"relation",pattern:i.relation.lineType==1?"dashed":"solid",id:V(i.id1,i.id2,{prefix:"id",counter:o}),arrowhead:i.type==="arrow_open"?"none":"normal",startLabelRight:i.relationTitle1==="none"?"":i.relationTitle1,endLabelLeft:i.relationTitle2==="none"?"":i.relationTitle2,arrowTypeStart:xt(i.relation.type1),arrowTypeEnd:xt(i.relation.type2),style:"fill:none",labelStyle:"",curve:O(n?.curve,P)};if(s.info(r,i),i.style!==void 0){let c=A(i.style);r.style=c.style,r.labelStyle=c.labelStyle}i.text=i.title,i.text===void 0?i.style!==void 0&&(r.arrowheadStyle="fill: #333"):(r.arrowheadStyle="fill: #333",r.labelpos="c",p().flowchart?.htmlLabels??p().htmlLabels?(r.labelType="html",r.label='<span class="edgeLabel">'+i.text+"</span>"):(r.labelType="text",r.label=i.text.replace(M.lineBreakRegex,`
`),i.style===void 0&&(r.style=r.style||"stroke: #333; stroke-width: 1.5px;fill:none"),r.labelStyle=r.labelStyle.replace("color:","fill:"))),t.setEdge(i.id1,i.id2,r,o)})},"addRelations"),Gt=g(function(e){H={...H,...e}},"setConf"),Mt=g(async function(e,t,n,o){s.info("Drawing class - ",t);let i=p().flowchart??p().class,r=p().securityLevel;s.info("config:",i);let c=i?.nodeSpacing??50,h=i?.rankSpacing??50,d=new J({multigraph:!0,compound:!0}).setGraph({rankdir:o.db.getDirection(),nodesep:c,ranksep:h,marginx:8,marginy:8}).setDefaultEdgeLabel(function(){return{}}),u=o.db.getNamespaces(),w=o.db.getClasses(),m=o.db.getRelations(),b=o.db.getNotes();s.info(m),Lt(u,d,t,o),Ct(w,d,t,o),Rt(m,d),Jt(b,d,m.length+1,w);let y;r==="sandbox"&&(y=E("#i"+t));let a=r==="sandbox"?E(y.nodes()[0].contentDocument.body):E("body"),l=a.select(`[id="${t}"]`),N=a.select("#"+t+" g");if(await bt(N,d,["aggregation","extension","composition","dependency","lollipop"],"classDiagram",t),q.insertTitle(l,"classTitleText",i?.titleTopMargin??5,o.db.getDiagramTitle()),z(d,l,i?.diagramPadding,i?.useMaxWidth),!i?.htmlLabels){let v=r==="sandbox"?y.nodes()[0].contentDocument:document,L=v.querySelectorAll('[id="'+t+'"] .edgeLabel .label');for(let S of L){let j=S.getBBox(),D=v.createElementNS("http://www.w3.org/2000/svg","rect");D.setAttribute("rx",0),D.setAttribute("ry",0),D.setAttribute("width",j.width),D.setAttribute("height",j.height),S.insertBefore(D,S.firstChild)}}},"draw");function xt(e){let t;switch(e){case 0:t="aggregation";break;case 1:t="extension";break;case 2:t="composition";break;case 3:t="dependency";break;case 4:t="lollipop";break;default:t="none"}return t}g(xt,"getArrowMarker");var Nt={setConf:Gt,draw:Mt};var Ce={parser:tt,db:_,renderer:Nt,styles:et,init:g(e=>{e.class||(e.class={}),e.class.arrowMarkerAbsolute=e.arrowMarkerAbsolute,_.clear()},"init")};export{Ce as diagram};

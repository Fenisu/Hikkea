(function(a){function l(a,b){var c=new Object,d=new Object;for(var e=0;e<b.length;e++)c[b[e]]==null&&(c[b[e]]={rows:[],o:null}),c[b[e]].rows.push(e);for(var e=0;e<a.length;e++)d[a[e]]==null&&(d[a[e]]={rows:[],n:null}),d[a[e]].rows.push(e);for(var e in c)c[e].rows.length==1&&typeof d[e]!="undefined"&&d[e].rows.length==1&&(b[c[e].rows[0]]={text:b[c[e].rows[0]],row:d[e].rows[0]},a[d[e].rows[0]]={text:a[d[e].rows[0]],row:c[e].rows[0]});for(var e=0;e<b.length-1;e++)b[e].text!=null&&b[e+1].text==null&&b[e].row+1<a.length&&a[b[e].row+1].text==null&&b[e+1]==a[b[e].row+1]&&(b[e+1]={text:b[e+1],row:b[e].row+1},a[b[e].row+1]={text:a[b[e].row+1],row:e+1});for(var e=b.length-1;e>0;e--)b[e].text!=null&&b[e-1].text==null&&b[e].row>0&&a[b[e].row-1].text==null&&b[e-1]==a[b[e].row-1]&&(b[e-1]={text:b[e-1],row:b[e].row-1},a[b[e].row-1]={text:a[b[e].row-1],row:e-1});return{o:a,n:b}}function k(a,b,c){a=a.replace(/\s+$/,""),b=b.replace(/\s+$/,"");var d=l(a==""?[]:a.split(/\s+/),b==""?[]:b.split(/\s+/)),e="",f=a.match(/\s+/g);f==null?f=["\n"]:f.push("\n");var g=b.match(/\s+/g);g==null?g=["\n"]:g.push("\n");if(d.n.length==0)for(var h=0;h<d.o.length;h++)e+='<del tabindex="1">'+j(d.o[h])+f[h]+"</del>",c.equal=!1;else{if(d.n[0].text==null)for(b=0;b<d.o.length&&d.o[b].text==null;b++)e+='<del tabindex="1">'+j(d.o[b])+f[b]+"</del>",c.equal=!1;for(var h=0;h<d.n.length;h++)if(d.n[h].text==null)e+='<ins tabindex="1">'+j(d.n[h])+g[h]+"</ins>",c.equal=!1;else{var i="";for(b=d.n[h].row+1;b<d.o.length&&d.o[b].text==null;b++)i+='<del tabindex="1">'+j(d.o[b])+f[b]+"</del>",c.equal=!1;e+=" "+d.n[h].text+g[h]+i}}return e}function j(a,b){var c=a;c=c.replace(/&/g,"&amp;"),c=c.replace(/</g,"&lt;"),c=c.replace(/>/g,"&gt;"),c=c.replace(/"/g,"&quot;"),b&&(c=c.replace(/\s\s/g,"&nbsp; "),c=c.replace(/\n/g,"<br/>"));return c}function i(a){return a.nodeName.indexOf("/")>-1}function h(b){var c={},d=b.split(";");for(var e=0;e<d.length;e++){var f=d[e];if(a.trim(f)!=""){var g=f.split(":",2);g[0]=a.trim(g[0]),g[1]=a.trim(g[1]),g[1].length>0&&(c[g[0]]=g[1])}}return c}function g(b,c){return a(b).attr(c.nodeName)}function f(c,d,e,f,g){if(e==f)c.push(e);else if(d=="style"){var i={},j=h(String(e)),l=h(String(f));for(var m in j){var n=j[m],o=l[m];i[m]=!0,o?(c.push(m,":"),n!=o?(g.equal=!1,c.push("<del tabindex='1'>",n,"</del><ins tabindex='1'>",o,"</ins>;")):c.push(n,";")):(c.push("<del tabindex='1'>",m,":",n,";</del>"),g.equal=!1)}for(var p in l)i[p]||(c.push("<ins tabindex='1'>",p,":",l[p],";</ins>"),g.equal=!1)}else b[d]?c.push(e):c.push(a.trim(k(String(e),String(f),g)))}function e(a,b,c,d){var e={},h=b==null?null:b.attributes,i=c==null?null:c.attributes;if(h)for(var k=0;k<h.length;k++){var l=h[k];if(l.nodeName.indexOf("xmlns:")==0||!l.specified)continue;var m=null;i&&(m=i.getNamedItem(l.nodeName),m&&!m.specified&&(m=null)),e[l.nodeName]=!0,a.push(" ","<nobr>");if(!m){var n=g(b,l);n!=null&&n.length>0&&(a.push("<del tabindex='1'><span class='attrname'>",l.nodeName,"</span>=&quot;"),a.push("<span class='attrvalue'>",j(String(n),!0),"</span>"),a.push("&quot;","</del>"),d.equal=!1)}else{a.push("<nobr>"),a.push("<span class='attrname'>",l.nodeName,"</span>=&quot;"),a.push("<span class='attrvalue'>");var n=g(b,l),o=g(c,m);f(a,l.nodeName.toLowerCase(),n,o,d),a.push("</span>"),a.push("&quot;")}a.push("</nobr>")}if(i)for(var k=0;k<i.length;k++){var m=i[k];if(m.nodeName.indexOf("xmlns:")==0||!m.specified)continue;if(!e[m.nodeName]){var p=g(c,m);p!=null&&p.length>0&&(a.push(" ","<ins tabindex='1'><span class='attrname'>",m.nodeName,"</span>=&quot;"),a.push(j(String(p),!0)),a.push("&quot;","</ins>"),d.equal=!1)}}}function d(a,b,d,e){a.push("<ul class='indent'>");if(b&&!d)for(var f=0;f<b.length;f++)i(b[f])||(a.push("<li>"),c(a,b[f],null,e),a.push("</li>"));else if(!b&&d)for(var f=0;f<d.length;f++)i(d[f])||(a.push("<li>"),c(a,null,d[f],e),a.push("</li>"));else{var g=0,h=0;while(g<b.length){var j=b[g];if(!i(j)){var k=null;while(h<d.length&&k==null){k=d[h];if(!i(k)){if(j.nodeType==k.nodeType&&j.nodeName==k.nodeName){h++;break}a.push("<li>"),c(a,null,k,e),a.push("</li>"),k=null,h++}else k=null,h++}c(a,j,k,e)}g++}while(h<d.length){var k=d[h];i(k)||(a.push("<li>"),c(a,null,k,e),a.push("</li>")),h++}}a.push("</ul>")}function c(b,c,f,g){c&&!f?c.nodeType==1?(g.equal=!1,b.push("<del tabindex='1'>"),b.push("<span class='taglt'>","&lt;","</span>"),b.push("<span class='tag'>"),b.push(c.nodeName.toLowerCase()),b.push("</span>"),b.push("</del>"),b.push(" "),e(b,c,null,g),c.childNodes.length>0?(b.push("<span class='taggt'>","&gt;","</span><br />"),d(b,c.childNodes,null,g),b.push("<del tabindex='1'>"),b.push("<span class='taglt'>","&lt;/","</span>"),b.push("<span class='tag'>"),b.push(c.nodeName.toLowerCase()),b.push("</span>"),b.push("<span class='taggt'>","&gt;","</span>","</del><br />")):b.push("<span class='taggt'>","/&gt;","</span><br />")):c.nodeType==3&&(g.equal=!1,b.push("<del tabindex='1'>"),b.push(j(c.nodeValue,!0)),b.push("</del>")):!c&&f?f.nodeType==1?(g.equal=!1,b.push("<ins tabindex='1'>"),b.push("<span class='taglt'>","&lt;","</span>"),b.push("<span class='tag'>"),b.push(f.nodeName.toLowerCase()),b.push("</span>"),b.push("</ins>"),b.push(" "),e(b,null,f,g),f.childNodes.length>0?(b.push("<span class='taggt'>","&gt;","</span><br />"),d(b,null,f.childNodes,g),b.push("<del tabindex='1'>"),b.push("<span class='taglt'>","&lt;/","</span>"),b.push("<span class='tag'>"),b.push(f.nodeName.toLowerCase()),b.push("</span><br />"),b.push("<span class='taggt'>","&gt;","</span>","</del><br />")):b.push("<span class='taggt'>","/&gt;","</span><br />")):f.nodeType==3&&(g.equal=!1,b.push("<del tabindex='1'>"),b.push(j(f.nodeValue,!0)),b.push("</del><br />")):c.nodeType==1&&f.nodeType==1?(b.push("<span class='taglt'>","&lt;","</span>"),b.push("<span class='tag'>"),b.push(a.trim(k(String(c.nodeName.toLowerCase()),String(f.nodeName.toLowerCase()),g))),b.push("</span>"),e(b,c,f,g),c.childNodes.length>0||f.childNodes.length>0?(b.push("<span class='taggt'>","&gt;","</span>","<br />"),d(b,c.childNodes,f.childNodes,g),b.push("<span class='taglt'>","&lt;/","</span>"),b.push("<span class='tag'>"),b.push(a.trim(k(String(c.nodeName.toLowerCase()),String(f.nodeName.toLowerCase()),g))),b.push("</span>"),b.push("<span class='taggt'>","&gt;","</span><br />")):b.push("<span class='taggt'>","/&gt;","</span><br />")):c.nodeType==3&&f.nodeType==3&&b.push(k(String(c.nodeValue),String(f.nodeValue),g))}var b={checked:!0,compact:!0,defer:!0,disabled:!0,ismap:!0,multiple:!0,nohref:!0,noresize:!0,noshade:!0,nowrap:!0,readonly:!0,selected:!0};a.compare=function(a,b){a&&a.jquery&&(a=a.get(0)),b&&b.jquery&&(b=b.get(0));if(a&&b){var d={equal:!0},e=['<div data-equal="',"0","\" class='code' >"];e.push("<style>"),e.push(".code {font-size: 10pt;"),e.push("color: black;"),e.push('font-family: "Courier New", Courier, Monospace;'),e.push("background-color: #ffffff;}"),e.push("del { color:red; }"),e.push("ins { background-color:yellow;}"),e.push(".tag, .taglt, .taggt {color:brown;}"),e.push(".attrname {color:red;}"),e.push(".attrvalue {color:blue;}"),e.push(".indent { list-style-type:none;border-left: 1px solid #F0F0E9;margin-left: 0px;padding-left: 30px;}"),e.push("</style>"),c(e,a,b,d),e.push("</div>"),e[1]=d.equal?"1":"0";return e.join("")}return"<b>Could not compare.</b>"},a.fn.compare=function(b){return a.compare(this,b)}})(jQuery);
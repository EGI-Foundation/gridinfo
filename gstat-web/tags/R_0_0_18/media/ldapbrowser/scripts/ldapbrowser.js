<!-- Loading YUI libraries -->


	var loader = new YAHOO.util.YUILoader({ 
	    require: ["datatable", "fonts", "treeview"], 
	    loadOptional: true,
	    //onSuccess: function() {YAHOO.util.Event.onDOMReady(buildTree, true);}, 
	    timeout: 10000,
	    combine: true 
	}); 
	loader.insert();


<!-- treeinteraction.js -->

function loadData(node, fnLoadComplete)  {
    var callback = {
        success: function(Response) {
		    var Results =  eval("(" + Response.responseText + ")");
		    YAHOO.log(Response.responseText, "info", "example");
		    if (Results && (Results.length > 0)) {
		        for (var i=0, j=Results.length; i<j; i++) {
		    		label = Results[i].substring(0, Results[i].indexOf(node.label)-1)
		            var newNode = new YAHOO.widget.MenuNode(label, node, false);
		            newNode.title = Results[i];
		        }
	        }
		    Response.argument.fnLoadComplete();
		},
        failure: function(Response) {
            Response.argument.fnLoadComplete();
        },
        argument: {
            "node": node,
            "fnLoadComplete": fnLoadComplete
        },
        timeout: 7000
    };
            
    var nodeLabel = encodeURI(node.title);
    var url = "/gstat/ldap/browse?host=" + host + "&dn=" + nodeLabel;
    YAHOO.util.Connect.asyncRequest('GET', url, callback);
}

function showEntry(node, fnLoadComplete)  {           
    var nodeLabel = encodeURI(node.title);
    var url = "/gstat/ldap/browse?host=" + host + "&entry=true&dn=" + nodeLabel;
    YAHOO.util.Dom.get('entry').data = url;
}

function buildTree() {
    var tree = new YAHOO.widget.TreeView("tree");
    tree.setDynamicLoad(loadData, 1);
    var root = tree.getRoot();
    var rootNode = new YAHOO.widget.MenuNode("o=grid", root, false);
    rootNode.title = "o=grid";
    tree.subscribe("expand", function(node){ showEntry(node) });
    tree.draw();
}


<!-- attributesobject.js -->

	var alwayscombo={
		//Position of com box from window edge ["top|bottom", "left|right"]
		location: ["top", "right"],
		//Additional offset from specified location above [vertical, horizontal]
		addoffset: [190, window.innerWidth/2-470],
		//ID of div containing the floating element
		comboid: "entry",
	
		floatcombo:function(){
			var docElement=(document.compatMode=='CSS1Compat')? document.documentElement: document.body
			this.comboref.height=window.innerHeight-200;
			if (this.location[0]=="top") {
				this.comboref.style.top=0+this.addoffset[0]+"px";
			} else if (this.location[0]=="bottom")
				this.comboref.style.bottom=0+this.addoffset[0]+"px"
			if (this.location[1]=="left")
				this.comboref.style.left=0+this.addoffset[1]+"px"
			else if (this.location[1]=="right")
				this.comboref.style.right=0+this.addoffset[1]+"px"
		},
	
		init:function(){
			this.comboref=document.getElementById(this.comboid)
			this.comboref.style.visibility="visible"
			this.floatcombo()
		}
	}


	if (window.addEventListener)
		window.addEventListener("load", function(){alwayscombo.init()}, false)
	else if (window.attachEvent)
		window.attachEvent("onload", function(){alwayscombo.init()})


<!-- selectbox.js -->

	host='';
	var selectbox={
		navigate:function(selectobj){
			if (selectobj.options[selectobj.selectedIndex].value!="default") {
				host=selectobj.options[selectobj.selectedIndex].value;
				buildTree();
				YAHOO.util.Dom.get('entry').data = "/gstat/ldap/browse";
			}
		}
	}

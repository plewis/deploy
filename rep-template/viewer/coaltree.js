// The MIT License (MIT)
//
// Copyright (c) 2017-2023 Paul O. Lewis
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the “Software”), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
 
// Use with sort to compare only the first elements of supplied vectors a and b
// The first elements of both a and b should be numeric values.
function compareFirstElements(a, b) {
  if (a[0] < b[0]) {
    return -1;
  }
  if (a[0] > b[0]) {
    return 1;
  }
  // a[0] must be equal to b[0]
  return 0;
}

// Use with sort to compare the height attribute of supplied vectors a and b
// Both a.height and b.height should be numeric values.
function compareHeights(a, b) {
  if (a.height < b.height) {
    return -1;
  }
  if (a.height > b.height) {
    return 1;
  }
  // a[.height must be equal to b.height
  return 0;
}

function setsEqual(xset, yset) {
    return xset.size === yset.size && [...xset].every((x) => yset.has(x));
}

function TreeNode() {
    this.x = null,
    this.y = null,
    this.lchild =  null,
    this.rsib = null,
    this.parent = null,
    this.edgelen = 0.0,
    this.name = "",
    this.number = -1,
    this.radius = 0.0
    this.height = 0.0;
    this.info = "";
    this.loglike = 0.0;
}

function Tree() {
    this.nleaves = 0,
    this.root = [],         // Tree can have many root nodes (i.e. it can be a forest)
    this.preorder = [];     // preorder[i] is list of TreeNode objects in preorder sequence starting with root[i]
    this.xmax = 0.0;
    this.ymax = 0.0;
    this.maxPIDIC = [0.0, 0.0, 0.0, 0.0];   // maximum values of P, I, D, and IC over all nodes
}

TreeNode.prototype.setInfoAndRadius = function(which) {
    var pidic = [0.0, 0.0, 0.0, 0.0];
    if (this.lchild) {
        var m = this.name.match(/P=([0-9.-]+) I=([0-9.-]+) D=([0-9.-]+) IC=([0-9.-]+)/);
        if (m != null) {
            var P = Number(m[1]);
            var I = Number(m[2]);
            var D = Number(m[3]);
            if (D < 0.0)
                D = 0.0;
            var IC = Number(m[4]);
            pidic = [P, I, D, IC];
            this.radius = pidic[which];
            this.info = "<p>P = " + P + "</p><p>I = " + I + "</p><p>D = " + D + "</p><p>IC = " + IC + "</p>";
        }
    }
    else {
        console.log("Error: attempted to set info and radius for leaf node " + this.number + " (" + this.name + ")");
    }
    return pidic;
}

TreeNode.prototype.rightmostChild = function() {
    let child = this.lchild;
    while (child.rsib != null)
        child = child.rsib;
    return child;
}

TreeNode.prototype.getSpeciesFromName = function() {
    let m = this.name.match(/[a-zA-Z0-9]+\^([a-zA-Z0-9]+)/);
    if (m == null) {
        throw "was expecting the taxon name (" + this.name + ") to contain the species name after a caret";
    }
    return m[1];
}

TreeNode.prototype.getAncSet = function() {
    let curr = this;
    let ancset = new Set();
    while (curr.parent) {
        curr = curr.parent;
        ancset.add(curr);
    }
    return ancset;
}

TreeNode.prototype.setDescendants = function(new_taxon) {
    // First delete all of nd's descendants from its parent (if there is a parent)
    // and add new_taxon
    if (this.parent) {
        for (let taxon of this.info.descendants) {
            // Split taxon at character '~'
            const taxon_array = taxon.split('~');
            for (const t of taxon_array)
                this.parent.info.descendants.delete(t);
        }
        this.parent.info.descendants.add(new_taxon);
    }
    //else {
    //    //temporary!
    //    console.log("********** node " + this.number + " has no parent");
    //}
    
    // Now set nd's descendants to new_taxon
    this.info.descendants = new Set();
    this.info.descendants.add(new_taxon);
}

Tree.prototype.updateMaxPIDIC = function(pidic) {
    for (var i = 0; i < 4; i++) {
        if (pidic[i] > this.maxPIDIC[i])
            this.maxPIDIC[i] = pidic[i];
    }
}

Tree.prototype.recalcLeafOrder = function() {
    let leaf_names_in_order = [];
    let nroots = this.root.length;
    for (let i = 0; i < nroots; i++) {
        let preorder_i = this.preorder[i];
        for (let j in preorder_i) {
            var nd = preorder_i[j];
            if (nd.lchild == null) {
                leaf_names_in_order.push(nd.name);
            }
        }
    }
    return leaf_names_in_order;
};

Tree.prototype.recalcHeights = function(debug = false) {
    // deprecated in favor of recalcInternalHeights, which differs only in the way the information is returned.
    // Assumes tree is ultrametric.
    // Visits nodes in postorder sequence. Each leaf node gets height = 0 and
    // internal nodes have height equal to the height of any child plus that
    // child's edge length. Returns a vector each element of which is itself
    // a vector of length 2 containing the height followed by the node. Only
    // internal nodes are recorded as the height of each leaf node is zero.
    let node_heights = [];
    let nroots = this.root.length;
    for (let i = 0; i < nroots; i++) {
        let preorder_i = this.preorder[i];
        let n = preorder_i.length;
        for (let j = n-1; j >= 0; j--) {
            let nd = preorder_i[j];

            if (debug) {
                console.log("visiting node number " + nd.number + ", edgelen = " + nd.edgelen.toFixed(5));
                if (nd.parent)
                    console.log("  parent " + nd.parent.number);
                if (nd.lchild) {
                    console.log("  lchild " + nd.lchild.number);
                    console.log("  rchild " + nd.lchild.rsib.number);
                }
            }

            if (nd.lchild == null) {
                nd.height = 0.0;
            }
            if (nd.parent) {
                //if (nd.parent.number == 12) {
                //    console.log("at nd.parent.number == 12");                
                //}
                //console.log("|> nd.number                         = " + nd.number);
                //console.log("|> nd.parent.number                  = " + nd.parent.number);
                //console.log("|> nd.parent.lchild.number           = " + nd.parent.lchild.number);
                //console.log("|> nd.parent.rightmostChild().number = " + nd.parent.rightmostChild().number);
                if (nd == nd.parent.rightmostChild()) {
                    nd.parent.height = nd.height + nd.edgelen;
                    node_heights.push([nd.parent.height, nd.parent]);
                }
                else {
                    //console.log("node " + nd.parent.number + " height (" + nd.parent.height.toFixed(5) + ") did not equal expected height (" + (nd.height + nd.edgelen).toFixed(5) + ")")
                    if (Math.abs(nd.parent.height - (nd.height + nd.edgelen)) > .0001) {
                        throw "node " + nd.parent.number + " height (" + nd.parent.height.toFixed(5) + ") did not equal expected height (" + (nd.height + nd.edgelen).toFixed(5) + ")";
                    }
                }
            }
        }
    }
    return node_heights;
}

Tree.prototype.recalcInternalHeights = function(debug = false) {
    // Same as recalcHeights except for the nature of the return value.
    // Assumes tree is ultrametric.
    // Returns a vector of objects from the gene tree, e.g.
    //
    // node_heights = [
    //    {height: 2,  node: nd18}, 
    //    {height: 4,  node: nd16}, 
    //    {height: 6,  node: nd13}, 
    //    {height: 8,  node: nd14}, 
    //    {height: 10, node: nd17}, 
    //    {height: 14, node: nd15}, 
    //    {height: 16, node: nd12}, 
    //    {height: 18, node: nd11}, 
    //    {height: 20, node: nd10}
    // ]
    // Visits nodes in postorder sequence. Each leaf node gets height = 0 and
    // internal nodes have height equal to the height of any child plus that
    // child's edge length. Only internal node heights are returned.
    let node_heights = [];
    let nroots = this.root.length;
    for (let i = 0; i < nroots; i++) {
        let preorder_i = this.preorder[i];
        let n = preorder_i.length;
        for (let j = n-1; j >= 0; j--) {
            let nd = preorder_i[j];

            if (debug) {
                console.log("visiting node number " + nd.number + ", edgelen = " + nd.edgelen.toFixed(5));
                if (nd.parent)
                    console.log("  parent " + nd.parent.number);
                if (nd.lchild) {
                    console.log("  lchild " + nd.lchild.number);
                    console.log("  rchild " + nd.lchild.rsib.number);
                }
            }

            if (nd.lchild == null) {
                nd.height = 0.0;
            }
            if (nd.parent) {
                //if (nd.parent.number == 12) {
                //    console.log("at nd.parent.number == 12");                
                //}
                //console.log("|> nd.number                         = " + nd.number);
                //console.log("|> nd.parent.number                  = " + nd.parent.number);
                //console.log("|> nd.parent.lchild.number           = " + nd.parent.lchild.number);
                //console.log("|> nd.parent.rightmostChild().number = " + nd.parent.rightmostChild().number);
                if (nd == nd.parent.rightmostChild()) {
                    nd.parent.height = nd.height + nd.edgelen;
                    node_heights.push({height:nd.parent.height, node:nd.parent});
                }
                else {
                    //console.log("node " + nd.parent.number + " height (" + nd.parent.height.toFixed(5) + ") did not equal expected height (" + (nd.height + nd.edgelen).toFixed(5) + ")")
                    if (Math.abs(nd.parent.height - (nd.height + nd.edgelen)) > .0001) {
                        throw "node " + nd.parent.number + " height (" + nd.parent.height.toFixed(5) + ") did not equal expected height (" + (nd.height + nd.edgelen).toFixed(5) + ")";
                    }
                }
            }
        }
    }
    return node_heights;
}

Tree.prototype.storeDescendants = function() {
    let debugging = false;
    // Combine with recalcHeights?
    // Assumes tree is ultrametric.
    // Visits nodes in postorder sequences, setting each node's info
    // attribute to an object with a key "descendants" containing a 
    // set of all descendant species names 
    let nroots = this.root.length;
    if (debugging)
        console.log("#####  storeDescendants (" + nroots + " root" + (nroots == 1 ? "" : "s") + ") #####");
    for (let i = 0; i < nroots; i++) {
        let preorder_i = this.preorder[i];
        let n = preorder_i.length;
        for (let j = n-1; j >= 0; j--) {
            let nd = preorder_i[j];
            if (nd.lchild == null) {
                // leaf node
                let s = new Set();
                s.add(nd.name);
                nd.info = {descendants:s};
                if (debugging) {
                    console.log("### leaf: number " + nd.number + " (" + nd.name + ")")
                    console.log(nd.info.descendants)
                }
            }
            else {
                // internal node
                if (debugging) {
                    console.log("### internal: number " + nd.number + " (" + nd.name + ")")
                    console.log(nd.info.descendants)
                }
            }
            if (nd.parent) {
                if (nd == nd.parent.rightmostChild()) {
                    nd.parent.info = {descendants:new Set()};
                    for (const elem of nd.info.descendants) {
                        nd.parent.info.descendants.add(elem);
                    }
                }
                else {
                    for (const elem of nd.info.descendants) {
                        nd.parent.info.descendants.add(elem);
                    }
                }
            }
        }
    }
}

Tree.prototype.recalcValleyDepths = function() {
    // Visits leaves in preorder sequence, computing (for each leaf except the last)
    // the depth of the valley separating that leaf from the next one
    // Returns vector of valley depths that has one fewer element than vector returned
    // by recalcLeafOrder function
    let valley_depths = [];
    let curr = null;
    let next = null;
    let curr_ancestors = null;
    let next_ancestors = null;
    this.recalcHeights();
    let nroots = this.root.length;
    for (let i = 0; i < nroots; i++) {
        let preorder_i = this.preorder[i];
        for (let j in preorder_i) {
            let nd = preorder_i[j];
            if (nd.lchild == null) {
                // Only consider leaf nodes (species) and gnore internal nodes
                if (curr == null && next == null) {
                    // Sitting at first leaf node
                    curr = nd;
                    curr_ancestors = curr.getAncSet();
                }
                else if (next == null) {
                    // Sitting at second leaf npde
                    next = nd;
                    next_ancestors = next.getAncSet();
                }
                else {
                    // Beyond second leaf node
                    curr = next;
                    curr_ancestors = next_ancestors;
                    next = nd;
                    next_ancestors = next.getAncSet();
                }
            
                if (curr != null && next != null) {
                    // Find valley separating species curr and species next
                    let mrca = null;
                    for (let elem of curr_ancestors) {
                        if (next_ancestors.has(elem)) {
                            if (mrca == null || elem.height < mrca.height) {
                                mrca = elem;
                            }
                        }
                    }
                    if (mrca == null) {
                        // Tree not completely constructed yet, so let valley depth
                        // be the total height of subtree i
                        if (i == 0)
                                throw "I don't understand why i == 0 here; should have an MRCA unless straddling subtrees";
                        let rooti = this.root[i];
                        let hi = rooti.height + rooti.edgelen;
                        let rootii = this.root[i-1];
                        let hii = rootii.height + rootii.edgelen;
                        if (Math.abs(hi - hii) > 0.0001)
                            throw "height of subtree " + (i-1) + " (" + hii.toFixed(5) + ") should be same as height of subtree " + i + " (" + hi.toFixed(5) + ")";
                        valley_depths.push(hi);
                    }
                    else {
                        // mrca exists, so record its depth as the barrier between
                        // species curr and species next
                        valley_depths.push(mrca.height);
                    }
                }
            }
        }
    }
    return valley_depths;
}

Tree.prototype.rebuildPreorder = function(msg = "") {
    this.preorder = [];
    let nroots = this.root.length;
    for (let i = 0; i < nroots; i++) {
        let preorder_i = [this.root[i]];
        let num_nodes = this.nleaves;
        nd = this.root[i];
        while (nd) {
            if (nd.parent) {
                preorder_i.push(nd);
            }

            if (nd.lchild != null) {
                // internal node
                nd.number = num_nodes;
                num_nodes += 1;

                // let name be concatenation of all child names
                let l = nd.lchild;
                nd.name = l.name;
                for (l = l.rsib; l != null; l = l.rsib) {
                    nd.name += "|" + l.name;
                }
            
                nd = nd.lchild;
            }
            else {
                // leaf node
                while (nd && !nd.rsib)
                    nd = nd.parent;
                if (nd)
                    nd = nd.rsib;
            }
        }
        this.preorder.push(preorder_i);
    }
    
    let debugging = true;
    if (debugging) {
        console.log("\n*** rebuildPreorder " + msg + "***");
        for (let i in this.preorder) {
            const which = Number(i) + 1;
            console.log("lineage " + which + ":");
            for (let nd of this.preorder[i]) {
                if (nd.lchild != null) {
                    // internal node
                    console.log("  internal node number = " + nd.number);
                    console.log("    lchild number = " + nd.lchild.number);
                    console.log("    rchild number = " + nd.lchild.rsib.number);
                } else {
                    // leaf node
                    console.log("  leaf node number = " + nd.number);
                }
            }
        }
    }        
}

Tree.prototype.buildFromNewick = function(translate, newick) {
    const verbose = false;
    if (verbose)
        console.log("entering buildFromNewick");

    var nd = new TreeNode();
    if (verbose)
        console.log("~~> creating new node to be first root node");
    this.root.push(nd);
    this.nleaves = 0;

    var Prev_Tok = {
        LParen:0x01,	// previous token was a left parenthesis ('(')
        RParen:0x02,	// previous token was a right parenthesis (')')
        Colon:0x04,	    // previous token was a colon (':')
        Comma:0x08,	    // previous token was a comma (',')
        Name:0x10,	    // previous token was a node name (e.g. '2', 'P._articulata')
        EdgeLen:0x20	// previous token was an edge length (e.g. '0.1', '1.7e-3')
    }
    var previous = Prev_Tok.LParen;

    // Some useful flag combinations
    var LParen_Valid = (Prev_Tok.LParen | Prev_Tok.Comma);
    var RParen_Valid = (Prev_Tok.RParen | Prev_Tok.Name | Prev_Tok.EdgeLen);
    var Comma_Valid  = (Prev_Tok.RParen | Prev_Tok.Name | Prev_Tok.EdgeLen);
    var Colon_Valid  = (Prev_Tok.RParen | Prev_Tok.Name);
    var Name_Valid   = (Prev_Tok.RParen | Prev_Tok.LParen | Prev_Tok.Comma);

    if (verbose) {
        console.log("LParen       = " + Prev_Tok.LParen);
        console.log("RParen       = " + Prev_Tok.RParen);
        console.log("Colon        = " + Prev_Tok.Colon);
        console.log("Comma        = " + Prev_Tok.Comma);
        console.log("Name         = " + Prev_Tok.Name);
        console.log("EdgeLen      = " + Prev_Tok.EdgeLen);
        console.log("LParen_Valid = " + LParen_Valid);
        console.log("RParen_Valid = " + RParen_Valid);
        console.log("Comma_Valid  = " + Comma_Valid);
        console.log("Colon_Valid  = " + Colon_Valid);
        console.log("Name_Valid   = " + Name_Valid);
        console.log("\nnewick = " + newick);
    }

    // loop through the characters in newick, building up tree as we go
    for (var c = 0; c < newick.length; c++)
        {
        var ch = newick[c];
        if (verbose)
            console.log("next character: ch = \'" + ch + "\'");
        if (/\s/.test(ch))
            continue;
        switch(ch)
            {
            case ';':
                if (verbose)
                    console.log("~~> semicolon"); // temporary
                break;

            case ')':
                if (verbose)
                    console.log("~~> right parenthesis"); // temporary

                // If nd is bottommost node, expecting left paren or semicolon, but not right paren
                if (!nd.parent)
                    console.log("Too many right parentheses at position " + c + " in tree description");

                // Expect right paren only after an edge length, a node name, or another right paren
                if (!(previous & RParen_Valid))
                    console.log("Unexpected right parenthesisat position " + c + " in tree description");

                // Go down a level
                if (nd.parent) {
                    nd = nd.parent;
                    if (!nd.lchild.rsib)
                        console.log("Internal node has only one child at position " + c + " in tree description");
                }
                else {
                    if (verbose)
                        console.log("*** nd.parent was null");
                }
                previous = Prev_Tok.RParen;
                break;

            case ':':
                // Expect colon only after a node name or another right paren
                if (!(previous & Colon_Valid))
                    console.log("Unexpected colon at position " + c + " in tree description");
                previous = Prev_Tok.Colon;
                break;

            case ',':
                // Expect comma only after an edge length, a node name, or a right paren
                if (!(previous & Comma_Valid)) {
                    console.log("Unexpected comma at position " + c + " in tree description (previous = " + previous + ")");
                }
                
                if (!nd.parent) {
                    // Create a new subtree root node
                    var subtree_root = new TreeNode();
                    if (verbose)
                        console.log("~~> creating new node to be root of another subtree");
                    this.root.push(subtree_root);
                    nd = subtree_root;
                    previous = Prev_Tok.LParen; // fake being at the start of tree description
                }
                else {
                    // Create the sibling
                    nd.rsib = new TreeNode();
                    if (verbose)
                        console.log("~~> creating new node to be rsib of current node");
                    nd.rsib.parent = nd.parent;
                    nd = nd.rsib;
                    previous = Prev_Tok.Comma;
                }
                break;

            case '(':
                if (verbose)
                    console.log("~~> left parenthesis"); // temporary
                // Expect left paren only after a comma or another left paren
                if (!(previous & LParen_Valid))
                    console.log("Not expecting left parenthesis at position " + c + " in tree description");

                // Create new node above and to the left of the current node
                nd.lchild = new TreeNode();
                if (verbose)
                    console.log("~~> creating new node to be lchild of current node");
                nd.lchild.parent = nd;
                nd = nd.lchild;
                previous = Prev_Tok.LParen;
                break;

            case "'":
            case "\"":
                // Encountered an apostrophe, which always indicates the start of a
                // node name (but note that node names do not have to be quoted)

                // Expect node name only after a left paren (child's name), a comma (sib's name)
                // or a right paren (parent's name)
                if (!(previous & Name_Valid))
                    console.log("Not expecting node name at position " + c + " in tree description");

                // Get the rest of the name
                for (c++; c < newick.length; c++)
                    {
                    ch = newick[c];
                    if (ch == '\'' || ch == '\"')
                        break;
                    else if (/\s/.test(ch))
                        nd.name += ' ';
                    else
                        nd.name += ch;
                    }
                if (ch != "'" && ch != "\"")
                    console.log("Expecting single quote to mark the end of node name at position " + c + " in tree description");

                if (nd.lchild == null) {
                    nd.number = Number(nd.name) - 1;
                    this.nleaves += 1;

                    // translate number to taxon name
                    var translated = translate[nd.name];
                    if (translated !== undefined) {
                        nd.name = translated;
                        }
                    }
                if (verbose)
                    console.log("~~> nd.name (quoted) = " + nd.name + ", ch = " + ch); // temporary

                previous = Prev_Tok.Name;
                break;

            default:
                // Expecting either an edge length or an unquoted node name
                if (previous == Prev_Tok.Colon)
                    {
                    if (verbose)
                        console.log("~~> default (after colon)"); // temporary
                    // Edge length expected (e.g. "235", "0.12345", "1.7e-3")
                    var edge_length_str = "";
                    for (; c < newick.length; c++)
                        {
                        ch = newick[c];
                        if (ch == ',' || ch == ')' || /\s/.test(ch))
                            break;
                        var valid = (ch =='e' || ch == 'E' || ch =='.' || ch == '-' || ch == '+' || /\d/.test(ch));
                        if (valid)
                            edge_length_str += ch;
                        else
                            console.log("Invalid branch length character (" + ch + ") at position " + c + " in tree description");
                        }
                    c--;
                    nd.edgelen = Number(edge_length_str);
                    if (nd.edgelen < 1.e-10)
                        nd.edgelen = 1.e-10;

                    previous = Prev_Tok.EdgeLen;
                    }
                else
                    {
                    if (verbose)
                        console.log("~~> default (not after colon)"); // temporary
                    // Get the node name
                    nd.name = "";
                    for (; c < newick.length; c++)
                        {
                        ch = newick[c];
                        if (ch == '(')
                            console.log("Unexpected left parenthesis inside node name at position " + c + " in tree description");
                        if (/\s/.test(ch) || ch == ':' || ch == ',' || ch == ')')
                            break;
                        nd.name += ch;
                        }
                    c--;

                    // Expect node name only after a left paren (child's name), a comma (sib's name) or a right paren (parent's name)
                    if (!(previous & Name_Valid))
                        console.log("Unexpected node name (" + nd.name + ") at position " + c + " in tree description");

                    if (nd.lchild == null) {
                        nd.number = Number(nd.name) - 1;
                        this.nleaves += 1;

                        if (verbose)
                            console.log("~~> nd.name in newick = " + nd.name + ", nd.number = " + nd.number); // temporary

                        var translated = translate[nd.name];
                        if (translated !== undefined) {
                            nd.name = translated;
                            }
                        }
                    if (verbose)
                        console.log("~~> nd.name (unquoted) = " + nd.name + ", ch = " + ch); // temporary

                    previous = Prev_Tok.Name;
                    }
            }
            if (c == newick.length-1)
                break;
        }   // loop over characters in newick string


    this.rebuildPreorder("buildFromNewick");
    
    if (false) {
        // Build preorder arrays
        let nroots = this.root.length;
        for (let i = 0; i < nroots; i++) {
            let preorder_i = [this.root[i]];
            let num_nodes = this.nleaves;
            nd = this.root[i];
            while (nd) {
                if (nd.parent) {
                    preorder_i.push(nd);
                }

                if (nd.lchild != null) {
                    // internal node
                    nd.number = num_nodes;
                    num_nodes += 1;

                    // let name be concatenation of all child names
                    let l = nd.lchild;
                    nd.name = l.name;
                    for (l = l.rsib; l != null; l = l.rsib) {
                        nd.name += "|" + l.name;
                    }
            
                    nd = nd.lchild;
                }
                else {
                    // leaf node
                    while (nd && !nd.rsib)
                        nd = nd.parent;
                    if (nd)
                        nd = nd.rsib;
                }
            }
            this.preorder.push(preorder_i);
        }
    }
    
    if (verbose)
        console.log("leaving buildFromNewick");
}

Tree.prototype.checkForValueInArray = function(val, arr, tol) {
    for (let i = 0; i < arr.length; i++) {
        if (Math.abs(arr[i] - val) < tol) 
            return true;
    }
    return false;
}

Tree.prototype.setNodeXY = function(relrate, leaf_order) {
    // leaf_order takes nd.number as index and returns 0-offset order
    const verbose = false;

    if (verbose) {
        console.log("");
        console.log("setNodeXY:");
    }
    
    // yused will hold y values already used so that internal nodes
    // get jiggered if they are directly lined up with a node higher up
    let yused = [];
    
    // Set x coordinate of each node
    let nd = this.root;
    nd.x = 0.0;
    nd.y = 0.0;
    this.xmax = 0.0;
    let nroots = this.root.length;
    for (let i = 0; i < nroots; i++) {
        let preorder_i = this.preorder[i];
        for (let j in preorder_i) {
            nd = preorder_i[j];
            nd.x = nd.edgelen/relrate;
            nd.y = 0.0;
            if (nd.lchild == null) {
                // leaf node (no children)
                nd.y = 2*leaf_order[nd.number];
                yused.push(nd.y);
            }
            if (nd.parent != null)
                nd.x += nd.parent.x;
            if (nd.x > this.xmax)
                this.xmax = nd.x;
            if (verbose) {
                console.log("------------------------");
                if (nd.lchild == null) {
                    console.log("leaf node:");
                } else {
                    console.log("internal node:");
                }
                console.log("  nd.name    = " + nd.name);
                console.log("  nd.number  = " + nd.number);
                console.log("  nd.edgelen = " + nd.edgelen);
                console.log("  nd.x       = " + nd.x);
                console.log("  nd.y       = " + nd.y);
                console.log("  xmax       = " + this.xmax);
                if (nd.parent == null) {
                    console.log("  no parent");
                } else {
                    console.log("  parent.number = " + nd.parent.number);
                }
            }
        }
    }

    // Set y coordinate of internal nodes to be average y coordinate of its children
    this.ymax = 0.0;
    for (let i = 0; i < nroots; i++) {
        let preorder_i = this.preorder[i];
        for (j = preorder_i.length - 1; j >= 0; j--) {
            nd = preorder_i[j];
            if (nd.lchild != null) {
                // internal node (has children)
                nd.y /= 2;
                if (this.checkForValueInArray(nd.y, yused, 0.01)) {
                    // choose random jigger value between -0.5 and +0.5
                    let jigger_value = Math.random() - 0.5;
                
                    // push jiggered value away from current value by at least 0.25
                    if (jigger_value < 0.0)
                        jigger_value -= 0.25;
                    else
                        jigger_value += 0.25;
                    
                    if (verbose) {
                        console.log("  jiggering " + nd.name + " from " + nd.y + " to " + (nd.y + jigger_value));
                    }
                
                    // add the jigger value
                    nd.y += jigger_value;
                }
                yused.push(nd.y);
            }

            if (nd.parent) {
                // update parent's y value
                nd.parent.y += nd.y;
             }

            if (nd.y > this.ymax)
                this.ymax = nd.y;
        }
    }
    
    if (verbose) {
        for (let i = 0; i < nroots; i++) {
            let preorder_i = this.preorder[i];
            for (let j in preorder_i) {
                nd = preorder_i[j];
                console.log("  name = " + nd.name + ", x = " + nd.x + ", y = " + nd.y);
            }
        }
    }
    
    return {xmax:this.xmax, ymax:this.ymax};
}

Tree.prototype.addTreeLines = function(gene_name, linedata, add_root_edge = false) {
    // Create a polyline starting at a node and going left to the level of the parent
    // and then up or down to the parent. If add_root_edge is not null, then
    // draw line from root of each subtree left for a distance equal to the root's edge length.
    const verbose = false;
    
    if (verbose) {
        console.log("");
        console.log("addTreeLines for gene " + gene_name + ":");
    }

    let k = 0;
    let nroots = this.root.length;
    for (let i = 0; i < nroots; i++) {
        let preorder_i = this.preorder[i];
        for (let j = 0; j < preorder_i.length; j++) {
            let d = preorder_i[j];
            let polyline = [];
            if (d.parent != null) {
                // start at node itself
                polyline.push({x:d.x, y:d.y});

                // go straight back to parent's level
                polyline.push({x:d.parent.x, y:d.y});

                // now up or down to parent's node
                polyline.push({x:d.parent.x, y:d.parent.y});

                // save polyline data for one node
                k++;
                let edge_name = "edge-" + k.toString()
                linedata.push({
                    nodenumber:d.number,
                    nodex:d.x,
                    nodey:d.y,
                    genename:gene_name, 
                    edgename:edge_name, 
                    edgelen:d.x - d.parent.x, 
                    depth:this.xmax - d.parent.x, 
                    treeheight:this.xmax, 
                    edgelines:polyline
                });
            
                if (verbose) {
                    console.log("  number = " + d.number + ": (" + d.x + "," + d.y + ") back to (" + d.parent.x + "," + d.y + ") up/down to (" + d.parent.x + "," + d.parent.y + ")")
                    console.log("    --> treeheight = " + this.xmax.toFixed(6))
                    console.log("    --> start   = " + d.parent.x.toFixed(6))
                    console.log("    --> finish  = " + d.x.toFixed(6))
                    console.log("    --> edgelen = " + Number(d.x - d.parent.x).toFixed(6))
                }
            }
        }
        
        // Draw line from root back (left) for a distance equal to the root's edge length
        if (add_root_edge) {
            let polyline = [];
            
            // get ith root node
            let root_i = this.root[i];

            // start at root node itself
            polyline.push({x:root_i.x, y:root_i.y});
            
            // go straight back (left) to end of barrier
            polyline.push({x:root_i.x - root_i.edgelen, y:root_i.y});
            
            k++;
            let edge_name = "edge-" + k.toString()
            linedata.push({
                nodenumber:root_i.number,
                nodex:root_i.x,
                nodey:root_i.y,
                genename:gene_name, 
                edgename:edge_name, 
                edgelen:root_i.edgelen, 
                depth:this.xmax - root_i.x - root_i.edgelen, 
                treeheight:this.xmax, 
                edgelines:polyline
            });
        }
    }
}

Tree.prototype.calcOrderScore = function(sset, sorder) {
    // sorder is a vector holding the species names in the preorder sequence from the species tree
    // sset is a set of species names (parsimony state set at a node)
    // Assume sorder = ['s0','s1','s2']
    // Suppose left child has sset = ['s0']
    //   Consider each element of sset in turn and record that element's index in sorder:
    //          score  = 0, n = 0
    //    's0': score += 0, n = 1
    //   Returns score/n = 0/1 = 0.0
    // Suppose right child has sset = ['s1','s2']
    //   Consider each element of sset in turn and record that element's index in sorder:
    //          score  = 0, n = 0
    //    's1': score += 1, n = 1
    //    's2': score += 2, n = 2
    //   Returns score/n = 2/2 = 1.0
    // No swap needed because score for left child < score for right child
    let score = 0.0;
    let n = 0;
    for (let s of sset) {
        for (let j = 0; j < sorder.length; j++) {
            if (s == sorder[j]) {
                score += j;
                n++;
                break;   
            }
        }
    }
    if (n > 0)
        return score/n;
    throw "no elements of sset found in sorder in calcOrderScore";
}

Tree.prototype.getSpeciesSet = function() {
    let species_set = [];
    let nroots = this.root.length;
    for (let i = 0; i < nroots; i++) {
        let preorder_i = this.preorder[i];
        let n = preorder_i.length;
        for (let j = 0; j < n; j++) {
            let d = this.preorder[j];
            let s = "|";
            for (let elem of d.info) {
                s += elem + "|";
            }
            species_set.push({x:d.x, y:d.y, info:s});
        }
    }
    return species_set;
}

Tree.prototype.calcSpeciesMapAtLeaves = function(species_names) {
    let species_map = {};
    let nroots = this.root.length;
    for (let i = 0; i < nroots; i++) {
        let preorder_i = this.preorder[i];
        let n = preorder_i.length;
        for (let j = 0; j < n; j++) {
            let nd = preorder_i[j];
            if (!nd.lchild) {
                // This is a leaf node
                
                // Extract species name from taxon name
                const s = nd.getSpeciesFromName();
                
                // Find index of s in species_names
                const k = species_names.findIndex((nm) => nm == s);
                
                if (k in species_map)
                    species_map[k].push(nd);
                else
                    species_map[k]= [nd];
            }
        }
    }
    
    const debugging = false;
    if (debugging) {
        console.log("object being returned from calcSpeciesMapAtLeaves:");
        console.log(species_map);
    }
    
    return species_map;
}

Tree.prototype.listSpeciesJoins = function(species_names) {
    let debugging = false;
    
    // Should be called only for species tree, which is assumed to be ultrametric and fully dichotomous.
    // The return value is an object with keys "names" and "joins". The names attribute is an array
    // that is a copy of species_names with ancestral species appended. The joins attribute is a vector 
    // of objects specifying the height at which pairs of species join in the species tree and 
    // which species (indices) are joined: e.g.
    //
    // species_joins = [
    //          {height: 10.5, ancspecies:5, speciesjoins:[0,4]},
    //          {height: 11,   ancspecies:6, speciesjoins:[1,3]},
    //          {height: 12,   ancspecies:7, speciesjoins:[5,6]},
    //          {height: 13,   ancspecies:8, speciesjoins:[2,7]}
    //      ]
    // height is the distance from leaf level to the end of the barrier;
    // anc is the index of the node formed by the join; and
    // joins provides the indices (into the names array) of the pair of species joined.
    
    let all_names = [...species_names];
    
    // node_heights = [
    //    {height: 2,  node: nd18}, 
    //    {height: 4,  node: nd16}, 
    //    {height: 6,  node: nd13}, 
    //    {height: 8,  node: nd14}, 
    //    {height: 10, node: nd17}, 
    //    {height: 14, node: nd15}, 
    //    {height: 16, node: nd12}, 
    //    {height: 18, node: nd11}, 
    //    {height: 20, node: nd10}
    // ]
    let node_heights = this.recalcInternalHeights();
    node_heights.sort(compareHeights);
    let species_joins = [];
    let k = all_names.length;
    for (let i = 0; i < node_heights.length; i++) {
        const h = node_heights[i].height;
        const nd = node_heights[i].node;
        
        // Build joins array comprising indices (into all_names array) of left and right children
        const kleft = all_names.findIndex((nm) => nm == nd.lchild.name);
        const kright = all_names.findIndex((nm) => nm == nd.lchild.rsib.name);
        
        // Name this internal node and add to all_names array
        nd.name = "anc" + k++;
        all_names.push(nd.name);
        const kanc = all_names.length - 1;
        const kanc_check = all_names.findIndex((nm) => nm == nd.name);
        if (kanc != kanc_check) {
            throw "expecting kanc (" + kanc + ") to equal " + kanc_check;
        }
        
        species_joins.push({height:h, ancspecies:kanc, speciesjoins:[kleft, kright]});
    }
        
    return {names:all_names, joins:species_joins};
}

Tree.prototype.coalescentLikelihood = function(species_names, species_joins, theta) {
    const verbose = true;
    
    // Assumes this is an ultrametric gene tree that has no polytomies.
    //
    // The argument species_names should be a list of species names, including ancestral species: e.g.
    //
    // species_names = ["s2", "s1", "s3", "s0", "s4", "anc5", "anc6", "anc7", "anc8"]
    //
    // The argument species_joins should be a vector of objects specifying the height
    // at which pairs of species join in the species tree and which species (indices) are joined: e.g.
    //
    // species_joins = [
    //          {height: 10.5, ancspecies:5, speciesjoins:[0,4]},
    //          {height: 11,   ancspecies:6, speciesjoins:[1,3]},
    //          {height: 12,   ancspecies:7, speciesjoins:[5,6]},
    //          {height: 13,   ancspecies:8, speciesjoins:[2,7]}
    //      ]
    // height is the distance from leaf level to the end of the barrier;
    // ancspecies is the index of the node formed by the join; and
    // speciesjoins is the pair of species joined
    
    // recalcInternalHeights returns a vector of objects from the gene tree, e.g.
    //
    // node_heights = [
    //    {height: 2,  node: nd18}, 
    //    {height: 4,  node: nd16}, 
    //    {height: 6,  node: nd13}, 
    //    {height: 8,  node: nd14}, 
    //    {height: 10, node: nd17}, 
    //    {height: 14, node: nd15}, 
    //    {height: 16, node: nd12}, 
    //    {height: 18, node: nd11}, 
    //    {height: 20, node: nd10}
    // ]
    //
    // Create the vector epochinfo that combines species_joins and node_heights, 
    // sorted by height. The log coalescent likelihood is computed for each epoch
    // and summed. Epochs in which node is not null represent coalescent events.
    // e.g. epochinfo = [
    //    {height: 2,    prevheight: 0,    node: nd18, ancspecies: null, speciesjoins: null }, 
    //    {height: 4,    prevheight: 2,    node: nd16, ancspecies: null, speciesjoins: null }, 
    //    {height: 6,    prevheight: 4,    node: nd13, ancspecies: null, speciesjoins: null }, 
    //    {height: 8,    prevheight: 6,    node: nd14, ancspecies: null, speciesjoins: null }, 
    //    {height: 10,   prevheight: 8,    node: nd17, ancspecies: null, speciesjoins: null }, 
    //    {height: 10.5, prevheight: 10,   node: null, ancspecies: 5,    speciesjoins: [0,4]},
    //    {height: 11,   prevheight: 10.5, node: null, ancspecies: 6,    speciesjoins: [1,3]},
    //    {height: 12,   prevheight: 11,   node: null, ancspecies: 7,    speciesjoins: [5,6]},
    //    {height: 13,   prevheight: 12,   node: null, ancspecies: 8,    speciesjoins: [2,7]},
    //    {height: 14,   prevheight: 13,   node: nd15, ancspecies: null, speciesjoins: null }, 
    //    {height: 16,   prevheight: 14,   node: nd12, ancspecies: null, speciesjoins: null }, 
    //    {height: 18,   prevheight: 16,   node: nd11, ancspecies: null, speciesjoins: null }, 
    //    {height: 20,   prevheight: 18,   node: nd10, ancspecies: null, speciesjoins: null }
    // ]
    // 
    // Determine heights of each of the internal nodes in this gene tree.
    let node_heights = this.recalcInternalHeights();
    
    let epochinfo = [];
    for (const x of species_joins) {
        epochinfo.push({height:x.height, prevheight:0.0, node:null, ancspecies:x.ancspecies, speciesjoins:x.speciesjoins, coallike:0.0});
    }
    for (const x of node_heights) {
        epochinfo.push({height:x.height, prevheight:0.0, node:x.node, ancspecies:null, speciesjoins:null, coallike:0.0});
    }
    epochinfo.sort(compareHeights);
    
    // Compute prevheight attributes now that epochinfo has been sorted
    let hprev = 0.0;
    for (const x of epochinfo) {
        x.prevheight = hprev;
        hprev = x.height;
    }
    
    // Create a species map from the taxon names at the leaves of the gene tree
    let species_map = this.calcSpeciesMapAtLeaves(species_names);
    //console.log(species_map);
    
    // Visit each epoch computing log coalescent likelihood as we go
    
    if (verbose)
        console.log("\n[##### COMPUTING COALESCENT LIKELIHOOD #####]");
    let log_coalescent_likelihood = 0.0;
    for (const i in epochinfo) {
        let epoch = epochinfo[i];
        let logpr = 0.0;
        const t = epoch.height - epoch.prevheight;
        if (verbose) {
            console.log("__________________________________________________");
            console.log("epoch = " + i + ", t = " + t.toFixed(9));
        }
        if (epoch.node) {
            // one coalescent event took place in this epoch
            let coalescent_event_found = false;
            
            if (verbose) {
                console.log("  node = " + epoch.node.number);
                console.log("    lchild = " + epoch.node.lchild.number + (epoch.node.lchild.lchild ? "" : " (" + epoch.node.lchild.name + ")"));
                console.log("    rchild = " + epoch.node.lchild.rsib.number + (epoch.node.lchild.rsib.lchild ? "" : " (" + epoch.node.lchild.rsib.name + ")"));
                //console.log("    logpr before = " + logpr.toFixed(8));
            }
            
            // Loop over species
            for (let j in species_map) {
                let curr_species = species_map[j];

                if (verbose) {
                    console.log("  considering species " + j + " (n = " + curr_species.length + ")");
                    for (const s of curr_species)
                        console.log("    s = " + s.number);
                }

                // Get the number of lineages for this species
                const n = curr_species.length;
                
                // Probability of no coalescence over time t
                logpr -= n*(n-1)*t/theta;
                //console.log("  logpr after no coal over time " + t.toFixed(8) + " = " + logpr.toFixed(8));
                
                if (Object.values(curr_species).includes(epoch.node.lchild)) {
                    // Coalescent event took place in curr_species
                    coalescent_event_found = true;
                    
                    if (Object.values(curr_species).includes(epoch.node.lchild.rsib)) {
                        if (verbose)
                            console.log("    *** found lineages that coalesced ***");
                        
                        // Probability of choosing the two lineages that coalesced
                        logpr -= Math.log(n*(n-1)/2);
                        //console.log("  logpr after 1/{n choose 2} = " + logpr.toFixed(8));
                
                        // Probability density of coalescence event
                        logpr += Math.log(n*(n-1)/theta);
                        //console.log("  logpr after coal event = " + logpr.toFixed(8));
                        
                        // Replace lchild and rchild of epoch.node with epoch.node in curr_species
                        let indices_to_delete = [];
                        for (const s in curr_species) {
                            if (curr_species[s] == epoch.node.lchild || curr_species[s] == epoch.node.lchild.rsib)
                                indices_to_delete.push(s);
                        }
                        indices_to_delete.sort();
                        indices_to_delete.reverse();
                        for (const z of indices_to_delete) {
                            curr_species.splice(z, 1);
                        } 
                        curr_species.push(epoch.node);
                    }
                    else
                        throw "expecting both children of node " + epoch.node.number + "(" + epoch.node.name + ") to be in the same species (" + i + ")";
                }
            }
            if (!coalescent_event_found)
                throw "expecting one coalescent event to be found for epoch " + i + " but there were none";
        }
        else {
            // no coalescence this epoch but there was a species merger
            // Get the number of lineages for each species
            for (let j in species_map) {
                const curr_species = species_map[j];
                const n = curr_species.length;
                if (verbose) {
                    console.log("    species " + j + " has " + n + " lineages");
                }
                logpr -= n*(n-1)*t/theta;
            }

            const anc = epoch.ancspecies;
            const joins = epoch.speciesjoins;
            species_map[anc] = [];
            if (verbose)
                console.log("  Merging species " + joins[0] + " with " + joins[1] + " to form " + anc);
            for (const j of joins) {
                // Copy all nodes in species j to anc
                for (const nd of species_map[j]) {
                    species_map[anc].push(nd);
                }
                
                // Remove species j from species_map
                delete species_map[j]                
            }
        }
        
        if (verbose)
            console.log("  logpr = " + logpr.toFixed(8));
            
        log_coalescent_likelihood += logpr;
        epoch.coallike = logpr;
    }    
    
    if (verbose) {
        console.log("__________________________________________________");
        console.log("log_coalescent_likelihood = " + log_coalescent_likelihood.toFixed(8));
    }
        
    return {logcoallike:log_coalescent_likelihood, epochs:epochinfo};
}

Tree.prototype.imposeSpeciesOrder = function(order) {
    const verbose = false;
    
    // Assumes tree has no polytomies.
    // Assumes order is a vector of species names like this: ["A","B","C","D"]
    // Assumes leaf names include the species name after a caret, like this: "xxx^A"
    // Uses parsimony to assign a species to each ancestral node, using the name attribute
    // to store the species name (e.g. "^A") and using the info attribute to store
    // state sets. It then performs a postorder traversal, swapping left and right 
    // children if they are in different species and if the species are in the wrong order.
    
    //console.log("***** order *****");
    //console.log(order);
    
    // Postorder traversal to create state sets
    let nroots = this.root.length;
    for (let i = 0; i < nroots; i++) {
        let preorder_i = this.preorder[i];
        let n = preorder_i.length;
        if (verbose)
            console.log("***** i = " + i + ", n = " + n);
        for (let j = n - 1; j >= 0; j--) {
            let d = preorder_i[j];
            if (d.lchild == null) {
                if (verbose)
                    console.log("***** " + d.name + " (" + d.number + ") is a leaf");
                d.info = new Set();
                d.info.add(d.getSpeciesFromName());
            }

            if (d.parent) {
                let left_child = d.parent.lchild;
                let right_child = left_child.rsib;
            
                if (!right_child || d == right_child)  {
                    if (verbose)
                        console.log("*****   rightmost child");
                    d.parent.info = new Set(d.info)
                }
                else {
                    if (verbose)
                        console.log("*****   not rightmost child");
                    for (let elem of d.info) {
                        d.parent.info.add(elem);
                    }
                }
            }
        }
    }
    
    // Now traverse tree and swap when necessary
    // Build vector of y positions of all leaves.
    let yvect = [];
    let leafvect = [];
    let message = "";
    for (let i = 0; i < nroots; i++) {
        let preorder_i = this.preorder[i];
        let n = preorder_i.length;
        for (let j = 0; j < n; j++) {
            let d = preorder_i[j];
            if (d.lchild) {
                // internal
                if (d.lchild.rsib) {
                    // not root node
                    let lset = d.lchild.info;
                    let lscore = this.calcOrderScore(lset, order);
                    let rset = d.lchild.rsib.info;
                    let rscore = this.calcOrderScore(rset, order);
                    if (lscore > rscore) {
                        // swap
                        let sleft = "|";
                        for (let elem of d.lchild.info) {
                            sleft += elem + "|";
                        }
                        let sright = "|";
                        for (let elem of d.lchild.rsib.info) {
                            sright += elem + "|";
                        }
                        message += "swapping left=" + sleft + " with right=" + sright + "\n";
                
                        let tmp = d.lchild;
                        d.lchild = tmp.rsib;
                        tmp.rsib = null;
                        d.lchild.rsib = tmp;
                    }
                }
            }
            else {
                // leaf node
                leafvect.push(d);
                yvect.push(d.y);
            }
        }
    }
    
    // Finally, rebuild preorder arrays
    this.rebuildPreorder("imposeSpeciesOrder");
    
    if (verbose) {
        console.log("***** message *****");    
        console.log(message);
    }
}


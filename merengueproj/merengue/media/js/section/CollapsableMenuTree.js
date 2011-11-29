(function ($) {
    var plus;
    var minus;
    var draggable;
    var draggable_disabled;
    var span15 = '<span class="span15">&nbsp;</span>';
    var span50 = '<span class="span50">&nbsp;</span>';
    var save_url = '/cms/sections/ajax/save_menu_order/';
    var painting = 0;

    function recalculateRows() {
        $('#changelist table tbody tr:visible').each(function(index) {
            $(this).removeClass('row1').removeClass('row2');
            $(this).addClass('row' + (index%2+1));
        });
    }

    function Node(element, level) {
        this.children = [];
        this.domelement = element;
        this.level = level;
        this.opened = false;
        this.expand = false;
        this.parent = null;
    }


    Node.prototype.getRoot = function() {
            if (!this.parent) return this;
            return this.parent.getRoot();
        };
    Node.prototype.getLevel = function() {
            if (!this.parent) return 0;
            return this.parent.getLevel()+1;
        };
    Node.prototype.open = function() {
            this.opened = true;
            this.paintNodes();
            recalculateRows();
        };
    Node.prototype.close = function() {
            this.closeChildren();
            this.paintNodes(true);
            recalculateRows();
        };
    Node.prototype.addChild = function(node) {
            this.children.push(node);
            node.parent = this;
        };
    Node.prototype.getChildren = function() {
            return this.children;
        };
    Node.prototype.setChildren = function(children) {
            this.children = children;
            for (var i in children) {
                children[i].parent = this;
            }
        };
    Node.prototype.findLastLevelNode = function(level, lastnode) {
            var children = this.getChildren();
            var newnode = null;
            if (this.getLevel() === level) {
                return this;
            } else if (this.getLevel() > level) {
                return lastnode
            }
            for (i in children) {
                newnode = children[i].findLastLevelNode(level, lastnode)
                lastnode = newnode
            }
            return newnode
        };
    Node.prototype.undecorate = function() {
            var element = this.domelement;
            element.find('.plusMenu,.minusMenu,.span15,.span50,.draggable-icon,.draggable-icon-disabled').remove();
        };
    Node.prototype.decorate = function() {
            var element = this.domelement;
            if (this.children.length) {
                element.children("th").eq(0).prepend(minus.clone()).prepend(plus.clone().show());
                element.children("th").eq(0).css('white-space', 'nowrap');
                element.children("th").eq(0).find('a').css('white-space', 'normal');
            } else {
                element.children("th").eq(0).prepend(span15);
            }
            for(var i=0;i<this.getLevel()-1;i++) {
                element.children("th").eq(0).prepend(span50);
            }
            if (this.parent.opened) element.show(); else element.hide();
            if (this.opened) {
                element.find(".minusMenu").show();
                element.find(".plusMenu").hide();
            } else {
                element.find(".minusMenu").hide();
                element.find(".plusMenu").show();
            }
            element.children("th").eq(0).prepend(draggable.clone().load(function(){$(this).show()}));
            element.children("th").eq(0).prepend(draggable_disabled.clone());
            if (this.expand) {
                element.find('.plusMenu').trigger('click');
                this.expand=false;
            }
        };
    Node.prototype.closeChildren = function() {
            var children = this.children;
            for (var i in children) {
                children[i].closeChildren();
            }
            this.opened = false;
        };
    Node.prototype.setListeners = function() {
            var element = this.domelement;
            var node = this;
	    element.find(".plusMenu").click(function() {
               node.open();
            });
	    element.find(".minusMenu").click(function() {
               node.close();
            });
        };
    Node.prototype.paintNode = function(moving) {
            if (typeof(moving) == 'undefined') moving = false;
            var element = this.domelement;
            if (!element) return;
            element.children('td').eq(0).hide();
            element.children('td').eq(1).hide();
            if (!moving) {
                this.undecorate();
                this.decorate();
                this.setListeners();
            } else {
            if (this.parent.opened) element.show(); else element.hide();
                if (this.opened) {
                    element.find(".minusMenu").show();
                    element.find(".plusMenu").hide();
                } else {
                    element.find(".minusMenu").hide();
                    element.find(".plusMenu").show();
                }
            }
        };
    Node.prototype.paintNodes = function(moving) {
            if (typeof(moving) == 'undefined') moving = false;
            var children = this.children;
            for (var i in children) {
                children[i].paintNodes(moving);
            }
            var node = this;
            node.paintNode(moving);
            //recalculateRows();
        };
    Node.prototype.findNodeByElement = function(element) {
            var node = null;
            if (this.domelement && this.domelement.get(0) === element.get(0)) {
                return this;
            } else { 
                var children = this.children;
                for (var i in children) { 
                    node = children[i].findNodeByElement(element);
                    if (node) return node;
                }
            }
            return null;
        };
    Node.prototype.unParent = function() {
            var siblings = this.parent.getChildren();
            var newsiblings = [];
            for (var i in siblings) {
                if (siblings[i] !== this) newsiblings.push(siblings[i]);
            }
            this.parent.setChildren(newsiblings);
        };
    Node.prototype.moveLastChild = function(node) {
            this.unParent();
            node.addChild(this);
        };
    Node.prototype.moveFirstChild = function(node) {
            this.unParent();
            this.parent = node;
            var siblings = this.parent.getChildren();
            var newsiblings = [];
            newsiblings.push(this);
            for (var i in siblings) {
                newsiblings.push(siblings[i]);
            }
            this.parent.setChildren(newsiblings);
        };
    Node.prototype.moveAfterWithLevel = function(node, level, recurse) {
            if (node.getLevel() < level) {
                this.unParent();
                node.addChild(this);
                node.expand=true;
            } else if (node.getLevel() === level) {
                this.moveAfter(node);
            } else if (recurse) {
                this.moveAfterWithLevel(node.parent, level, recurse);
            } else {
                this.moveAfter(node);
            }
        };
    Node.prototype.moveAfter = function(node) {
            this.unParent();
            this.parent = node.parent;
            var siblings = this.parent.getChildren();
            var newsiblings = [];
            for (var i in siblings) {
                newsiblings.push(siblings[i]);
                if (siblings[i] === node) {
                    newsiblings.push(this);
                }
            }
            this.parent.setChildren(newsiblings);
        };
    Node.prototype.moveBefore = function(node) {
            this.unParent();
            this.parent = node.parent;
            var siblings = this.parent.getChildren();
            var newsiblings = [];
            for (var i in siblings) {
                if (siblings[i] === node) {
                    newsiblings.push(this);
                }
                newsiblings.push(siblings[i]);
            }
            this.parent.setChildren(newsiblings);
        };
    Node.prototype.getQueryString = function() {
            var children = this.children;
            var str = '';
            var parent_val;
            if (!this.domelement) {
                parent_val = 'menu0'
            } else {
                parent_val = 'menu'+this.domelement.find('input.thisMenu').val()
            }
            for (var i in children) {
                child_val = children[i].domelement.find('input.thisMenu').val()
                str += parent_val + '=' + child_val + '&'
                str += children[i].getQueryString()
            }
            return str
        }

    function Tree() {
        this.root = new Node(null, 0);
        this.finished = false;
    }
    Tree.prototype.insertIntoLastLevel = function(node, level) {
            var parent_node = this.root.findLastLevelNode(level);
            if (parent_node) {
                parent_node.addChild(node);
            }
        };
    Tree.prototype.paintTree = function() {
            this.root.paintNodes();
            recalculateRows();
        };
    Tree.prototype.findNodeByElement = function(element) {
            return this.root.findNodeByElement(element);
        };
    Tree.prototype.getQueryString = function() {
            return this.root.getQueryString();
        };


    function make_tree() {
    	var main_tree = new Tree();
        var rows = $("#changelist table tbody tr").length;
        if (!rows) {
            main_tree.finished=true;
        }
        $("#changelist table tbody tr").each(function(i) {
            var tr = $(this);
            setTimeout(function() {
                var td_level = tr.children("td").eq(0);
                var level = parseInt(td_level.text());
                var node = new Node(tr, level);
                main_tree.insertIntoLastLevel(node, level-1);
                if (i==rows-1) {
                    main_tree.finished=true;
                }
            }, 10 * i);
        });
        return main_tree;
    }
  
    function redo_row(node) {
        if (node.domelement)
            $("#changelist table tbody").append(node.domelement);
        var children = node.getChildren();
        for (var i in children) 
            redo_row(children[i]);
    }

    function redo_table(tree) {
        $("#changelist table tbody tr").remove();
        var node = tree.root;
        redo_row(node);
        tree.paintTree();
    }

    function save_tree(tree) {
        var data = tree.getQueryString();
        $('.ajax-loading').show();
        $.ajax({
            data:data,
            url: save_url,
            type: "GET",
            async: true,
            success: function(response){
                $('.ajax-loading').hide();
            }});
    }

    $(document).ready(function () {
        plus = $('.plusMenu');
        minus = $('.minusMenu');
        draggable = $('.draggable-icon');
        draggable_disabled = $('.draggable-icon-disabled');
        save_url = $('#collapsableSaveURL').html() || save_url;
        $("#changelist table thead tr").children("th").eq(0).hide();
        $("#changelist table thead tr").children("th").eq(1).hide();
        $("#changelist table tbody").hide();
        var tree = make_tree();

        var finish = function () {
            if (!tree.finished) {
                setTimeout(finish, 10);
            } else {
                tree.root.open();
                tree.paintTree();
                redo_table(tree);
                $('#changelist table tbody').sortable({
                    items: 'tr',
                    tolerance: 'pointer',
                    placeholder: 'row1',
                    forceHelperSize: true,
                    forcePlaceholderSize: true,
                    handle: '.draggable-icon',
                    start: function(e, ui) {
                        var current = tree.findNodeByElement(ui.item);
                        current.close();
                        ui.helper.find('.span50').remove();
                        $(this).find('.draggable-icon').hide();
                        $(this).find('.draggable-icon-disabled').show();
                        ui.helper.find('.draggable-icon').show();
                        ui.helper.find('.draggable-icon-disabled').hide();
                    },
                    stop: function(e, ui) {
                        var current = tree.findNodeByElement(ui.item);
                        var previous = tree.findNodeByElement(ui.item.prevAll('tr:visible').eq(0));
                        var next = tree.findNodeByElement(ui.item.nextAll('tr:visible').eq(0));
        
                        if (!previous) {
                            current.moveFirstChild(tree.root);
                        } else  {
                            if (!next) {
                                next_level = -1;
                            } else {
                                next_level = next.getLevel();
                            }
                            prev_level = previous.getLevel();
                            if (next_level > prev_level) {
                                current.moveBefore(next); 
                            } else if (next_level === prev_level) {
                                current.moveAfterWithLevel(previous, parseInt(ui.position.left/50)+1, false); 
                            } else {
                                current.moveAfterWithLevel(previous, parseInt(ui.position.left/50)+1, true); 
                            }
                        }
                        redo_table(tree);
                        save_tree(tree);
                    }
                });
                $("#changelist table tbody").show();
                $(".loading-list").hide();
            }
        };
        setTimeout(finish, 10);
    });

})(jQuery);

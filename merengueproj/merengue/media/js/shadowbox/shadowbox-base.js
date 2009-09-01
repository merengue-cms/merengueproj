/**
 * A base library for Shadowbox used as a standalone (without another base
 * library/adapter combination).
 *
 * This file is part of Shadowbox.
 *
 * Shadowbox is an online media viewing application that supports all of the
 * most popular web publishing formats. Shadowbox is written entirely in
 * JavaScript and CSS and is highly customizable.
 *
 * Shadowbox is released under version 3.0 of the Creative Commons Attribution-
 * Noncommercial-Share Alike license. This means that it is absolutely free
 * for personal, noncommercial use provided that you 1) make attribution to the
 * author and 2) release any derivative work under the same or a similar
 * license.
 *
 * If you wish to use Shadowbox for commercial purposes, licensing information
 * can be found at http://mjijackson.com/shadowbox/.
 *
 * @author      Michael J. I. Jackson <mjijackson@gmail.com>
 * @copyright   2007-2008 Michael J. I. Jackson
 * @license     http://creativecommons.org/licenses/by-nc-sa/3.0/
 * @version     SVN: $Id: shadowbox-base.js 91 2008-03-28 17:39:13Z mjijackson $
 */

// create the Shadowbox object first
var Shadowbox = {};

Shadowbox.lib = function(){

    // local style camelizing for speed
    var styleCache = {};
    var camelRe = /(-[a-z])/gi;
    var camelFn = function(m, a){
        return a.charAt(1).toUpperCase();
    };

    var view = document.defaultView;
    var alphaRe = /alpha\([^\)]*\)/gi;

    /**
     * Sets the opacity of the given element to the specified level.
     *
     * @param   {HTMLElement}   el          The element
     * @param   {Number}        opacity     The opacity to use
     * @return  void
     * @private
     * @static
     */
    var setOpacity = function(el, opacity){
        var s = el.style;
        if(window.ActiveXObject){ // IE
            s.zoom = 1;
            s.filter = (s.filter || '').replace(alphaRe, '') +
                       (opacity == 1 ? '' : ' alpha(opacity=' + opacity * 100 + ')');
        }else{
            s.opacity = opacity;
        }
    };

    return {

        /**
         * Gets the value of the style on the given element. This function
         * adapted from Ext.Element.getStyle().
         *
         * @param   {HTMLElement}   el      The DOM element
         * @param   {String}        style   The name of the style (e.g. margin-top)
         * @return  {mixed}                 The value of the given style
         * @public
         * @static
         */
        getStyle: function(){
            return view && view.getComputedStyle
                ? function(el, style){
                    var v, cs, camel;
                    if(style == 'float') style = 'cssFloat';
                    if(v = el.style[style]) return v;
                    if(cs = view.getComputedStyle(el, '')){
                        if(!(camel = styleCache[style])){
                            camel = styleCache[style] = style.replace(camelRe, camelFn);
                        }
                        return cs[camel];
                    }
                    return null;
                }
                : function(el, style){
                    var v, cs, camel;
                    if(style == 'opacity'){
                        if(typeof el.style.filter == 'string'){
                            var m = el.style.filter.match(/alpha\(opacity=(.*)\)/i);
                            if(m){
                                var fv = parseFloat(m[1]);
                                if(!isNaN(fv)) return fv ? fv / 100 : 0;
                            }
                        }
                        return 1;
                    }else if(style == 'float'){
                        style = 'styleFloat';
                    }
                    if(!(camel = styleCache[style])){
                        camel = styleCache[style] = style.replace(camelRe, camelFn);
                    }
                    if(v = el.style[camel]) return v;
                    if(cs = el.currentStyle) return cs[camel];
                    return null;
                };
        }(),

        /**
         * Sets the style on the given element to the given value. May be an
         * object to specify multiple values. This function adapted from
         * Ext.Element.setStyle().
         *
         * @param   {HTMLElement}   el      The DOM element
         * @param   {String/Object} style   The name of the style to set if a
         *                                  string, or an object of name =>
         *                                  value pairs
         * @param   {String}        value   The value to set the given style to
         * @return  void
         * @public
         * @static
         */
        setStyle: function(el, style, value){
            if(typeof style == 'string'){
                var camel;
                if(!(camel = styleCache[style])){
                    camel = styleCache[style] = style.replace(camelRe, camelFn);
                }
                if(camel == 'opacity'){
                    setOpacity(el, value);
                }else{
                    el.style[camel] = value;
                }
            }else{
                for(var s in style){
                    this.setStyle(el, s, style[s]);
                }
            }
        },

        /**
         * Gets a reference to the given element.
         *
         * @param   {String/HTMLElement}    el      The element to fetch
         * @return  {HTMLElement}                   A reference to the element
         * @public
         * @static
         */
        get: function(el){
            return typeof el == 'string' ? document.getElementById(el) : el;
        },

        /**
         * Removes an element from the DOM.
         *
         * @param   {HTMLElement}       el      The element to remove
         * @return  void
         * @public
         * @static
         */
        remove: function(el){
            el.parentNode.removeChild(el);
        },

        /**
         * Gets the target of the given event. The event object passed will be
         * the same object that is passed to listeners registered with
         * addEvent().
         *
         * @param   {mixed}             e       The event object
         * @return  {HTMLElement}               The event's target element
         * @public
         * @static
         */
        getTarget: function(e){
            var t = e.target ? e.target : e.srcElement;
            return t.nodeType == 3 ? t.parentNode : t;
        },

        /**
         * Prevents the event's default behavior. The event object here will
         * be the same object that is passed to listeners registered with
         * addEvent().
         *
         * @param   {mixed}             e       The event object
         * @return  void
         * @public
         * @static
         */
        preventDefault: function(e){
            if(e.preventDefault){
                e.preventDefault();
            }else{
                e.returnValue = false;
            }
        },

        /**
         * Gets the key code of the given event object (keydown). The event
         * object here will be the same object that is passed to listeners
         * registered with addEvent().
         *
         * @param   {mixed}         e       The event object
         * @return  {Number}                The key code of the event
         * @public
         * @static
         */
        keyCode: function(e){
            return e.which ? e.which : e.keyCode;
        },

        /**
         * Adds an event listener to the given element. It is expected that this
         * function will be passed the event as its first argument.
         *
         * @param   {HTMLElement}   el          The DOM element to listen to
         * @param   {String}        name        The name of the event to register
         *                                      (i.e. 'click', 'scroll', etc.)
         * @param   {Function}      handler     The event handler function
         * @return  void
         * @public
         * @static
         */
        addEvent: function(el, name, handler){
            if(el.addEventListener){
                el.addEventListener(name, handler, false);
            }else if(el.attachEvent){
                el.attachEvent('on' + name, handler);
            }else{
                el['on' + name] = handler;
            }
        },

        /**
         * Removes an event listener from the given element.
         *
         * @param   {HTMLElement}   el          The DOM element to stop listening to
         * @param   {String}        name        The name of the event to stop
         *                                      listening for (i.e. 'click')
         * @param   {Function}      handler     The event handler function
         * @return  void
         * @public
         * @static
         */
        removeEvent: function(el, name, handler){
            if(el.removeEventListener){
                el.removeEventListener(name, handler, false);
            }else if(el.detachEvent){
                el.detachEvent('on' + name, handler);
            }else{
                el['on' + name] = undefined;
            }
        },

        /**
         * Appends an HTML fragment to the given element.
         *
         * @param   {HTMLElement}       el      The element to append to
         * @param   {String}            html    The HTML fragment to use
         * @return  void
         * @public
         * @static
         */
        append: function(el, html){
            if(el.insertAdjacentHTML){
                el.insertAdjacentHTML('BeforeEnd', html);
            }else if(el.lastChild){
                var range = el.ownerDocument.createRange();
                range.setStartAfter(el.lastChild);
                var frag = range.createContextualFragment(html);
                el.appendChild(frag);
            }else{
                el.innerHTML = html;
            }
        }

    };

}();

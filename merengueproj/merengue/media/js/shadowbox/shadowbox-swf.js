/**
 * The Shadowbox SWF movie player class.
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
 * @version     SVN: $Id: shadowbox-swf.js 98 2008-04-04 20:29:36Z mjijackson $
 */

(function(){

    // shorthand
    var SB = Shadowbox;
    var SL = SB.lib;

    /**
     * Constructor. This class is used to display SWF movies.
     *
     * @param   {String}    id      The id to use for this content
     * @param   {Object}    obj     The content object
     * @public
     */
    Shadowbox.swf = function(id, obj){
        this.id = id;
        this.obj = obj;

        // SWF's are resizable
        this.resizable = true;

        // height defaults to 300 pixels
        this.height = this.obj.height ? parseInt(this.obj.height, 10) : 300;

        // width defaults to 300 pixels
        this.width = this.obj.width ? parseInt(this.obj.width, 10) : 300;
    };

    Shadowbox.swf.prototype = {

        /**
         * Returns an object containing the markup for this content, suitable
         * to pass to Shadowbox.lib.createHTML().
         *
         * @param   {Object}    dims    The current Shadowbox dimensions
         * @return  {Object}            The markup for this content item
         * @public
         */
        markup: function(dims){
            var bgcolor = SB.getOptions().flashBgColor;
            return {
                tag:        'object',
                id:         this.id,
                name:       this.id,
                type:       'application/x-shockwave-flash',
                data:       this.obj.content,
                children:   [
                    { tag: 'param', name: 'movie', value: this.obj.content },
                    { tag: 'param', name: 'bgcolor', value: bgcolor }
                ],
                height:     dims.resize_h, // use resized dimensions
                width:      dims.resize_w
            };
        },

        /**
         * Removes this SWF from the document.
         *
         * @return  void
         * @public
         */
        remove: function(){
            var el = SL.get(this.id);
            if(el) SL.remove(el);
        }

    };

})();

/**
 * The Shadowbox iframe player class.
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
 * @version     SVN: $Id: shadowbox-iframe.js 84 2008-03-24 03:05:09Z mjijackson $
 */

(function(){

    // shorthand
    var SB = Shadowbox;
    var SL = SB.lib;
    var C = SB.getClient();

    /**
     * Constructor. This class is used to display web pages in an HTML iframe.
     *
     * @param   {String}    id      The id to use for this content
     * @param   {Object}    obj     The content object
     * @public
     */
    Shadowbox.iframe = function(id, obj){
        this.id = id;
        this.obj = obj;

        // height defaults to full viewport height
        this.height = this.obj.height ? parseInt(this.obj.height, 10) : SL.getViewportHeight();

        // width defaults to full viewport width
        this.width = this.obj.width ? parseInt(this.obj.width, 10) : SL.getViewportWidth();
    };

    Shadowbox.iframe.prototype = {

        /**
         * Returns an object containing the markup for this content, suitable
         * to pass to Shadowbox.lib.createHTML().
         *
         * @param   {Object}    dims    The dimensions available as determined
         *                              by getDimensions()
         * @return  {Object}            The markup for this content item
         * @public
         */
        markup: function(dims){
            return {
                tag:            'iframe',
                id:             this.id,
                name:           this.id,
                height:         '100%',
                width:          '100%',
                frameborder:    '0',
                marginwidth:    '0',
                marginheight:   '0',
                scrolling:      'auto'
            };
        },

        /**
         * An optional callback function to process after this content has been
         * loaded.
         *
         * @param   {Object}    dims    The dimensions available as determined
         *                              by getDimensions()
         * @return  void
         * @public
         */
        onLoad: function(dims){
            var win = (C.isIE) ? SL.get(this.id).contentWindow : window.frames[this.id];
            win.location = this.obj.content; // set the iframe's location
        },

        /**
         * Removes this iframe from the document.
         *
         * @return  void
         * @public
         */
        remove: function(){
            var el = SL.get(this.id);
            if(el){
                SL.remove(el);
                if(C.isGecko) delete window.frames[this.id]; // needed for Firefox
            }
        }

    };

})();

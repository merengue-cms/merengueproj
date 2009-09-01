/**
 * The Shadowbox image player class.
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
 * @version     SVN: $Id: shadowbox-img.js 84 2008-03-24 03:05:09Z mjijackson $
 */

(function(){

    // shorthand
    var SB = Shadowbox;
    var SL = SB.lib;
    var C = SB.getClient();

    /**
     * Keeps track of 4 floating values (x, y, start_x, & start_y) that are used
     * in the drag calculations.
     *
     * @property    {Object}        drag
     * @private
     */
    var drag;

    /**
     * Holds the draggable element so we don't have to fetch it every time
     * the mouse moves.
     *
     * @property    {HTMLElement}   draggable
     * @private
     */
    var draggable;

    /**
     * The id to use for the drag layer.
     *
     * @property    {String}        drag_id
     * @private
     */
    var drag_id = 'shadowbox_drag_layer';

    /**
     * Resource used to preload images. It's class-level so that when a new
     * image is requested, the same resource can be reassigned, cancelling
     * the original's callback.
     *
     * @property    {HTMLElement}   preloader
     * @private
     */
    var preloader;

    /**
     * Resets the class drag variable.
     *
     * @return  void
     * @private
     */
    var resetDrag = function(){
        drag = {
            x:          0,
            y:          0,
            start_x:    null,
            start_y:    null
        };
    };

    /**
     * Toggles the drag function on and off.
     *
     * @param   {Boolean}   on      True to toggle on, false to toggle off
     * @param   {Number}    h       The height of the drag layer
     * @param   {Number}    w       The width of the drag layer
     * @return  void
     * @private
     */
    var toggleDrag = function(on, h, w){
        if(on){
            resetDrag();
            // add drag layer to prevent browser dragging of actual image
            var styles = [
                'position:absolute',
                'height:' + h + 'px',
                'width:' + w + 'px',
                'cursor:' + (C.isGecko ? '-moz-grab' : 'move')
            ];
            // make drag layer transparent
            styles.push('background-color:' + (C.isIE ? '#fff;filter:alpha(opacity=0)' : 'transparent'));
            SL.append(SL.get('shadowbox_body_inner'), '<div id="' + drag_id + '" style="' + styles.join(';') + '"></div>');
            SL.addEvent(SL.get(drag_id), 'mousedown', listenDrag);
        }else{
            var d = SL.get(drag_id);
            if(d){
                SL.removeEvent(d, 'mousedown', listenDrag);
                SL.remove(d);
            }
        }
    };

    /**
     * Sets up a drag listener on the document. Called when the mouse button is
     * pressed (mousedown).
     *
     * @param   {mixed}     ev      The mousedown event
     * @return  void
     * @private
     */
    var listenDrag = function(ev){
        drag.start_x = ev.clientX;
        drag.start_y = ev.clientY;
        draggable = SL.get('shadowbox_content');
        SL.addEvent(document, 'mousemove', positionDrag);
        SL.addEvent(document, 'mouseup', unlistenDrag);
        if(C.isGecko) SL.setStyle(SL.get(drag_id), 'cursor', '-moz-grabbing');
    };

    /**
     * Removes the drag listener. Called when the mouse button is released
     * (mouseup).
     *
     * @return  void
     * @private
     */
    var unlistenDrag = function(){
        SL.removeEvent(document, 'mousemove', positionDrag);
        SL.removeEvent(document, 'mouseup', unlistenDrag); // clean up
        if(C.isGecko) SL.setStyle(SL.get(drag_id), 'cursor', '-moz-grab');
    };

    /**
     * Positions an oversized image on drag.
     *
     * @param   {mixed}     ev      The drag event
     * @return  void
     * @private
     */
    var positionDrag = function(ev){
        var move_y = ev.clientY - drag.start_y;
        drag.start_y = drag.start_y + move_y;
        drag.y = Math.max(Math.min(0, drag.y + move_y), SB.currentHeight - SB.optimalHeight); // y boundaries
        SL.setStyle(draggable, 'top', drag.y + 'px');
        var move_x = ev.clientX - drag.start_x;
        drag.start_x = drag.start_x + move_x;
        drag.x = Math.max(Math.min(0, drag.x + move_x), SB.currentWidth - SB.optimalWidth); // x boundaries
        SL.setStyle(draggable, 'left', drag.x + 'px');
    };

    /**
     * Constructor. This class is used to display images.
     *
     * @param   {String}    id      The id to use for this content
     * @param   {Object}    obj     The content object
     * @public
     */
    Shadowbox.img = function(id, obj){
        this.id = id;
        this.obj = obj;

        // images are resizable
        this.resizable = true;

        // preload the image
        this.ready = false;
        var self = this; // needed inside preloader callback
        preloader = new Image();
        preloader.onload = function(){
            // height defaults to image height
            self.height = self.obj.height ? parseInt(self.obj.height, 10) : preloader.height;

            // width defaults to image width
            self.width = self.obj.width ? parseInt(self.obj.width, 10) : preloader.width;

            // ready to go
            self.ready = true;

            // clean up to prevent memory leak in IE
            preloader.onload = '';
            preloader = null;
        };
        preloader.src = obj.content;
    };

    Shadowbox.img.prototype = {

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
                tag:    'img',
                id:     this.id,
                height: dims.r_height, // use resized dimensions
                width:  dims.r_width,
                src:    this.obj.content,
                style:  'position:absolute'
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
            if(dims.enableDrag && SB.getOptions().handleLgImages == 'drag'){
                // listen for drag
                // in the case of oversized images, the "resized" height and
                // width will actually be the original image height and width
                toggleDrag(true, dims.r_height, dims.r_width);
            }
        },

        /**
         * Removes this image from the document.
         *
         * @return  void
         * @public
         */
        remove: function(){
            var el = SL.get(this.id);
            if(el) SL.remove(el);

            // disable drag layer
            toggleDrag(false);

            // prevent old image requests from loading
            if(preloader){
                preloader.onload = '';
                preloader = null;
            }
        }

    };

})();

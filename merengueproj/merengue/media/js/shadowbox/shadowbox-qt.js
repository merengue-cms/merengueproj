/**
 * The Shadowbox QuickTime player class.
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
 * @version     SVN: $Id: shadowbox-qt.js 84 2008-03-24 03:05:09Z mjijackson $
 */

(function(){

    // shorthand
    var SB = Shadowbox;
    var SL = SB.lib;
    var C = SB.getClient();

    /**
     * Constructor. This class is used to display QuickTime movies.
     *
     * @param   {String}    id      The id to use for this content
     * @param   {Object}    obj     The content object
     * @public
     */
    Shadowbox.qt = function(id, obj){
        this.id = id;
        this.obj = obj;

        // height defaults to 300 pixels
        this.height = this.obj.height ? parseInt(this.obj.height, 10) : 300;
        if(SB.getOptions().showMovieControls == true){
            this.height += 16; // height of QuickTime controller
        }

        // width defaults to 300 pixels
        this.width = this.obj.width ? parseInt(this.obj.width, 10) : 300;
    };

    Shadowbox.qt.prototype = {

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
            var options = SB.getOptions();
            var autoplay = String(options.autoplayMovies);
            var controls = String(options.showMovieControls);

            var markup = {
                tag:        'object',
                id:         this.id,
                name:       this.id,
                height:     this.height, // height includes controller
                width:      this.width,
                children:   [
                    { tag: 'param', name: 'src', value: this.obj.content },
                    { tag: 'param', name: 'scale', value: 'aspect' },
                    { tag: 'param', name: 'controller', value: controls },
                    { tag: 'param', name: 'autoplay', value: autoplay }
                ]
            };
            if(C.isIE){
                markup.classid = 'clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B';
                markup.codebase = 'http://www.apple.com/qtactivex/qtplugin.cab#version=6,0,2,0';
            }else{
                markup.type = 'video/quicktime';
                markup.data = this.obj.content;
            }

            return markup;
        },

        /**
         * Removes this movie from the document.
         *
         * @return  void
         * @public
         */
        remove: function(){
            try{
                document[this.id].Stop(); // stop QT video stream
            }catch(e){}
            var el = SL.get(this.id);
            if(el){
                el.innerHTML = ''; // stop QT audio stream for movies that have not yet loaded
                SL.remove(el);
            }
        }

    };

})();

/**
 * The Spanish language file for Shadowbox.
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
 * @version     SVN: $Id: shadowbox-es.js 86 2008-03-27 01:29:48Z mjijackson $
 */

if(typeof Shadowbox == 'undefined'){
    throw 'Unable to load Shadowbox language file, base library not found.';
}

/**
 * An object containing all textual messages to be used in Shadowbox. These are
 * provided so they may be translated into different languages. Alternative
 * translations may be found in js/lang/shadowbox-*.js where * is an abbreviation
 * of the language name (see
 * http://www.gnu.org/software/gettext/manual/gettext.html#Language-Codes).
 *
 * @var     {Object}    LANG
 * @public
 * @static
 */
 
Shadowbox.LANG = {

    code:       'es',

    of:         'de',

    loading:    'cargando',

    cancel:     'Cerrar',

    next:       'Siguiente',

    previous:   'Anterior',

    play:       'Iniciar',

    pause:      'Detener',

    close:      'Cerrar',

    errors:     {
        single: 'Para poder ver este contenido necesitas instalar el plugin <a href="{0}">{1}</a>.',
        shared: 'Para poder ver este contenido necesitas instalar estos dos plugins: <a href="{0}">{1}</a> y <a href="{2}">{3}</a>.',
        either: 'Para poder ver este contenido necesitas instalar alguno de estos plugins: <a href="{0}">{1}</a> o <a href="{2}">{3}</a>.'
    }

};



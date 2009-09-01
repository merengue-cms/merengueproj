//// MediaGallery

var MediaGallery = new Class({
    initialize: function(basecontent){
        this.imageGallery = null;
        this.imageController = null;
        this.imagesLogo = null;
        this.imagesCurrent = 0;

        this.videoGallery = null;
        this.videoController = null;
        this.videosLogo = null;
        this.videosCurrent = 0;

        this.Gallery = basecontent;

        this.currentGallery = 'imagesGallery';

        this.effectsOptions = { 
                duration: 300,
                transition: Fx.Transitions.Sine.easeInOut
        }

        this.videoGallery = this.Gallery.getElement('.screenShotVideos');
        this.imageGallery = this.Gallery.getElement('.screenShotImgs');
        if(this.videoGallery && this.imageGallery){
            this.Gallery.getElement('.toVideos').addEvent('click',this.changeToVideosGallery.bindWithEvent(this));
            this.Gallery.getElement('.toImages').addEvent('click',this.changeToImagesGallery.bindWithEvent(this));
        }
        if(this.imageGallery){
            this.imageController = this.Gallery.getElement('.imageController');
            this.loadImagesActions();
        }
        if(this.videoGallery){
            this.videoController = this.Gallery.getElement('.videoController');
            this.loadVideosActions();
        }
    },

    changeA2B: function(elementIn, elementOut){
            var efectoout = new Fx.Styles(elementOut, this.effectsOptions);
            var efectoin = new Fx.Styles(elementIn, this.effectsOptions);
            
            efectoout.start({
                            'opacity': [1,0]
            }).chain(function(){
                elementOut.setStyle('display','none');
 
                elementIn.setStyle('opacity',0);
                elementIn.setStyle('display','block');

                efectoin.start({
                    'opacity': [0,1]
                });
            });
    },

    changeToVideosGallery: function(){
        if(this.currentGallery != 'videosGallery'){
            this.changeA2B(this.videoGallery, this.imageGallery);
            this.changeA2B(this.videoController, this.imageController);
            this.Gallery.getElement('.toVideos').addClass('activeButton');
            this.Gallery.getElement('.toImages').removeClass('activeButton');
            this.currentGallery = 'videosGallery';
        }
    },

    changeToImagesGallery: function(){
        if(this.currentGallery != 'imagesGallery'){
            this.changeA2B(this.imageGallery, this.videoGallery);
            this.changeA2B(this.imageController, this.videoController);
            this.Gallery.getElement('.toImages').addClass('activeButton');
            this.Gallery.getElement('.toVideos').removeClass('activeButton');
            this.currentGallery = 'imagesGallery';
        }
    },


   nextImage: function(gallery, current){
        items = gallery.getElements('a');
        if (current < items.length-1){
            this.loadNewImage(gallery, items[current+1]);
            if (current < items.length-2){
                this.loadNewImage(gallery, items[current+2]);
            }
            this.changeA2B(items[current + 1], items[current]);
            current =  ++current;
        }
        return current;
    },


    loadNewImage: function(gallery, item){
        image = item.getElement('img');
        if (!image.getAttribute('src')){
            image_src = item.getAttribute('thumb');
            image.setAttribute('src', image_src);
        }
    },

    previousImage: function(gallery, current){
        items = gallery.getElements('a');
        if (current > 0){
            this.changeA2B(items[current - 1], items[current]); 
            current = --current;
        }
        return current
    },

    loadImagesActions: function(){
        this.imageController.getElement('.nextImg').addEvent('click',function(){
                            this.imagesCurrent = this.nextImage(this.imageGallery, this.imagesCurrent);
                            this.imageController.getElement('.imgNow').innerHTML = this.imagesCurrent + 1 ;
                        }.bindWithEvent(this));
        this.imageController.getElement('.prevImg').addEvent('click',function(){
                            this.imagesCurrent = this.previousImage(this.imageGallery, this.imagesCurrent);
                            this.imageController.getElement('.imgNow').innerHTML = this.imagesCurrent + 1 ;
                        }.bindWithEvent(this));
    },

    loadVideosActions: function(){
        this.videoController.getElement('.nextImg').addEvent('click',function(){
                            this.videosCurrent = this.nextImage(this.videoGallery, this.videosCurrent);
                            this.videoController.getElement('.imgNow').innerHTML = this.videosCurrent + 1 ;
                        }.bindWithEvent(this));
        this.videoController.getElement('.prevImg').addEvent('click',function(){
                            this.videosCurrent = this.previousImage(this.videoGallery, this.videosCurrent);
                            this.videoController.getElement('.imgNow').innerHTML = this.videosCurrent + 1 ;
                        }.bindWithEvent(this));
    }


});
/* registerPloneFunction(loadGallery); */


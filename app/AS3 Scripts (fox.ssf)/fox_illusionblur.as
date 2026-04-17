// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_illusionblur

package 
{
    import flash.display.MovieClip;

    public dynamic class fox_illusionblur extends MovieClip 
    {

        public function fox_illusionblur()
        {
            addFrameScript(2, this.frame3);
        }

        internal function frame3():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}//package 


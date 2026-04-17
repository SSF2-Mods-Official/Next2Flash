// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_shineEffect

package 
{
    import flash.display.MovieClip;

    public dynamic class fox_shineEffect extends MovieClip 
    {

        public function fox_shineEffect()
        {
            addFrameScript(13, this.frame14);
        }

        internal function frame14():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}//package 


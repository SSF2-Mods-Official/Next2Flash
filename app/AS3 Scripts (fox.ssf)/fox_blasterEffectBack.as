// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_blasterEffectBack

package 
{
    import flash.display.MovieClip;

    public dynamic class fox_blasterEffectBack extends MovieClip 
    {

        public function fox_blasterEffectBack()
        {
            addFrameScript(7, this.frame8);
        }

        internal function frame8():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}//package 


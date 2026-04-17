// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_blasterEffectDown

package 
{
    import flash.display.MovieClip;

    public dynamic class fox_blasterEffectDown extends MovieClip 
    {

        public function fox_blasterEffectDown()
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


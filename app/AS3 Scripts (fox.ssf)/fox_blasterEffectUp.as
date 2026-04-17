// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_blasterEffectUp

package 
{
    import flash.display.MovieClip;

    public dynamic class fox_blasterEffectUp extends MovieClip 
    {

        public function fox_blasterEffectUp()
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


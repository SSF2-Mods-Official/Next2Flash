// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_shineFinish

package 
{
    import flash.display.MovieClip;

    public dynamic class fox_shineFinish extends MovieClip 
    {

        public function fox_shineFinish()
        {
            addFrameScript(6, this.frame7);
        }

        internal function frame7():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}//package 


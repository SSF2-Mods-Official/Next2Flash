// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_shineLoop

package 
{
    import flash.display.MovieClip;

    public dynamic class fox_shineLoop extends MovieClip 
    {

        public function fox_shineLoop()
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


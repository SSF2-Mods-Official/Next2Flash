// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_shineStart

package 
{
    import flash.display.MovieClip;

    public dynamic class fox_shineStart extends MovieClip 
    {

        public function fox_shineStart()
        {
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}//package 


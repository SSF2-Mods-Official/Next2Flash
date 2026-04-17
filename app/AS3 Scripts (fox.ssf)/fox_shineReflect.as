// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_shineReflect

package 
{
    import flash.display.MovieClip;

    public dynamic class fox_shineReflect extends MovieClip 
    {

        public function fox_shineReflect()
        {
            addFrameScript(5, this.frame6);
        }

        internal function frame6():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}//package 


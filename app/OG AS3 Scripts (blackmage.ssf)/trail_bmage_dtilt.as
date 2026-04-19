// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//trail_bmage_dtilt

package 
{
    import flash.display.MovieClip;

    public dynamic class trail_bmage_dtilt extends MovieClip 
    {

        public function trail_bmage_dtilt()
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

